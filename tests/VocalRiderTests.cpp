#include "../src/dsp/VocalRiderCore.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace
{
int failures = 0;

void expect (bool condition, const std::string& message)
{
    if (! condition)
    {
        ++failures;
        std::cerr << "[FAIL] " << message << std::endl;
    }
}

float dbToGain (float db)
{
    return std::pow (10.0f, db / 20.0f);
}

struct SegmentResult
{
    float minGainDb { std::numeric_limits<float>::infinity() };
    float maxGainDb { -std::numeric_limits<float>::infinity() };
    float meanTailGainDb { 0.0f };
    float finalGainDb { 0.0f };
    bool finite { true };
};

SegmentResult runTone (cipi::dsp::VocalRiderCore& rider,
                       double sampleRate,
                       double seconds,
                       float levelDb,
                       float amount,
                       double frequency = 190.0)
{
    const auto total = static_cast<int> (std::lround (seconds * sampleRate));
    const auto tailStart = static_cast<int> (0.75 * static_cast<double> (total));
    const auto amplitude = dbToGain (levelDb);

    SegmentResult result;
    double tailSum = 0.0;
    int tailCount = 0;

    for (int n = 0; n < total; ++n)
    {
        const auto phase = 2.0 * 3.14159265358979323846
                         * frequency * static_cast<double> (n) / sampleRate;
        const auto sample = amplitude * static_cast<float> (std::sin (phase));
        const auto gainDb = rider.processSample (std::abs (sample), amount);

        result.finite = result.finite && std::isfinite (gainDb);
        result.minGainDb = std::min (result.minGainDb, gainDb);
        result.maxGainDb = std::max (result.maxGainDb, gainDb);

        if (n >= tailStart)
        {
            tailSum += gainDb;
            ++tailCount;
        }

        result.finalGainDb = gainDb;
    }

    if (tailCount > 0)
        result.meanTailGainDb = static_cast<float> (tailSum / tailCount);

    return result;
}

SegmentResult runSilence (cipi::dsp::VocalRiderCore& rider,
                          double sampleRate,
                          double seconds,
                          float amount)
{
    const auto total = static_cast<int> (std::lround (seconds * sampleRate));
    SegmentResult result;
    double tailSum = 0.0;
    int tailCount = 0;
    const auto tailStart = static_cast<int> (0.75 * static_cast<double> (total));

    for (int n = 0; n < total; ++n)
    {
        const auto gainDb = rider.processSample (0.0f, amount);
        result.finite = result.finite && std::isfinite (gainDb);
        result.minGainDb = std::min (result.minGainDb, gainDb);
        result.maxGainDb = std::max (result.maxGainDb, gainDb);

        if (n >= tailStart)
        {
            tailSum += gainDb;
            ++tailCount;
        }

        result.finalGainDb = gainDb;
    }

    if (tailCount > 0)
        result.meanTailGainDb = static_cast<float> (tailSum / tailCount);

    return result;
}

void testAmountZeroUnityControl()
{
    cipi::dsp::VocalRiderCore rider;
    rider.prepare (48000.0);

    for (int n = 0; n < 48000 * 3; ++n)
    {
        const auto level = (n % 2000) < 1000 ? 0.8f : 0.02f;
        const auto gainDb = rider.processSample (level, 0.0f);

        expect (std::isfinite (gainDb), "Amount 0 produced non-finite gain.");
        expect (std::abs (gainDb) < 1.0e-6f, "Amount 0 must keep ride gain at 0 dB.");
    }
}

struct ScenarioMetrics
{
    float referenceGain { 0.0f };
    float quietGain { 0.0f };
    float loudGain { 0.0f };
    float silenceEndGain { 0.0f };
    float minGain { 0.0f };
    float maxGain { 0.0f };
    bool finite { true };
};

ScenarioMetrics runScenario (double sampleRate, float amount)
{
    cipi::dsp::VocalRiderCore rider;
    rider.prepare (sampleRate);

    auto silenceA = runSilence (rider, sampleRate, 0.5, amount);
    auto reference = runTone (rider, sampleRate, 5.0, -20.0f, amount);
    auto gapA = runSilence (rider, sampleRate, 0.5, amount);
    auto quiet = runTone (rider, sampleRate, 2.0, -28.0f, amount);
    auto gapB = runSilence (rider, sampleRate, 0.5, amount);
    auto loud = runTone (rider, sampleRate, 2.0, -12.0f, amount);
    auto silenceB = runSilence (rider, sampleRate, 3.0, amount);

    ScenarioMetrics result;
    result.referenceGain = reference.meanTailGainDb;
    result.quietGain = quiet.meanTailGainDb;
    result.loudGain = loud.meanTailGainDb;
    result.silenceEndGain = silenceB.finalGainDb;

    result.minGain = std::min ({ reference.minGainDb, quiet.minGainDb, loud.minGainDb,
                                 gapA.minGainDb, gapB.minGainDb, silenceB.minGainDb });
    result.maxGain = std::max ({ reference.maxGainDb, quiet.maxGainDb, loud.maxGainDb,
                                 gapA.maxGainDb, gapB.maxGainDb, silenceB.maxGainDb });

    result.finite = silenceA.finite && reference.finite && gapA.finite
                 && quiet.finite && gapB.finite && loud.finite && silenceB.finite;
    return result;
}

void testNominalRiding()
{
    const auto metrics = runScenario (48000.0, 0.5f);

    expect (metrics.finite, "Nominal scenario produced non-finite gain.");
    expect (std::abs (metrics.referenceGain) < 1.0f,
            "Reference phrase should establish Auto Target without a large ride.");
    expect (metrics.quietGain > 0.5f,
            "A sustained quiet phrase should receive positive ride gain.");
    expect (metrics.loudGain < -0.5f,
            "A sustained loud phrase should receive negative ride gain.");
    expect (metrics.minGain >= -4.25f && metrics.maxGain <= 4.25f,
            "Amount 50 ride exceeded the provisional ±4 dB-class range.");
    expect (std::abs (metrics.silenceEndGain) < 0.25f,
            "Ride gain should return close to 0 dB after sustained inactivity.");
}

void testExtremeAmountBound()
{
    const auto metrics = runScenario (48000.0, 1.0f);

    expect (metrics.finite, "Amount 100 scenario produced non-finite gain.");
    expect (metrics.minGain >= -5.25f && metrics.maxGain <= 5.25f,
            "Amount 100 exceeded the provisional ±5 dB-class range.");
}

void testSampleRateConsistency()
{
    const auto a = runScenario (44100.0, 0.5f);
    const auto b = runScenario (96000.0, 0.5f);

    expect (a.finite && b.finite, "Sample-rate scenarios must remain finite.");
    expect (std::abs (a.quietGain - b.quietGain) < 0.20f,
            "Quiet-phrase ride changed too much between 44.1 and 96 kHz.");
    expect (std::abs (a.loudGain - b.loudGain) < 0.20f,
            "Loud-phrase ride changed too much between 44.1 and 96 kHz.");
}

void testShortBurstDoesNotCauseGainJump()
{
    constexpr double sampleRate = 48000.0;
    cipi::dsp::VocalRiderCore rider;
    rider.prepare (sampleRate);

    runTone (rider, sampleRate, 4.0, -20.0f, 0.5f);

    const auto before = rider.getCurrentGainDb();

    const auto burstSamples = static_cast<int> (0.020 * sampleRate);
    float maxDelta = 0.0f;

    for (int n = 0; n < burstSamples; ++n)
    {
        const auto impulseLike = (n % 48 == 0) ? 1.0f : 0.0f;
        const auto gainDb = rider.processSample (impulseLike, 0.5f);
        maxDelta = std::max (maxDelta, std::abs (gainDb - before));
    }

    expect (std::isfinite (maxDelta), "Burst test produced non-finite gain movement.");
    expect (maxDelta < 0.25f,
            "20 ms impulse-like burst caused too much immediate macro ride movement.");
}

void testInvalidInputSafety()
{
    cipi::dsp::VocalRiderCore rider;
    rider.prepare (48000.0);

    const auto nan = std::numeric_limits<float>::quiet_NaN();
    const auto inf = std::numeric_limits<float>::infinity();

    for (int i = 0; i < 1000; ++i)
    {
        const auto a = rider.processSample (nan, 0.5f);
        const auto b = rider.processSample (inf, 0.5f);
        expect (std::isfinite (a) && std::isfinite (b),
                "NaN/Inf input must not create non-finite ride gain.");
    }
}
} // namespace

int main()
{
    testAmountZeroUnityControl();
    testNominalRiding();
    testExtremeAmountBound();
    testSampleRateConsistency();
    testShortBurstDoesNotCauseGainJump();
    testInvalidInputSafety();

    if (failures == 0)
    {
        std::cout << "[PASS] Vocal Rider deterministic prototype gate passed." << std::endl;
        return 0;
    }

    std::cerr << "[FAIL] Vocal Rider deterministic prototype gate: "
              << failures << " failure(s)." << std::endl;
    return 1;
}

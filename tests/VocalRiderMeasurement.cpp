#include "../src/dsp/VocalRiderCore.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

namespace
{
float dbToGain (float db)
{
    return std::pow (10.0f, db / 20.0f);
}

struct SegmentStats
{
    float meanTailGainDb { 0.0f };
    float finalGainDb { 0.0f };
    float minGainDb { std::numeric_limits<float>::infinity() };
    float maxGainDb { -std::numeric_limits<float>::infinity() };
    float maxAbsSpeedDbPerSec { 0.0f };
    bool finite { true };
};

SegmentStats runSegment (cipi::dsp::VocalRiderCore& rider,
                         double sampleRate,
                         double seconds,
                         float levelDb,
                         float amount,
                         bool tone)
{
    const auto total = std::max (1, static_cast<int> (std::lround (seconds * sampleRate)));
    const auto tailStart = static_cast<int> (0.75 * static_cast<double> (total));
    const auto amplitude = tone ? dbToGain (levelDb) : 0.0f;
    constexpr double frequency = 190.0;

    SegmentStats stats;
    double tailSum = 0.0;
    int tailCount = 0;
    float previousGain = rider.getCurrentGainDb();

    for (int n = 0; n < total; ++n)
    {
        const auto phase = 2.0 * 3.14159265358979323846
                         * frequency * static_cast<double> (n) / sampleRate;
        const auto sample = tone ? amplitude * static_cast<float> (std::sin (phase)) : 0.0f;
        const auto gainDb = rider.processSample (std::abs (sample), amount);

        stats.finite = stats.finite && std::isfinite (gainDb);
        stats.minGainDb = std::min (stats.minGainDb, gainDb);
        stats.maxGainDb = std::max (stats.maxGainDb, gainDb);
        stats.maxAbsSpeedDbPerSec = std::max (
            stats.maxAbsSpeedDbPerSec,
            static_cast<float> (std::abs (gainDb - previousGain) * sampleRate));
        previousGain = gainDb;

        if (n >= tailStart)
        {
            tailSum += gainDb;
            ++tailCount;
        }

        stats.finalGainDb = gainDb;
    }

    if (tailCount > 0)
        stats.meanTailGainDb = static_cast<float> (tailSum / tailCount);

    return stats;
}

struct Scenario
{
    double sampleRate { 0.0 };
    float amount { 0.0f };
    float referenceGain { 0.0f };
    float quietGain { 0.0f };
    float loudGain { 0.0f };
    float silenceReturn { 0.0f };
    float minGain { 0.0f };
    float maxGain { 0.0f };
    float maxSpeed { 0.0f };
    float burstDelta { 0.0f };
    bool finite { true };
    double realtimeFactor { 0.0 };
};

Scenario measureScenario (double sampleRate, float amount)
{
    cipi::dsp::VocalRiderCore rider;
    rider.prepare (sampleRate);

    const auto start = std::chrono::steady_clock::now();

    const auto pre = runSegment (rider, sampleRate, 0.5, -120.0f, amount, false);
    const auto reference = runSegment (rider, sampleRate, 5.0, -20.0f, amount, true);
    const auto gapA = runSegment (rider, sampleRate, 0.5, -120.0f, amount, false);
    const auto quiet = runSegment (rider, sampleRate, 2.0, -28.0f, amount, true);
    const auto gapB = runSegment (rider, sampleRate, 0.5, -120.0f, amount, false);
    const auto loud = runSegment (rider, sampleRate, 2.0, -12.0f, amount, true);

    const auto beforeBurst = rider.getCurrentGainDb();
    float burstDelta = 0.0f;
    const auto burstSamples = static_cast<int> (std::lround (0.020 * sampleRate));

    for (int n = 0; n < burstSamples; ++n)
    {
        const auto sample = (n % std::max (1, static_cast<int> (sampleRate / 1000.0))) == 0 ? 1.0f : 0.0f;
        const auto gainDb = rider.processSample (sample, amount);
        burstDelta = std::max (burstDelta, std::abs (gainDb - beforeBurst));
    }

    const auto post = runSegment (rider, sampleRate, 3.0, -120.0f, amount, false);

    const auto end = std::chrono::steady_clock::now();
    const auto elapsed = std::chrono::duration<double> (end - start).count();
    constexpr double programSeconds = 13.52;

    Scenario result;
    result.sampleRate = sampleRate;
    result.amount = amount;
    result.referenceGain = reference.meanTailGainDb;
    result.quietGain = quiet.meanTailGainDb;
    result.loudGain = loud.meanTailGainDb;
    result.silenceReturn = post.finalGainDb;
    result.minGain = std::min ({ pre.minGainDb, reference.minGainDb, gapA.minGainDb,
                                 quiet.minGainDb, gapB.minGainDb, loud.minGainDb, post.minGainDb });
    result.maxGain = std::max ({ pre.maxGainDb, reference.maxGainDb, gapA.maxGainDb,
                                 quiet.maxGainDb, gapB.maxGainDb, loud.maxGainDb, post.maxGainDb });
    result.maxSpeed = std::max ({ pre.maxAbsSpeedDbPerSec, reference.maxAbsSpeedDbPerSec,
                                  gapA.maxAbsSpeedDbPerSec, quiet.maxAbsSpeedDbPerSec,
                                  gapB.maxAbsSpeedDbPerSec, loud.maxAbsSpeedDbPerSec,
                                  post.maxAbsSpeedDbPerSec });
    result.burstDelta = burstDelta;
    result.finite = pre.finite && reference.finite && gapA.finite
                 && quiet.finite && gapB.finite && loud.finite && post.finite;
    result.realtimeFactor = elapsed > 0.0 ? programSeconds / elapsed : 0.0;
    return result;
}

float medianValue (std::vector<float> values)
{
    if (values.empty())
        return 0.0f;

    std::sort (values.begin(), values.end());
    const auto middle = values.size() / 2;

    if ((values.size() & 1U) != 0U)
        return values[middle];

    return 0.5f * (values[middle - 1] + values[middle]);
}

float standardDeviation (const std::vector<float>& values)
{
    if (values.empty())
        return 0.0f;

    double mean = 0.0;
    for (const auto value : values)
        mean += value;
    mean /= static_cast<double> (values.size());

    double variance = 0.0;
    for (const auto value : values)
    {
        const auto delta = static_cast<double> (value) - mean;
        variance += delta * delta;
    }

    variance /= static_cast<double> (values.size());
    return static_cast<float> (std::sqrt (variance));
}

struct SectionDynamicsResult
{
    float inputSectionContrastDb { 6.0f };
    float outputSectionContrastDb { 0.0f };
    float sectionContrastPreservedRatio { 0.0f };
    float inputWithinSectionPhraseStdDb { 0.0f };
    float outputWithinSectionPhraseStdDb { 0.0f };
    float withinSectionLevelingReduction { 0.0f };
    bool finite { true };
};

SectionDynamicsResult measureSectionDynamics (double sampleRate, float amount)
{
    cipi::dsp::VocalRiderCore rider;
    rider.prepare (sampleRate);

    const std::array<float, 4> sectionBaseDb { -24.0f, -18.0f, -24.0f, -18.0f };
    const std::array<float, 3> phraseOffsetDb { -2.0f, 0.0f, 2.0f };

    std::array<std::vector<float>, 4> outputPhraseLevels;
    std::array<float, 4> outputSectionMedians {};
    std::vector<float> verseMedians;
    std::vector<float> chorusMedians;

    for (std::size_t section = 0; section < sectionBaseDb.size(); ++section)
    {
        for (const auto offsetDb : phraseOffsetDb)
        {
            const auto inputLevelDb = sectionBaseDb[section] + offsetDb;
            const auto phrase = runSegment (rider, sampleRate, 2.8, inputLevelDb, amount, true);

            if (! phrase.finite || ! std::isfinite (phrase.meanTailGainDb))
            {
                SectionDynamicsResult bad;
                bad.finite = false;
                return bad;
            }

            outputPhraseLevels[section].push_back (inputLevelDb + phrase.meanTailGainDb);
            runSegment (rider, sampleRate, 0.7, -120.0f, amount, false);
        }

        outputSectionMedians[section] = medianValue (outputPhraseLevels[section]);

        if ((section & 1U) == 0U)
            verseMedians.push_back (outputSectionMedians[section]);
        else
            chorusMedians.push_back (outputSectionMedians[section]);
    }

    SectionDynamicsResult result;
    result.outputSectionContrastDb = medianValue (chorusMedians) - medianValue (verseMedians);
    result.sectionContrastPreservedRatio = result.outputSectionContrastDb / result.inputSectionContrastDb;

    const std::vector<float> inputOffsets { -2.0f, 0.0f, 2.0f };
    result.inputWithinSectionPhraseStdDb = standardDeviation (inputOffsets);

    float outputStdSum = 0.0f;
    for (const auto& section : outputPhraseLevels)
        outputStdSum += standardDeviation (section);

    result.outputWithinSectionPhraseStdDb = outputStdSum / static_cast<float> (outputPhraseLevels.size());

    if (result.inputWithinSectionPhraseStdDb > 1.0e-6f)
        result.withinSectionLevelingReduction =
            1.0f - result.outputWithinSectionPhraseStdDb / result.inputWithinSectionPhraseStdDb;

    result.finite = std::isfinite (result.outputSectionContrastDb)
                 && std::isfinite (result.sectionContrastPreservedRatio)
                 && std::isfinite (result.outputWithinSectionPhraseStdDb)
                 && std::isfinite (result.withinSectionLevelingReduction);
    return result;
}
} // namespace

int main (int argc, char** argv)
{
    const std::filesystem::path outputDir = argc > 1 ? argv[1] : "vocal-rider-measurements";
    std::filesystem::create_directories (outputDir);

    const std::vector<double> sampleRates { 44100.0, 48000.0, 88200.0, 96000.0, 192000.0 };
    const std::vector<float> amounts { 0.0f, 0.25f, 0.50f, 0.75f, 1.0f };

    std::vector<Scenario> rows;
    rows.reserve (sampleRates.size() * amounts.size());

    for (const auto sampleRate : sampleRates)
        for (const auto amount : amounts)
            rows.push_back (measureScenario (sampleRate, amount));

    std::ofstream csv (outputDir / "vocal_rider_core_matrix.csv");
    csv << "sample_rate,amount,reference_gain_db,quiet_gain_db,loud_gain_db,"
           "silence_return_db,min_gain_db,max_gain_db,max_speed_db_per_s,"
           "burst_delta_db,finite,realtime_factor\n";
    csv << std::fixed << std::setprecision (6);

    for (const auto& r : rows)
    {
        csv << r.sampleRate << ','
            << r.amount << ','
            << r.referenceGain << ','
            << r.quietGain << ','
            << r.loudGain << ','
            << r.silenceReturn << ','
            << r.minGain << ','
            << r.maxGain << ','
            << r.maxSpeed << ','
            << r.burstDelta << ','
            << (r.finite ? 1 : 0) << ','
            << r.realtimeFactor << '\n';
    }

    const auto nominalIt = std::find_if (rows.begin(), rows.end(), [] (const Scenario& r)
    {
        return r.sampleRate == 48000.0 && std::abs (r.amount - 0.50f) < 1.0e-6f;
    });

    if (nominalIt == rows.end())
        return 2;

    float quietSpread = 0.0f;
    float loudSpread = 0.0f;
    float nominalQuietMin = std::numeric_limits<float>::infinity();
    float nominalQuietMax = -std::numeric_limits<float>::infinity();
    float nominalLoudMin = std::numeric_limits<float>::infinity();
    float nominalLoudMax = -std::numeric_limits<float>::infinity();
    bool allFinite = true;

    for (const auto& r : rows)
    {
        allFinite = allFinite && r.finite;

        if (std::abs (r.amount - 0.50f) < 1.0e-6f)
        {
            nominalQuietMin = std::min (nominalQuietMin, r.quietGain);
            nominalQuietMax = std::max (nominalQuietMax, r.quietGain);
            nominalLoudMin = std::min (nominalLoudMin, r.loudGain);
            nominalLoudMax = std::max (nominalLoudMax, r.loudGain);
        }
    }

    quietSpread = nominalQuietMax - nominalQuietMin;
    loudSpread = nominalLoudMax - nominalLoudMin;

    const auto sectionDynamics = measureSectionDynamics (48000.0, 0.50f);
    allFinite = allFinite && sectionDynamics.finite;

    std::ofstream summary (outputDir / "summary.md");
    summary << "# Vocal Rider core deterministic measurement\n\n";
    summary << "Measurement maturity: **DSP_MEASURED** for the standalone core only.\n\n";
    summary << "## Nominal 48 kHz / Amount 50%\n\n";
    summary << std::fixed << std::setprecision (3);
    summary << "- reference phrase tail ride: " << nominalIt->referenceGain << " dB\n";
    summary << "- quiet phrase tail ride: " << nominalIt->quietGain << " dB\n";
    summary << "- loud phrase tail ride: " << nominalIt->loudGain << " dB\n";
    summary << "- final gain after 3 s silence: " << nominalIt->silenceReturn << " dB\n";
    summary << "- min / max ride: " << nominalIt->minGain << " / " << nominalIt->maxGain << " dB\n";
    summary << "- maximum observed gain speed: " << nominalIt->maxSpeed << " dB/s\n";
    summary << "- 20 ms impulse-like burst immediate delta: " << nominalIt->burstDelta << " dB\n";
    summary << "- benchmark realtime factor: " << nominalIt->realtimeFactor << "x (runner-dependent; informational only)\n\n";
    summary << "## Sample-rate consistency at Amount 50%\n\n";
    summary << "- quiet-phrase tail ride spread, 44.1-192 kHz: " << quietSpread << " dB\n";
    summary << "- loud-phrase tail ride spread, 44.1-192 kHz: " << loudSpread << " dB\n";
    summary << "- all matrix values finite: " << (allFinite ? "yes" : "no") << "\n\n";
    summary << "## Intentional section-dynamics probe (48 kHz / Amount 50%)\n\n";
    summary << "- input verse-to-chorus contrast: " << sectionDynamics.inputSectionContrastDb << " dB\n";
    summary << "- output verse-to-chorus contrast: " << sectionDynamics.outputSectionContrastDb << " dB\n";
    summary << "- section contrast preserved: " << (100.0f * sectionDynamics.sectionContrastPreservedRatio) << "%\n";
    summary << "- input within-section phrase std: " << sectionDynamics.inputWithinSectionPhraseStdDb << " dB\n";
    summary << "- output within-section phrase std: " << sectionDynamics.outputWithinSectionPhraseStdDb << " dB\n";
    const bool sectionDynamicsPass =
        sectionDynamics.sectionContrastPreservedRatio >= 0.70f
        && sectionDynamics.withinSectionLevelingReduction >= 0.20f;

    summary << "- within-section leveling reduction: " << (100.0f * sectionDynamics.withinSectionLevelingReduction) << "%\n";
    summary << "- section-dynamics gate: " << (sectionDynamicsPass ? "PASS" : "FAIL") << "\n\n";
    summary << "Gate thresholds are provisional research criteria: preserve >=70% of a sustained 6 dB section contrast while reducing within-section phrase spread by >=20%.\n\n";
    summary << "The CSV contains the full 5 sample-rate x 5 Amount matrix.\n";

    std::ofstream json (outputDir / "metrics.json");
    json << "{\n"
         << "  \"measurement_maturity\": \"DSP_MEASURED_CORE\",\n"
         << "  \"nominal_sample_rate\": 48000,\n"
         << "  \"nominal_amount\": 0.5,\n"
         << "  \"reference_gain_db\": " << nominalIt->referenceGain << ",\n"
         << "  \"quiet_gain_db\": " << nominalIt->quietGain << ",\n"
         << "  \"loud_gain_db\": " << nominalIt->loudGain << ",\n"
         << "  \"silence_return_db\": " << nominalIt->silenceReturn << ",\n"
         << "  \"min_gain_db\": " << nominalIt->minGain << ",\n"
         << "  \"max_gain_db\": " << nominalIt->maxGain << ",\n"
         << "  \"max_speed_db_per_s\": " << nominalIt->maxSpeed << ",\n"
         << "  \"burst_delta_db\": " << nominalIt->burstDelta << ",\n"
         << "  \"amount50_quiet_sample_rate_spread_db\": " << quietSpread << ",\n"
         << "  \"amount50_loud_sample_rate_spread_db\": " << loudSpread << ",\n"
         << "  \"section_input_contrast_db\": " << sectionDynamics.inputSectionContrastDb << ",\n"
         << "  \"section_output_contrast_db\": " << sectionDynamics.outputSectionContrastDb << ",\n"
         << "  \"section_contrast_preserved_ratio\": " << sectionDynamics.sectionContrastPreservedRatio << ",\n"
         << "  \"section_input_phrase_std_db\": " << sectionDynamics.inputWithinSectionPhraseStdDb << ",\n"
         << "  \"section_output_phrase_std_db\": " << sectionDynamics.outputWithinSectionPhraseStdDb << ",\n"
         << "  \"section_within_leveling_reduction\": " << sectionDynamics.withinSectionLevelingReduction << ",\n"
         << "  \"section_dynamics_pass\": " << (sectionDynamicsPass ? "true" : "false") << ",\n"
         << "  \"all_finite\": " << (allFinite ? "true" : "false") << "\n"
         << "}\n";

    if (! allFinite)
        return 3;

    if (! sectionDynamicsPass)
        return 4;

    return 0;
}

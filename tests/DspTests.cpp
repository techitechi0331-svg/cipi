#include <JuceHeader.h>
#include "../src/dsp/EnvelopeFollower.h"
#include "../src/dsp/CrestFactorDetector.h"
#include "../src/dsp/SoftKneeCompressor.h"

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

void testGainComputer()
{
    using cipi::dsp::gainComputerDb;

    expect (std::abs (gainComputerDb (-6.0f, -18.0f, 1.0f, 6.0f)) < 1.0e-6f,
            "Ratio 1:1 must produce unity gain.");

    float previousOutput = -200.0f;

    for (int i = 0; i <= 960; ++i)
    {
        const auto inputDb = -72.0f + 0.1f * static_cast<float> (i);
        const auto gainDb = gainComputerDb (inputDb, -18.0f, 4.0f, 6.0f);
        const auto outputDb = inputDb + gainDb;

        expect (std::isfinite (gainDb), "Gain computer produced non-finite output.");
        expect (gainDb <= 1.0e-4f, "Downward compressor must not create positive gain.");
        expect (outputDb + 1.0e-4f >= previousOutput,
                "Static transfer curve must remain monotonic.");

        previousOutput = outputDb;
    }

    const auto justBelow = gainComputerDb (-21.001f, -18.0f, 4.0f, 6.0f);
    const auto justInside = gainComputerDb (-20.999f, -18.0f, 4.0f, 6.0f);

    expect (std::abs (justInside - justBelow) < 0.01f,
            "Soft-knee lower boundary must be continuous.");
}

void testEnvelopeFollower()
{
    cipi::dsp::EnvelopeFollower envelope;
    envelope.prepare (48000.0);
    envelope.setAttackRelease (10.0f, 100.0f);

    float y = 0.0f;

    for (int i = 0; i < 4800; ++i)
        y = envelope.process (1.0f);

    expect (std::isfinite (y), "Envelope attack produced non-finite state.");
    expect (y > 0.99f && y <= 1.0001f,
            "10 ms one-pole envelope should essentially settle after 100 ms.");

    for (int i = 0; i < 4800; ++i)
        y = envelope.process (0.0f);

    expect (std::isfinite (y), "Envelope release produced non-finite state.");
    expect (y > 0.35f && y < 0.39f,
            "100 ms release should decay to approximately e^-1 after 100 ms.");
}

void testLinkwitzRileyReconstruction()
{
    constexpr double sampleRate = 48000.0;
    constexpr float cutoff = 5600.0f;

    for (const auto frequency : { 200.0, 1000.0, 5600.0, 10000.0, 18000.0 })
    {
        juce::dsp::LinkwitzRileyFilter<float> crossover;
        crossover.prepare ({ sampleRate, 512, 1 });
        crossover.setCutoffFrequency (cutoff);

        double inputEnergy = 0.0;
        double sumEnergy = 0.0;
        int measured = 0;

        for (int n = 0; n < 48000; ++n)
        {
            const auto phase = juce::MathConstants<double>::twoPi
                             * frequency * static_cast<double> (n) / sampleRate;
            const auto x = static_cast<float> (std::sin (phase));

            float low = 0.0f;
            float high = 0.0f;
            crossover.processSample (0, x, low, high);

            const auto sum = low + high;

            expect (std::isfinite (low) && std::isfinite (high),
                    "Linkwitz-Riley crossover produced non-finite output.");

            if (n > 8192)
            {
                inputEnergy += static_cast<double> (x) * x;
                sumEnergy += static_cast<double> (sum) * sum;
                ++measured;
            }
        }

        const auto inputRms = std::sqrt (inputEnergy / measured);
        const auto sumRms = std::sqrt (sumEnergy / measured);
        const auto ratioDb = 20.0 * std::log10 (sumRms / inputRms);

        expect (std::abs (ratioDb) < 0.15,
                "Low+high Linkwitz-Riley magnitude reconstruction exceeded 0.15 dB.");
    }
}

void testOversamplingFiniteAndLatency()
{
    juce::dsp::Oversampling<float> oversampling (
        2, 2,
        juce::dsp::Oversampling<float>::filterHalfBandFIREquiripple,
        true, true);

    oversampling.initProcessing (512);
    oversampling.reset();

    const auto latency = oversampling.getLatencyInSamples();
    expect (std::isfinite (latency) && latency >= 0.0f,
            "Oversampling latency must be finite and non-negative.");

    juce::AudioBuffer<float> buffer (2, 512);
    buffer.clear();
    buffer.setSample (0, 0, 1.0f);
    buffer.setSample (1, 0, 1.0f);

    auto block = juce::dsp::AudioBlock<float> (buffer);
    auto up = oversampling.processSamplesUp (block);

    for (size_t channel = 0; channel < up.getNumChannels(); ++channel)
    {
        auto* data = up.getChannelPointer (channel);

        for (size_t i = 0; i < up.getNumSamples(); ++i)
            data[i] = std::tanh (4.0f * data[i]) / 4.0f;
    }

    oversampling.processSamplesDown (block);

    for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
        for (int i = 0; i < buffer.getNumSamples(); ++i)
            expect (std::isfinite (buffer.getSample (ch, i)),
                    "Oversampled nonlinear path produced non-finite output.");
}

void testCrestFactorDetector()
{
    constexpr double sampleRate = 48000.0;

    auto measureSine = [] (float amplitude)
    {
        cipi::dsp::CrestFactorDetector detector;
        detector.prepare (sampleRate);
        detector.setIntegrationTimeMs (80.0f);

        float crestSquared = 0.0f;

        for (int n = 0; n < 96000; ++n)
        {
            const auto phase = juce::MathConstants<double>::twoPi
                             * 440.0 * static_cast<double> (n) / sampleRate;
            crestSquared = detector.process (
                amplitude * static_cast<float> (std::sin (phase)));
        }

        return crestSquared;
    };

    const auto fullLevel = measureSine (0.8f);
    const auto lowerLevel = measureSine (0.08f);

    expect (std::isfinite (fullLevel) && std::isfinite (lowerLevel),
            "Crest detector produced non-finite output.");

    expect (std::abs (fullLevel - lowerLevel) < 0.02f,
            "Crest detector should be approximately invariant to gain scaling.");

    expect (fullLevel > 1.8f && fullLevel < 2.2f,
            "Steady sine crest-squared should settle near 2.");

    cipi::dsp::CrestFactorDetector transientDetector;
    transientDetector.prepare (sampleRate);
    transientDetector.setIntegrationTimeMs (80.0f);

    float maximumTransientFactor = 0.0f;

    for (int n = 0; n < 96000; ++n)
    {
        const auto base = 0.05f * static_cast<float> (
            std::sin (juce::MathConstants<double>::twoPi
                      * 220.0 * static_cast<double> (n) / sampleRate));

        const auto impulse = (n % 4800 == 0) ? 0.95f : 0.0f;
        transientDetector.process (base + impulse);

        maximumTransientFactor = juce::jmax (
            maximumTransientFactor,
            transientDetector.getTransientFactor());
    }

    expect (maximumTransientFactor > 0.75f,
            "Transient-rich signal should produce a high transient factor.");

    const auto transientAttackMs = 6.0f + 34.0f * maximumTransientFactor;
    const auto transientReleaseMs = 400.0f - 280.0f * maximumTransientFactor;

    expect (transientAttackMs >= 6.0f && transientAttackMs <= 40.0001f,
            "PeakBody attack mapping must remain within 6-40 ms.");
    expect (transientReleaseMs >= 119.999f && transientReleaseMs <= 400.0f,
            "PeakBody release mapping must remain within 120-400 ms.");

    transientDetector.reset();
    const auto silenceCrest = transientDetector.process (0.0f);
    const auto silenceFactor = transientDetector.getTransientFactor();

    expect (std::isfinite (silenceCrest) && std::isfinite (silenceFactor),
            "Crest detector must remain finite at silence.");
    expect (std::abs (silenceFactor) < 1.0e-6f,
            "Silence should default to zero transient factor.");
}

void testPeakBodyRevision02Policy()
{
    constexpr double sampleRate = 48000.0;
    constexpr float thresholdDb = -16.0f;
    constexpr float ratio = 2.5f;
    constexpr float kneeDb = 6.0f;

    cipi::dsp::CrestFactorDetector detector;
    detector.prepare (sampleRate);
    detector.setIntegrationTimeMs (80.0f);

    cipi::dsp::GainReductionBallistics adaptive;
    cipi::dsp::GainReductionBallistics fixed;
    adaptive.prepare (sampleRate);
    fixed.prepare (sampleRate);

    float adaptiveBurstPeakGr = 0.0f;
    float fixedBurstPeakGr = 0.0f;

    const int preSamples = static_cast<int> (0.2 * sampleRate);
    const int burstSamples = static_cast<int> (0.03 * sampleRate);
    const int totalBurstTest = preSamples + burstSamples + static_cast<int> (0.1 * sampleRate);

    for (int n = 0; n < totalBurstTest; ++n)
    {
        float x = 0.0f;

        if (n >= preSamples && n < preSamples + burstSamples)
        {
            const auto k = n - preSamples;
            x = 0.8f * static_cast<float> (
                std::sin (juce::MathConstants<double>::twoPi
                          * 220.0 * static_cast<double> (k) / sampleRate));
        }

        detector.process (x);

        const auto transientFactor = detector.getTransientFactor();
        const auto attackMs = 6.0f + 34.0f * transientFactor;
        const auto releaseMs = 400.0f - 280.0f * transientFactor;

        const auto inputDb = juce::Decibels::gainToDecibels (std::abs (x), -120.0f);
        const auto targetReductionDb = -cipi::dsp::gainComputerDb (
            inputDb, thresholdDb, ratio, kneeDb);

        const auto adaptiveGr = adaptive.process (
            targetReductionDb, attackMs, releaseMs);

        const auto fixedGr = fixed.process (
            targetReductionDb, 40.0f, 400.0f);

        if (n >= preSamples && n < preSamples + burstSamples)
        {
            adaptiveBurstPeakGr = juce::jmax (adaptiveBurstPeakGr, adaptiveGr);
            fixedBurstPeakGr = juce::jmax (fixedBurstPeakGr, fixedGr);
        }
    }

    expect (adaptiveBurstPeakGr <= fixedBurstPeakGr + 0.15f,
            "PeakBody Revision 02 must not over-compress a 30 ms burst by more than 0.15 dB versus fixed 40 ms attack.");

    detector.reset();
    adaptive.reset();

    const int sustainSamples = static_cast<int> (1.5 * sampleRate);
    float grAt150Ms = 0.0f;
    float finalGr = 0.0f;

    for (int n = 0; n < preSamples + sustainSamples; ++n)
    {
        float x = 0.0f;

        if (n >= preSamples)
        {
            const auto k = n - preSamples;
            x = 0.3f * static_cast<float> (
                std::sin (juce::MathConstants<double>::twoPi
                          * 220.0 * static_cast<double> (k) / sampleRate));
        }

        detector.process (x);

        const auto transientFactor = detector.getTransientFactor();
        const auto attackMs = 6.0f + 34.0f * transientFactor;
        const auto releaseMs = 400.0f - 280.0f * transientFactor;

        const auto inputDb = juce::Decibels::gainToDecibels (std::abs (x), -120.0f);
        const auto targetReductionDb = -cipi::dsp::gainComputerDb (
            inputDb, thresholdDb, ratio, kneeDb);

        finalGr = adaptive.process (
            targetReductionDb, attackMs, releaseMs);

        if (n == preSamples + static_cast<int> (0.15 * sampleRate))
            grAt150Ms = finalGr;
    }

    expect (finalGr > 2.5f,
            "PeakBody sustained-body test must reach meaningful steady gain reduction.");
    expect (grAt150Ms >= 0.88f * finalGr,
            "PeakBody Revision 02 must settle at least 88% toward final sustained-body GR within 150 ms.");
}
}

int main()
{
    testGainComputer();
    testEnvelopeFollower();
    testCrestFactorDetector();
    testPeakBodyRevision02Policy();
    testLinkwitzRileyReconstruction();
    testOversamplingFiniteAndLatency();

    if (failures == 0)
    {
        std::cout << "[PASS] CIPI deterministic DSP gate passed." << std::endl;
        return 0;
    }

    std::cerr << "[FAIL] CIPI deterministic DSP gate: "
              << failures << " failure(s)." << std::endl;
    return 1;
}

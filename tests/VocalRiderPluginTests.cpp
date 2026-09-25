#include "../src/plugins/VocalRider/PluginProcessor.h"

#include <cmath>
#include <iostream>
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

void runLatencyCase (double sampleRate, int blockSize)
{
    VocalRiderAudioProcessor processor;
    processor.prepareToPlay (sampleRate, blockSize);

    const auto expected = std::max (1, static_cast<int> (std::lround (sampleRate * 0.050)));
    expect (processor.getLatencySamples() == expected,
            "Latency mismatch at " + std::to_string (sampleRate)
            + " Hz. expected=" + std::to_string (expected)
            + " actual=" + std::to_string (processor.getLatencySamples()));

    juce::AudioBuffer<float> buffer (2, blockSize);
    buffer.clear();
    juce::MidiBuffer midi;

    processor.processBlock (buffer, midi);
    expect (processor.getLatencySamples() == expected,
            "Latency changed unexpectedly after processBlock at "
            + std::to_string (sampleRate) + " Hz.");

    processor.processBlockBypassed (buffer, midi);
    expect (processor.getLatencySamples() == expected,
            "Latency changed unexpectedly after bypass processing at "
            + std::to_string (sampleRate) + " Hz.");
}

void runStateRoundTrip()
{
    VocalRiderAudioProcessor processor;
    processor.prepareToPlay (48000.0, 256);

    juce::MemoryBlock state;
    processor.getStateInformation (state);

    VocalRiderAudioProcessor restored;
    restored.prepareToPlay (48000.0, 256);
    restored.setStateInformation (state.getData(), static_cast<int> (state.getSize()));

    expect (restored.getLatencySamples() == 2400,
            "State restore must not disturb the 48 kHz / 50 ms latency contract.");
}
void testBoostHeadroomGuard()
{
    constexpr double sampleRate = 48000.0;
    constexpr int blockSize = 256;

    VocalRiderAudioProcessor processor;
    processor.prepareToPlay (sampleRate, blockSize);

    juce::AudioBuffer<float> block (2, blockSize);
    juce::MidiBuffer midi;

    double phase = 0.0;
    const auto increment = 2.0 * 3.14159265358979323846 * 190.0 / sampleRate;
    float observedPeak = 0.0f;

    const auto processSeconds = [&] (double seconds, float levelDb, bool injectPeak)
    {
        const auto totalSamples = static_cast<int> (std::lround (seconds * sampleRate));
        int rendered = 0;

        while (rendered < totalSamples)
        {
            const auto n = std::min (blockSize, totalSamples - rendered);
            block.setSize (2, n, false, false, true);

            const auto amplitude = juce::Decibels::decibelsToGain (levelDb);

            for (int i = 0; i < n; ++i)
            {
                float sample = amplitude * static_cast<float> (std::sin (phase));
                phase += increment;
                if (phase >= 2.0 * 3.14159265358979323846)
                    phase -= 2.0 * 3.14159265358979323846;

                if (injectPeak && rendered + i == totalSamples / 3)
                    sample = 0.99f;

                block.setSample (0, i, sample);
                block.setSample (1, i, sample);
            }

            processor.processBlock (block, midi);

            for (int ch = 0; ch < block.getNumChannels(); ++ch)
                for (int i = 0; i < n; ++i)
                {
                    const auto y = block.getSample (ch, i);
                    expect (std::isfinite (y), "Headroom-guard scenario produced non-finite output.");
                    observedPeak = std::max (observedPeak, std::abs (y));
                }

            rendered += n;
        }
    };

    processSeconds (5.0, -20.0f, false);
    processSeconds (2.5, -28.0f, false);
    processSeconds (1.0, -28.0f, true);
    processSeconds (0.2, -28.0f, false);

    const auto ceiling = juce::Decibels::decibelsToGain (-0.20f);
    expect (observedPeak <= ceiling + 1.0e-4f,
            "Positive ride allowed a near-full-scale future peak to exceed the safety ceiling.");
}

void testBypassTransition()
{
    constexpr double sampleRate = 48000.0;
    constexpr int blockSize = 256;

    VocalRiderAudioProcessor processor;
    processor.prepareToPlay (sampleRate, blockSize);

    juce::AudioBuffer<float> block (2, blockSize);
    juce::MidiBuffer midi;

    const auto processConstant = [&] (double seconds, float value, bool bypassed,
                                      float* firstOutput, float* lastOutput)
    {
        const auto totalSamples = static_cast<int> (std::lround (seconds * sampleRate));
        int rendered = 0;
        bool firstCaptured = false;

        while (rendered < totalSamples)
        {
            const auto n = std::min (blockSize, totalSamples - rendered);
            block.setSize (2, n, false, false, true);

            for (int ch = 0; ch < 2; ++ch)
                for (int i = 0; i < n; ++i)
                    block.setSample (ch, i, value);

            if (bypassed)
                processor.processBlockBypassed (block, midi);
            else
                processor.processBlock (block, midi);

            if (! firstCaptured && firstOutput != nullptr)
            {
                *firstOutput = block.getSample (0, 0);
                firstCaptured = true;
            }

            if (lastOutput != nullptr)
                *lastOutput = block.getSample (0, n - 1);

            rendered += n;
        }
    };

    processConstant (5.0, 0.10f, false, nullptr, nullptr);
    processConstant (2.0, 0.04f, false, nullptr, nullptr);

    float lastBypassed = 0.0f;
    processConstant (0.6, 0.04f, true, nullptr, &lastBypassed);

    float firstRestored = 0.0f;
    processConstant (0.02, 0.04f, false, &firstRestored, nullptr);

    expect (std::isfinite (lastBypassed) && std::isfinite (firstRestored),
            "Bypass transition produced non-finite output.");
    expect (std::abs (firstRestored - lastBypassed) < 0.005f,
            "Host bypass restore created an excessive first-sample level jump.");
}

} // namespace

int main()
{
    for (const auto sampleRate : { 44100.0, 48000.0, 88200.0, 96000.0, 192000.0 })
        for (const auto blockSize : { 32, 64, 128, 256, 512, 1024 })
            runLatencyCase (sampleRate, blockSize);

    runStateRoundTrip();
    testBoostHeadroomGuard();
    testBypassTransition();

    if (failures == 0)
    {
        std::cout << "[PASS] Vocal Rider processor latency/state gate passed." << std::endl;
        return 0;
    }

    std::cerr << "[FAIL] Vocal Rider processor latency/state gate: "
              << failures << " failure(s)." << std::endl;
    return 1;
}

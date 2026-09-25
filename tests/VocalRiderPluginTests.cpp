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
} // namespace

int main()
{
    for (const auto sampleRate : { 44100.0, 48000.0, 88200.0, 96000.0, 192000.0 })
        for (const auto blockSize : { 32, 64, 128, 256, 512, 1024 })
            runLatencyCase (sampleRate, blockSize);

    runStateRoundTrip();

    if (failures == 0)
    {
        std::cout << "[PASS] Vocal Rider processor latency/state gate passed." << std::endl;
        return 0;
    }

    std::cerr << "[FAIL] Vocal Rider processor latency/state gate: "
              << failures << " failure(s)." << std::endl;
    return 1;
}

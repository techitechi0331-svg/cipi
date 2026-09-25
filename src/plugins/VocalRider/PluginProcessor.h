#pragma once

#include <JuceHeader.h>
#include "../../dsp/VocalRiderCore.h"

class VocalRiderAudioProcessor final : public juce::AudioProcessor
{
public:
    VocalRiderAudioProcessor();
    ~VocalRiderAudioProcessor() override = default;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    void processBlockBypassed (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    const juce::String getName() const override { return JucePlugin_Name; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram (int) override {}
    const juce::String getProgramName (int) override { return "Default"; }
    void changeProgramName (int, const juce::String&) override {}

    void getStateInformation (juce::MemoryBlock&) override;
    void setStateInformation (const void*, int) override;

private:
    static juce::AudioProcessorValueTreeState::ParameterLayout createLayout();

    void processDelayOnly (juce::AudioBuffer<float>& buffer);
    float sanitise (float value) const noexcept
    {
        return std::isfinite (value) ? value : 0.0f;
    }

    juce::AudioProcessorValueTreeState apvts;
    cipi::dsp::VocalRiderCore rider;

    juce::AudioBuffer<float> delayBuffer;
    int delayWritePosition { 0 };
    int lookaheadSamples { 0 };

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (VocalRiderAudioProcessor)
};

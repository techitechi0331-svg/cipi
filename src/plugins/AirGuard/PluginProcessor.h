#pragma once
#include <JuceHeader.h>
#include "../../dsp/EnvelopeFollower.h"
#include "../../dsp/SoftKneeCompressor.h"

class AirGuardAudioProcessor final : public juce::AudioProcessor
{
public:
    AirGuardAudioProcessor();
    ~AirGuardAudioProcessor() override = default;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

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

    juce::AudioProcessorValueTreeState apvts;
    juce::dsp::LinkwitzRileyFilter<float> crossover;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Multiplicative> focusSmoother;
    juce::SmoothedValue<float> tameSmoother;
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Multiplicative> outputGainSmoother;
    float lastAppliedFocusHz { -1.0f };

    cipi::dsp::EnvelopeFollower highEnvelope;
    cipi::dsp::EnvelopeFollower fullEnvelope;
    cipi::dsp::GainReductionBallistics grBallistics;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (AirGuardAudioProcessor)
};

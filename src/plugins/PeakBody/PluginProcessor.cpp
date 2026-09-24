#include "PluginProcessor.h"

PeakBodyAudioProcessor::PeakBodyAudioProcessor()
    : AudioProcessor (BusesProperties().withInput ("Input", juce::AudioChannelSet::stereo(), true)
                                     .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "STATE", createLayout())
{
}

juce::AudioProcessorValueTreeState::ParameterLayout PeakBodyAudioProcessor::createLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> parameters;

    parameters.push_back (
        std::make_unique<juce::AudioParameterFloat> (
            "amount", "Amount", 0.0f, 100.0f, 50.0f));

    parameters.push_back (
        std::make_unique<juce::AudioParameterFloat> (
            "output", "Output", -12.0f, 12.0f, 0.0f));

    return { parameters.begin(), parameters.end() };
}

bool PeakBodyAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    const auto input = layouts.getMainInputChannelSet();
    const auto output = layouts.getMainOutputChannelSet();

    return input == output
        && (input == juce::AudioChannelSet::mono()
            || input == juce::AudioChannelSet::stereo());
}

void PeakBodyAudioProcessor::prepareToPlay (double sampleRate, int)
{
    crestDetector.prepare (sampleRate);
    crestDetector.setIntegrationTimeMs (200.0f);

    gainReduction.prepare (sampleRate);

    const auto amount = apvts.getRawParameterValue ("amount")->load() * 0.01f;
    const auto outputGain = juce::Decibels::decibelsToGain (
        apvts.getRawParameterValue ("output")->load());

    amountSmoother.reset (sampleRate, 0.010);
    amountSmoother.setCurrentAndTargetValue (amount);

    outputGainSmoother.reset (sampleRate, 0.010);
    outputGainSmoother.setCurrentAndTargetValue (outputGain);
}

void PeakBodyAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer,
                                           juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    amountSmoother.setTargetValue (
        apvts.getRawParameterValue ("amount")->load() * 0.01f);

    outputGainSmoother.setTargetValue (
        juce::Decibels::decibelsToGain (
            apvts.getRawParameterValue ("output")->load()));

    const auto numChannels = buffer.getNumChannels();
    const auto numSamples = buffer.getNumSamples();

    for (int sample = 0; sample < numSamples; ++sample)
    {
        float linkedMagnitude = 0.0f;

        for (int channel = 0; channel < numChannels; ++channel)
            linkedMagnitude = juce::jmax (
                linkedMagnitude,
                std::abs (buffer.getSample (channel, sample)));

        crestDetector.process (linkedMagnitude);

        const auto timingScale = crestDetector.getTimingScale (0.25f, 0.35f);
        const auto attackMs = 40.0f * timingScale;
        const auto releaseMs = 400.0f * timingScale;

        const auto amount = amountSmoother.getNextValue();

        const auto thresholdDb = juce::jmap (amount, -8.0f, -24.0f);
        const auto ratio = 1.0f + 3.0f * amount;
        constexpr float kneeDb = 6.0f;

        const auto inputDb = juce::Decibels::gainToDecibels (
            linkedMagnitude, -120.0f);

        const auto targetGainDb = cipi::dsp::gainComputerDb (
            inputDb, thresholdDb, ratio, kneeDb);

        const auto targetReductionDb =
            amount <= 0.0001f ? 0.0f : -targetGainDb;

        const auto reductionDb = gainReduction.process (
            targetReductionDb, attackMs, releaseMs);

        const auto gain = juce::Decibels::decibelsToGain (-reductionDb)
                        * outputGainSmoother.getNextValue();

        for (int channel = 0; channel < numChannels; ++channel)
            buffer.setSample (
                channel,
                sample,
                buffer.getSample (channel, sample) * gain);
    }
}

juce::AudioProcessorEditor* PeakBodyAudioProcessor::createEditor()
{
    return new juce::GenericAudioProcessorEditor (*this);
}

void PeakBodyAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void PeakBodyAudioProcessor::setStateInformation (const void* data, int size)
{
    if (auto xml = getXmlFromBinary (data, size))
        apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new PeakBodyAudioProcessor();
}

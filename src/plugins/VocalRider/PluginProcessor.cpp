#include "PluginProcessor.h"

#include <cmath>

VocalRiderAudioProcessor::VocalRiderAudioProcessor()
    : AudioProcessor (BusesProperties().withInput ("Input", juce::AudioChannelSet::stereo(), true)
                                     .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "STATE", createLayout())
{
}

juce::AudioProcessorValueTreeState::ParameterLayout VocalRiderAudioProcessor::createLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> parameters;
    parameters.push_back (std::make_unique<juce::AudioParameterFloat> (
        "amount", "Amount", juce::NormalisableRange<float> (0.0f, 100.0f, 0.1f), 50.0f));
    parameters.push_back (std::make_unique<juce::AudioParameterFloat> (
        "output", "Output", juce::NormalisableRange<float> (-12.0f, 12.0f, 0.1f), 0.0f));
    return { parameters.begin(), parameters.end() };
}

bool VocalRiderAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    const auto input = layouts.getMainInputChannelSet();
    const auto output = layouts.getMainOutputChannelSet();

    if (input != output)
        return false;

    return input == juce::AudioChannelSet::mono() || input == juce::AudioChannelSet::stereo();
}

void VocalRiderAudioProcessor::prepareToPlay (double sampleRate, int)
{
    rider.prepare (sampleRate);

    amountSmooth.reset (sampleRate, 0.050);
    outputGainSmooth.reset (sampleRate, 0.020);

    const auto initialAmount = juce::jlimit (
        0.0f, 1.0f, apvts.getRawParameterValue ("amount")->load() * 0.01f);
    const auto initialOutputGain = juce::Decibels::decibelsToGain (
        apvts.getRawParameterValue ("output")->load());

    amountSmooth.setCurrentAndTargetValue (initialAmount);
    outputGainSmooth.setCurrentAndTargetValue (initialOutputGain);
    controlsPrimed = true;

    lookaheadSamples = juce::jmax (1, static_cast<int> (std::lround (sampleRate * 0.050)));
    delayBuffer.setSize (juce::jmax (1, getTotalNumInputChannels()), lookaheadSamples, false, true, true);
    delayBuffer.clear();
    delayWritePosition = 0;

    headroomGuard.prepare (sampleRate, lookaheadSamples);

    setLatencySamples (lookaheadSamples);
}

void VocalRiderAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    const auto channels = buffer.getNumChannels();
    const auto samples = buffer.getNumSamples();

    if (channels <= 0 || samples <= 0 || delayBuffer.getNumSamples() <= 0)
        return;

    const auto requestedAmount = juce::jlimit (
        0.0f, 1.0f, apvts.getRawParameterValue ("amount")->load() * 0.01f);
    const auto requestedOutputGain = juce::Decibels::decibelsToGain (
        apvts.getRawParameterValue ("output")->load());

    if (! controlsPrimed)
    {
        amountSmooth.setCurrentAndTargetValue (requestedAmount);
        outputGainSmooth.setCurrentAndTargetValue (requestedOutputGain);
        controlsPrimed = true;
    }
    else
    {
        amountSmooth.setTargetValue (requestedAmount);
        outputGainSmooth.setTargetValue (requestedOutputGain);
    }

    for (int i = 0; i < samples; ++i)
    {
        float linkedAbs = 0.0f;

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto input = sanitise (buffer.getSample (ch, i));
            linkedAbs = juce::jmax (linkedAbs, std::abs (input));
        }

        const auto amount = amountSmooth.getNextValue();
        const auto outputGain = outputGainSmooth.getNextValue();
        const auto rideDb = rider.processSample (linkedAbs, amount);

        const auto safetyOutputGain = juce::jmax (
            outputGain, outputGainSmooth.getTargetValue());
        const auto protectedRideDb = headroomGuard.process (
            linkedAbs, safetyOutputGain, rideDb);
        const auto totalGain = juce::Decibels::decibelsToGain (protectedRideDb) * outputGain;

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto input = sanitise (buffer.getSample (ch, i));
            auto* delay = delayBuffer.getWritePointer (ch);
            const auto delayed = delay[delayWritePosition];
            delay[delayWritePosition] = input;

            auto output = delayed * totalGain;
            if (! std::isfinite (output))
                output = 0.0f;

            buffer.setSample (ch, i, output);
        }

        if (++delayWritePosition >= lookaheadSamples)
            delayWritePosition = 0;
    }
}

void VocalRiderAudioProcessor::processDelayOnly (juce::AudioBuffer<float>& buffer)
{
    const auto channels = buffer.getNumChannels();
    const auto samples = buffer.getNumSamples();

    if (channels <= 0 || samples <= 0 || delayBuffer.getNumSamples() <= 0)
        return;

    for (int i = 0; i < samples; ++i)
    {
        for (int ch = 0; ch < channels; ++ch)
        {
            const auto input = sanitise (buffer.getSample (ch, i));
            auto* delay = delayBuffer.getWritePointer (ch);
            const auto delayed = delay[delayWritePosition];
            delay[delayWritePosition] = input;
            buffer.setSample (ch, i, delayed);
        }

        if (++delayWritePosition >= lookaheadSamples)
            delayWritePosition = 0;
    }
}

void VocalRiderAudioProcessor::processBlockBypassed (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    const auto channels = buffer.getNumChannels();
    const auto samples = buffer.getNumSamples();

    if (channels <= 0 || samples <= 0 || delayBuffer.getNumSamples() <= 0)
        return;

    amountSmooth.setTargetValue (0.0f);
    outputGainSmooth.setTargetValue (1.0f);

    for (int i = 0; i < samples; ++i)
    {
        float linkedAbs = 0.0f;

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto input = sanitise (buffer.getSample (ch, i));
            linkedAbs = juce::jmax (linkedAbs, std::abs (input));
        }

        const auto amount = amountSmooth.getNextValue();
        const auto neutralOutputGain = outputGainSmooth.getNextValue();
        const auto rideDb = rider.processSample (linkedAbs, amount);
        (void) headroomGuard.process (linkedAbs, neutralOutputGain, rideDb);

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto input = sanitise (buffer.getSample (ch, i));
            auto* delay = delayBuffer.getWritePointer (ch);
            const auto delayed = delay[delayWritePosition];
            delay[delayWritePosition] = input;
            buffer.setSample (ch, i, delayed);
        }

        if (++delayWritePosition >= lookaheadSamples)
            delayWritePosition = 0;
    }
}

juce::AudioProcessorEditor* VocalRiderAudioProcessor::createEditor()
{
    return new juce::GenericAudioProcessorEditor (*this);
}

void VocalRiderAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void VocalRiderAudioProcessor::setStateInformation (const void* data, int size)
{
    if (auto xml = getXmlFromBinary (data, size))
        apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new VocalRiderAudioProcessor();
}

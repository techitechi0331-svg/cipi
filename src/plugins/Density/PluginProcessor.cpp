#include "PluginProcessor.h"
#include <cmath>

DensityAudioProcessor::DensityAudioProcessor()
    : AudioProcessor (BusesProperties().withInput ("Input", juce::AudioChannelSet::stereo(), true)
                                     .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "STATE", createLayout())
{
}

juce::AudioProcessorValueTreeState::ParameterLayout DensityAudioProcessor::createLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> p;
    p.push_back (std::make_unique<juce::AudioParameterFloat> ("density", "Density", 0.0f, 100.0f, 35.0f));
    p.push_back (std::make_unique<juce::AudioParameterFloat> ("output", "Output", -12.0f, 12.0f, 0.0f));
    return { p.begin(), p.end() };
}

bool DensityAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    const auto in = layouts.getMainInputChannelSet();
    const auto out = layouts.getMainOutputChannelSet();
    return in == out && (in == juce::AudioChannelSet::mono() || in == juce::AudioChannelSet::stereo());
}

void DensityAudioProcessor::prepareToPlay (double, int samplesPerBlock)
{
    const auto channels = (size_t) juce::jmax (1, getTotalNumInputChannels());
    oversampling = std::make_unique<juce::dsp::Oversampling<float>> (
        channels, 2, juce::dsp::Oversampling<float>::filterHalfBandPolyphaseIIR, true, true);

    oversampling->initProcessing ((size_t) juce::jmax (1, samplesPerBlock));
    oversampling->reset();
    setLatencySamples ((int) std::round (oversampling->getLatencyInSamples()));

    dryBuffer.setSize ((int) channels, juce::jmax (1, samplesPerBlock), false, false, true);
}

void DensityAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    const auto channels = buffer.getNumChannels();
    const auto samples = buffer.getNumSamples();

    if (dryBuffer.getNumSamples() < samples)
        return;

    for (int ch = 0; ch < channels; ++ch)
        dryBuffer.copyFrom (ch, 0, buffer, ch, 0, samples);

    const auto density = apvts.getRawParameterValue ("density")->load() * 0.01f;
    const auto drive = 1.0f + 9.0f * density * density;
    const auto wet = 0.48f * density;
    const auto dry = 1.0f - wet;
    const auto output = juce::Decibels::decibelsToGain (apvts.getRawParameterValue ("output")->load());

    if (oversampling != nullptr && density > 0.0001f)
    {
        auto block = juce::dsp::AudioBlock<float> (buffer);
        auto up = oversampling->processSamplesUp (block);

        for (size_t ch = 0; ch < up.getNumChannels(); ++ch)
        {
            auto* d = up.getChannelPointer (ch);
            for (size_t i = 0; i < up.getNumSamples(); ++i)
                d[i] = std::tanh (drive * d[i]) / drive;
        }

        oversampling->processSamplesDown (block);
    }

    for (int ch = 0; ch < channels; ++ch)
    {
        auto* wetData = buffer.getWritePointer (ch);
        const auto* dryData = dryBuffer.getReadPointer (ch);

        for (int i = 0; i < samples; ++i)
            wetData[i] = (dryData[i] * dry + wetData[i] * wet) * output;
    }
}

juce::AudioProcessorEditor* DensityAudioProcessor::createEditor()
{
    return new juce::GenericAudioProcessorEditor (*this);
}

void DensityAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void DensityAudioProcessor::setStateInformation (const void* data, int size)
{
    if (auto xml = getXmlFromBinary (data, size))
        apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new DensityAudioProcessor();
}

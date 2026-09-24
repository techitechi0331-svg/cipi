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

void DensityAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    const auto channels = (size_t) juce::jmax (1, getTotalNumInputChannels());
    const auto maxBlock = (juce::uint32) juce::jmax (1, samplesPerBlock);

    // Parallel saturation needs predictable phase alignment. Use linear-phase FIR
    // oversampling and compensate its wet-path latency inside the dry/wet mixer.
    oversampling = std::make_unique<juce::dsp::Oversampling<float>> (
        channels, 2, juce::dsp::Oversampling<float>::filterHalfBandFIREquiripple, true, true);

    oversampling->initProcessing ((size_t) maxBlock);
    oversampling->reset();

    const auto latency = oversampling->getLatencyInSamples();
    setLatencySamples ((int) std::round (latency));

    juce::dsp::ProcessSpec spec { sampleRate, maxBlock, (juce::uint32) channels };
    dryWetMixer.prepare (spec);
    dryWetMixer.reset();
    dryWetMixer.setMixingRule (juce::dsp::DryWetMixingRule::linear);
    dryWetMixer.setWetLatency (latency);
    dryWetMixer.setWetMixProportion (0.0f);
}

void DensityAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    const auto density = apvts.getRawParameterValue ("density")->load() * 0.01f;
    const auto drive = 1.0f + 9.0f * density * density;
    const auto wet = 0.48f * density;
    const auto output = juce::Decibels::decibelsToGain (apvts.getRawParameterValue ("output")->load());

    auto block = juce::dsp::AudioBlock<float> (buffer);
    dryWetMixer.pushDrySamples (juce::dsp::AudioBlock<const float> (buffer));
    dryWetMixer.setWetMixProportion (wet);

    if (oversampling != nullptr)
    {
        auto up = oversampling->processSamplesUp (block);

        if (density > 0.0001f)
        {
            for (size_t ch = 0; ch < up.getNumChannels(); ++ch)
            {
                auto* d = up.getChannelPointer (ch);
                for (size_t i = 0; i < up.getNumSamples(); ++i)
                    d[i] = std::tanh (drive * d[i]) / drive;
            }
        }

        oversampling->processSamplesDown (block);
        dryWetMixer.mixWetSamples (block);
    }

    buffer.applyGain (output);
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

#include "PluginProcessor.h"

VoxLevelAudioProcessor::VoxLevelAudioProcessor()
    : AudioProcessor (BusesProperties().withInput ("Input", juce::AudioChannelSet::stereo(), true)
                                     .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "STATE", createLayout())
{
}

juce::AudioProcessorValueTreeState::ParameterLayout VoxLevelAudioProcessor::createLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> p;
    p.push_back (std::make_unique<juce::AudioParameterFloat> ("amount", "Amount", 0.0f, 100.0f, 50.0f));
    p.push_back (std::make_unique<juce::AudioParameterFloat> ("output", "Output", -12.0f, 12.0f, 0.0f));
    return { p.begin(), p.end() };
}

bool VoxLevelAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    const auto in = layouts.getMainInputChannelSet();
    const auto out = layouts.getMainOutputChannelSet();
    return in == out && (in == juce::AudioChannelSet::mono() || in == juce::AudioChannelSet::stereo());
}

void VoxLevelAudioProcessor::prepareToPlay (double sampleRate, int)
{
    slowEnvelope.prepare (sampleRate);
    fastEnvelope.prepare (sampleRate);
    ballistics.prepare (sampleRate);
    slowEnvelope.setAttackRelease (12.0f, 140.0f);
    fastEnvelope.setAttackRelease (1.2f, 55.0f);
}

void VoxLevelAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;

    const auto amount = apvts.getRawParameterValue ("amount")->load() * 0.01f;
    const auto outputDb = apvts.getRawParameterValue ("output")->load();
    const auto outGain = juce::Decibels::decibelsToGain (outputDb);

    const auto thresholdDb = juce::jmap (amount, -8.0f, -24.0f);
    const auto ratio = 1.0f + amount * 3.0f;
    const auto kneeDb = 3.0f + amount * 6.0f;
    const auto attackMs = juce::jmap (amount, 9.0f, 2.5f);
    const auto baseReleaseMs = juce::jmap (amount, 90.0f, 180.0f);

    const auto channels = buffer.getNumChannels();
    const auto samples = buffer.getNumSamples();

    for (int i = 0; i < samples; ++i)
    {
        float linkedPeak = 0.0f;
        for (int ch = 0; ch < channels; ++ch)
            linkedPeak = juce::jmax (linkedPeak, std::abs (buffer.getSample (ch, i)));

        const auto slow = slowEnvelope.process (linkedPeak);
        const auto fast = fastEnvelope.process (linkedPeak);
        const auto detector = juce::jmax (slow, fast * 0.50f);
        const auto detectorDb = juce::Decibels::gainToDecibels (detector, -120.0f);

        const auto targetGainDb = cipi::dsp::gainComputerDb (detectorDb, thresholdDb, ratio, kneeDb);
        const auto targetGrDb = amount <= 0.0001f ? 0.0f : -targetGainDb;

        const auto releaseScale = 1.0f + 1.25f * juce::jlimit (0.0f, 1.0f, ballistics.getCurrentDb() / 12.0f);
        const auto grDb = ballistics.process (targetGrDb, attackMs, baseReleaseMs * releaseScale);
        const auto gain = juce::Decibels::decibelsToGain (-grDb) * outGain;

        for (int ch = 0; ch < channels; ++ch)
            buffer.setSample (ch, i, buffer.getSample (ch, i) * gain);
    }
}

juce::AudioProcessorEditor* VoxLevelAudioProcessor::createEditor()
{
    return new juce::GenericAudioProcessorEditor (*this);
}

void VoxLevelAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void VoxLevelAudioProcessor::setStateInformation (const void* data, int size)
{
    if (auto xml = getXmlFromBinary (data, size))
        apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new VoxLevelAudioProcessor();
}

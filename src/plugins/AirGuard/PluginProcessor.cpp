#include "PluginProcessor.h"

AirGuardAudioProcessor::AirGuardAudioProcessor()
    : AudioProcessor (BusesProperties().withInput ("Input", juce::AudioChannelSet::stereo(), true)
                                     .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "STATE", createLayout())
{
}

juce::AudioProcessorValueTreeState::ParameterLayout AirGuardAudioProcessor::createLayout()
{
    std::vector<std::unique_ptr<juce::RangedAudioParameter>> p;
    p.push_back (std::make_unique<juce::AudioParameterFloat> ("tame", "Tame", 0.0f, 100.0f, 50.0f));
    p.push_back (std::make_unique<juce::AudioParameterFloat> ("focus", "Focus", 4200.0f, 8500.0f, 5600.0f));
    p.push_back (std::make_unique<juce::AudioParameterFloat> ("output", "Output", -12.0f, 12.0f, 0.0f));
    return { p.begin(), p.end() };
}

bool AirGuardAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    const auto in = layouts.getMainInputChannelSet();
    const auto out = layouts.getMainOutputChannelSet();
    return in == out && (in == juce::AudioChannelSet::mono() || in == juce::AudioChannelSet::stereo());
}

void AirGuardAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    currentSampleRate = sampleRate;
    highEnvelope.prepare (sampleRate);
    fullEnvelope.prepare (sampleRate);
    grBallistics.prepare (sampleRate);
    highEnvelope.setAttackRelease (0.8f, 55.0f);
    fullEnvelope.setAttackRelease (8.0f, 120.0f);

    juce::dsp::ProcessSpec spec { sampleRate, (juce::uint32) juce::jmax (1, samplesPerBlock), 1 };
    for (auto* bank : { &lp, &hp })
        for (auto& ch : *bank)
            for (auto& f : ch)
                f.prepare (spec);

    lastFocusHz = -1.0f;
    updateCrossover();
}

void AirGuardAudioProcessor::updateCrossover()
{
    const auto focus = apvts.getRawParameterValue ("focus")->load();
    if (std::abs (focus - lastFocusHz) < 0.5f)
        return;

    lastFocusHz = focus;
    constexpr float q = 0.70710678f;
    auto lowC = Coeff::makeLowPass (currentSampleRate, focus, q);
    auto highC = Coeff::makeHighPass (currentSampleRate, focus, q);

    for (auto& ch : lp)
        for (auto& f : ch)
            f.coefficients = lowC;

    for (auto& ch : hp)
        for (auto& f : ch)
            f.coefficients = highC;
}

void AirGuardAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{
    juce::ScopedNoDenormals noDenormals;
    updateCrossover();

    const auto tame = apvts.getRawParameterValue ("tame")->load() * 0.01f;
    const auto outGain = juce::Decibels::decibelsToGain (apvts.getRawParameterValue ("output")->load());
    const auto ratioThresholdDb = juce::jmap (tame, -6.0f, -18.0f);
    const auto maxReductionDb = 12.0f * tame;

    const auto channels = buffer.getNumChannels();
    const auto samples = buffer.getNumSamples();

    for (int i = 0; i < samples; ++i)
    {
        float lowS[2] {};
        float highS[2] {};
        float linkedHigh = 0.0f;
        float linkedFull = 0.0f;

        for (int ch = 0; ch < channels; ++ch)
        {
            const auto x = buffer.getSample (ch, i);
            auto lo = lp[(size_t) ch][0].processSample (x);
            lo = lp[(size_t) ch][1].processSample (lo);
            auto hi = hp[(size_t) ch][0].processSample (x);
            hi = hp[(size_t) ch][1].processSample (hi);
            lowS[ch] = lo;
            highS[ch] = hi;
            linkedHigh = juce::jmax (linkedHigh, std::abs (hi));
            linkedFull = juce::jmax (linkedFull, std::abs (x));
        }

        const auto hiDb = juce::Decibels::gainToDecibels (highEnvelope.process (linkedHigh), -120.0f);
        const auto fullDb = juce::Decibels::gainToDecibels (fullEnvelope.process (linkedFull), -120.0f);
        const auto spectralRatioDb = hiDb - fullDb;

        float target = 0.0f;
        if (tame > 0.0001f && spectralRatioDb > ratioThresholdDb)
            target = juce::jmin (maxReductionDb, (spectralRatioDb - ratioThresholdDb) * (0.55f + 1.45f * tame));

        const auto gr = grBallistics.process (target, 0.45f, 55.0f + 70.0f * tame);
        const auto hiGain = juce::Decibels::decibelsToGain (-gr);

        for (int ch = 0; ch < channels; ++ch)
            buffer.setSample (ch, i, (lowS[ch] + highS[ch] * hiGain) * outGain);
    }
}

juce::AudioProcessorEditor* AirGuardAudioProcessor::createEditor()
{
    return new juce::GenericAudioProcessorEditor (*this);
}

void AirGuardAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void AirGuardAudioProcessor::setStateInformation (const void* data, int size)
{
    if (auto xml = getXmlFromBinary (data, size))
        apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new AirGuardAudioProcessor();
}

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import FACTORY_VERSION
from .contract import contract_sha256, validate_contract


def _cpp_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _cpp_float(value: float | int) -> str:
    text = format(float(value), ".9g")
    if "." not in text and "e" not in text.lower():
        text += ".0"
    return text + "f"


def _target_name(plugin_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]", "", plugin_id)
    if not safe:
        raise ValueError("plugin id cannot produce an empty CMake target")
    if safe[0].isdigit():
        safe = "P" + safe
    return "JF" + safe


def _refuse_nonempty(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


def generate_project(contract: dict[str, Any], output_dir: str | Path) -> Path:
    validate_contract(contract)
    out = Path(output_dir)
    _refuse_nonempty(out)
    source = out / "Source"
    tests = out / "Tests"
    source.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)

    plugin = contract["plugin"]
    ui = contract["ui"]
    gain = next(p for p in contract["parameters"] if p["id"] == "gain_db")
    target = _target_name(plugin["id"])

    cmake = f'''cmake_minimum_required(VERSION 3.24)
project({target} VERSION {plugin["version"]} LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(DEFINED JUCE_SOURCE_DIR AND EXISTS "${{JUCE_SOURCE_DIR}}/CMakeLists.txt")
    add_subdirectory("${{JUCE_SOURCE_DIR}}" JUCE)
elseif(EXISTS "${{CMAKE_SOURCE_DIR}}/JUCE/CMakeLists.txt")
    add_subdirectory(JUCE)
else()
    include(FetchContent)
    FetchContent_Declare(
        JUCE
        GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
        GIT_TAG 9.0.2
        GIT_SHALLOW TRUE
    )
    FetchContent_MakeAvailable(JUCE)
endif()

juce_add_plugin({target}
    COMPANY_NAME "{_cpp_string(plugin["vendor"])}"
    BUNDLE_ID "{plugin["bundle_id"]}"
    PLUGIN_MANUFACTURER_CODE {plugin["manufacturer_code"]}
    PLUGIN_CODE {plugin["plugin_code"]}
    FORMATS VST3
    PRODUCT_NAME "{_cpp_string(plugin["name"])}"
    COPY_PLUGIN_AFTER_BUILD FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
)

juce_generate_juce_header({target})

target_sources({target}
    PRIVATE
        Source/PluginProcessor.cpp
        Source/PluginProcessor.h
        Source/PluginEditor.cpp
        Source/PluginEditor.h
)

target_compile_definitions({target}
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries({target}
    PRIVATE
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
)

enable_testing()
add_executable({target}FactoryTests Tests/DspTests.cpp)
target_include_directories({target}FactoryTests PRIVATE Source)
add_test(NAME {target}.DSPMatrix COMMAND {target}FactoryTests)
'''
    processor_h = r'''#pragma once

#include <JuceHeader.h>
#include "GoldenGainDSP.h"

class FactoryPluginAudioProcessor final : public juce::AudioProcessor
{
public:
    FactoryPluginAudioProcessor();
    ~FactoryPluginAudioProcessor() override = default;

    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;
    void processBlock(juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return JucePlugin_Name; }
    bool acceptsMidi() const override { return false; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 0.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}

    void getStateInformation(juce::MemoryBlock&) override;
    void setStateInformation(const void*, int) override;

    juce::AudioProcessorValueTreeState apvts;

private:
    static juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();
    GoldenGainDSP dsp;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(FactoryPluginAudioProcessor)
};
'''
    processor_cpp = f'''#include "PluginProcessor.h"
#include "PluginEditor.h"

FactoryPluginAudioProcessor::FactoryPluginAudioProcessor()
    : juce::AudioProcessor(BusesProperties()
          .withInput("Input", juce::AudioChannelSet::stereo(), true)
          .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      apvts(*this, nullptr, "PARAMETERS", createParameterLayout())
{{
}}

juce::AudioProcessorValueTreeState::ParameterLayout FactoryPluginAudioProcessor::createParameterLayout()
{{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        juce::ParameterID{{"gain_db", 1}},
        "{_cpp_string(gain.get("name", "Gain"))}",
        juce::NormalisableRange<float>({_cpp_float(gain["min"])}, {_cpp_float(gain["max"])}, 0.01f),
        {_cpp_float(gain["default"])},
        "dB"));
    return layout;
}}

void FactoryPluginAudioProcessor::prepareToPlay(double sampleRate, int)
{{
    dsp.prepare(sampleRate);
    dsp.setGainDb(apvts.getRawParameterValue("gain_db")->load());
}}

bool FactoryPluginAudioProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{{
    const auto in = layouts.getMainInputChannelSet();
    const auto out = layouts.getMainOutputChannelSet();
    if (in != out)
        return false;
    return in == juce::AudioChannelSet::mono() || in == juce::AudioChannelSet::stereo();
}}

void FactoryPluginAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer&)
{{
    juce::ScopedNoDenormals noDenormals;
    dsp.setGainDb(apvts.getRawParameterValue("gain_db")->load());

    std::array<float*, 2> channels {{ nullptr, nullptr }};
    const auto numChannels = juce::jmin(buffer.getNumChannels(), static_cast<int>(channels.size()));
    for (int channel = 0; channel < numChannels; ++channel)
        channels[static_cast<size_t>(channel)] = buffer.getWritePointer(channel);

    dsp.process(channels.data(), numChannels, buffer.getNumSamples());
}}

juce::AudioProcessorEditor* FactoryPluginAudioProcessor::createEditor()
{{
    return new FactoryPluginAudioProcessorEditor(*this);
}}

void FactoryPluginAudioProcessor::getStateInformation(juce::MemoryBlock& destData)
{{
    const auto state = apvts.copyState();
    if (const auto xml = state.createXml())
        copyXmlToBinary(*xml, destData);
}}

void FactoryPluginAudioProcessor::setStateInformation(const void* data, int sizeInBytes)
{{
    if (const auto xml = getXmlFromBinary(data, sizeInBytes))
        if (xml->hasTagName(apvts.state.getType()))
            apvts.replaceState(juce::ValueTree::fromXml(*xml));
}}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{{
    return new FactoryPluginAudioProcessor();
}}
'''
    dsp_core_h = r'''#pragma once

#include <algorithm>
#include <cmath>

class GoldenGainDSP
{
public:
    void prepare(double sampleRate)
    {
        const auto safeRate = std::isfinite(sampleRate) && sampleRate > 1.0 ? sampleRate : 44100.0;
        rampLengthSamples = std::max(1, static_cast<int>(std::llround(safeRate * 0.020)));
        currentGain = targetGain;
        step = 0.0f;
        remaining = 0;
    }

    void setGainDb(float db)
    {
        if (!std::isfinite(db))
            db = 0.0f;

        db = std::clamp(db, -96.0f, 48.0f);
        const auto nextTarget = std::pow(10.0f, db / 20.0f);

        if (!std::isfinite(nextTarget))
            return;

        if (std::abs(nextTarget - targetGain) <= 1.0e-9f)
            return;

        targetGain = nextTarget;
        remaining = rampLengthSamples;
        step = (targetGain - currentGain) / static_cast<float>(remaining);
    }

    void process(float* const* channels, int numChannels, int numSamples)
    {
        if (channels == nullptr || numChannels <= 0 || numSamples <= 0)
            return;

        for (int sample = 0; sample < numSamples; ++sample)
        {
            if (remaining > 0)
            {
                currentGain += step;
                --remaining;
                if (remaining == 0)
                    currentGain = targetGain;
            }

            if (!std::isfinite(currentGain))
            {
                currentGain = 1.0f;
                targetGain = 1.0f;
                step = 0.0f;
                remaining = 0;
            }

            for (int channel = 0; channel < numChannels; ++channel)
            {
                auto* data = channels[channel];
                if (data == nullptr)
                    continue;

                const auto input = std::isfinite(data[sample]) ? data[sample] : 0.0f;
                const auto output = input * currentGain;
                data[sample] = std::isfinite(output) ? output : 0.0f;
            }
        }
    }

private:
    int rampLengthSamples = 882;
    int remaining = 0;
    float currentGain = 1.0f;
    float targetGain = 1.0f;
    float step = 0.0f;
};
'''

    dsp_tests_cpp = r'''#include "GoldenGainDSP.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace
{
void require(bool condition, const char* message)
{
    if (!condition)
        throw std::runtime_error(message);
}

bool finiteBuffer(const std::vector<float>& buffer)
{
    return std::all_of(buffer.begin(), buffer.end(), [](float value) { return std::isfinite(value); });
}

void processBlocks(GoldenGainDSP& dsp, std::vector<float>& data, const std::vector<int>& blocks)
{
    int offset = 0;
    size_t blockIndex = 0;
    while (offset < static_cast<int>(data.size()))
    {
        const auto requested = blocks[blockIndex++ % blocks.size()];
        const auto count = std::min(requested, static_cast<int>(data.size()) - offset);
        float* channel = data.data() + offset;
        dsp.process(&channel, 1, count);
        offset += count;
    }
}

void testSilenceAndFiniteMatrix()
{
    const double sampleRates[] = { 44100.0, 48000.0, 88200.0, 96000.0, 192000.0 };
    const int blockSizes[] = { 32, 64, 127, 256, 511, 1024 };

    for (auto sampleRate : sampleRates)
    {
        for (auto blockSize : blockSizes)
        {
            GoldenGainDSP dsp;
            dsp.prepare(sampleRate);
            dsp.setGainDb(24.0f);
            std::vector<float> data(static_cast<size_t>(blockSize), 0.0f);
            float* channel = data.data();
            dsp.process(&channel, 1, blockSize);
            require(finiteBuffer(data), "silence matrix produced non-finite output");
            require(std::all_of(data.begin(), data.end(), [](float value) { return value == 0.0f; }),
                    "silence matrix produced non-zero output");
        }
    }
}

void testSettledGain()
{
    GoldenGainDSP dsp;
    dsp.prepare(48000.0);
    dsp.setGainDb(6.0f);
    std::vector<float> data(2200, 1.0f);
    processBlocks(dsp, data, { 64, 127, 31, 256 });
    const auto expected = std::pow(10.0f, 6.0f / 20.0f);
    require(std::abs(data.back() - expected) < 1.0e-4f, "gain did not settle to expected value");
}

void testBlockSegmentationInvariant()
{
    std::vector<float> a(4096, 0.25f);
    std::vector<float> b = a;

    GoldenGainDSP first;
    GoldenGainDSP second;
    first.prepare(96000.0);
    second.prepare(96000.0);
    first.setGainDb(12.0f);
    second.setGainDb(12.0f);

    processBlocks(first, a, { 4096 });
    processBlocks(second, b, { 17, 64, 255, 1024, 33 });

    require(a.size() == b.size(), "block invariance size mismatch");
    for (size_t i = 0; i < a.size(); ++i)
        require(std::abs(a[i] - b[i]) < 1.0e-7f, "block segmentation changed DSP output");
}

void testRapidAutomationAndNonFiniteDefense()
{
    GoldenGainDSP dsp;
    dsp.prepare(44100.0);

    std::vector<float> data(8192, 0.5f);
    int offset = 0;
    bool high = false;
    while (offset < static_cast<int>(data.size()))
    {
        dsp.setGainDb(high ? 24.0f : -24.0f);
        high = !high;
        const auto count = std::min(37, static_cast<int>(data.size()) - offset);
        float* channel = data.data() + offset;
        dsp.process(&channel, 1, count);
        offset += count;
    }
    require(finiteBuffer(data), "rapid automation produced non-finite output");

    dsp.setGainDb(std::numeric_limits<float>::quiet_NaN());
    std::vector<float> hostile { 1.0f, std::numeric_limits<float>::infinity(), -1.0f };
    float* channel = hostile.data();
    dsp.process(&channel, 1, static_cast<int>(hostile.size()));
    require(finiteBuffer(hostile), "non-finite defense failed");
}
}

int main()
{
    try
    {
        testSilenceAndFiniteMatrix();
        testSettledGain();
        testBlockSegmentationInvariant();
        testRapidAutomationAndNonFiniteDefense();
        std::cout << "JUCE Factory DSP matrix: PASS\n";
        return 0;
    }
    catch (const std::exception& e)
    {
        std::cerr << "JUCE Factory DSP matrix: FAIL: " << e.what() << "\n";
        return 1;
    }
}
'''

    editor_h = r'''#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

class FactoryPluginAudioProcessorEditor final : public juce::AudioProcessorEditor
{
public:
    explicit FactoryPluginAudioProcessorEditor(FactoryPluginAudioProcessor&);
    ~FactoryPluginAudioProcessorEditor() override = default;

    void paint(juce::Graphics&) override;
    void resized() override;

private:
    FactoryPluginAudioProcessor& processor;
    juce::Slider gainSlider;
    juce::Label gainLabel;
    juce::Label versionLabel;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> gainAttachment;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(FactoryPluginAudioProcessorEditor)
};
'''
    show_version = "true" if ui["show_version"] else "false"
    editor_cpp = f'''#include "PluginEditor.h"

FactoryPluginAudioProcessorEditor::FactoryPluginAudioProcessorEditor(FactoryPluginAudioProcessor& p)
    : juce::AudioProcessorEditor(&p), processor(p)
{{
    gainSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    gainSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 90, 24);
    gainLabel.setText("Gain", juce::dontSendNotification);
    gainLabel.setJustificationType(juce::Justification::centred);

    versionLabel.setText(JucePlugin_VersionString, juce::dontSendNotification);
    versionLabel.setJustificationType(juce::Justification::centredRight);
    versionLabel.setVisible({show_version});

    addAndMakeVisible(gainSlider);
    addAndMakeVisible(gainLabel);
    addAndMakeVisible(versionLabel);

    gainAttachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(
        processor.apvts, "gain_db", gainSlider);

    setSize({int(ui["width"])}, {int(ui["height"])});
}}

void FactoryPluginAudioProcessorEditor::paint(juce::Graphics& g)
{{
    g.fillAll(getLookAndFeel().findColour(juce::ResizableWindow::backgroundColourId));
}}

void FactoryPluginAudioProcessorEditor::resized()
{{
    auto bounds = getLocalBounds().reduced(20);
    auto footer = bounds.removeFromBottom(24);
    versionLabel.setBounds(footer);
    gainLabel.setBounds(bounds.removeFromTop(28));
    gainSlider.setBounds(bounds.reduced(20));
}}
'''

    manifest = {
        "factory_version": FACTORY_VERSION,
        "contract_version": contract["contract_version"],
        "contract_sha256": contract_sha256(contract),
        "plugin_id": plugin["id"],
        "plugin_version": plugin["version"],
        "dsp_template": contract["dsp"]["template"],
        "dsp_source_revision": contract["dsp"]["source_revision"],
        "juce_version": "9.0.2",
        "target_os": contract["target"]["os"],
        "formats": contract["target"]["formats"],
        "status": "GENERATED",
        "release_authority": False,
    }

    (out / "CMakeLists.txt").write_text(cmake, encoding="utf-8")
    (source / "GoldenGainDSP.h").write_text(dsp_core_h, encoding="utf-8")
    (tests / "DspTests.cpp").write_text(dsp_tests_cpp, encoding="utf-8")
    (source / "PluginProcessor.h").write_text(processor_h, encoding="utf-8")
    (source / "PluginProcessor.cpp").write_text(processor_cpp, encoding="utf-8")
    (source / "PluginEditor.h").write_text(editor_h, encoding="utf-8")
    (source / "PluginEditor.cpp").write_text(editor_cpp, encoding="utf-8")
    (out / "plugin_contract.json").write_text(
        json.dumps(contract, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "factory_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out

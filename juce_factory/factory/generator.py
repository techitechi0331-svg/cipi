from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import FACTORY_VERSION
from .contract import contract_sha256, validate_contract


def _cpp_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


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
    source.mkdir(parents=True, exist_ok=True)

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
'''
    processor_h = r'''#pragma once

#include <JuceHeader.h>

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
    juce::SmoothedValue<float, juce::ValueSmoothingTypes::Linear> smoothedGain { 1.0f };

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
        juce::NormalisableRange<float>({float(gain["min"]):.8g}f, {float(gain["max"]):.8g}f, 0.01f),
        {float(gain["default"]):.8g}f,
        "dB"));
    return layout;
}}

void FactoryPluginAudioProcessor::prepareToPlay(double sampleRate, int)
{{
    smoothedGain.reset(sampleRate, 0.02);
    const auto db = apvts.getRawParameterValue("gain_db")->load();
    smoothedGain.setCurrentAndTargetValue(juce::Decibels::decibelsToGain(db));
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
    const auto db = apvts.getRawParameterValue("gain_db")->load();
    smoothedGain.setTargetValue(juce::Decibels::decibelsToGain(db));

    const auto channels = buffer.getNumChannels();
    const auto samples = buffer.getNumSamples();

    for (int sample = 0; sample < samples; ++sample)
    {{
        const float gain = smoothedGain.getNextValue();
        for (int channel = 0; channel < channels; ++channel)
            buffer.getWritePointer(channel)[sample] *= gain;
    }}
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

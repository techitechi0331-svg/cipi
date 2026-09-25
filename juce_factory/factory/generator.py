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
    source.mkdir(parents=True, exist_ok=True)
    tests = out / "Tests"
    tests.mkdir(parents=True, exist_ok=True)

    plugin = contract["plugin"]
    ui = contract["ui"]
    validation = contract["validation"]
    sample_rates = validation.get("sample_rates", [44100, 48000, 88200, 96000])
    block_sizes = validation.get("block_sizes", [32, 64, 128, 257, 512, 1024])
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

    const juce::String getName() const override { return "__PRODUCT_NAME__"; }
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
        juce::NormalisableRange<float>({_cpp_float(gain["min"])}, {_cpp_float(gain["max"])}, 0.01f),
        {_cpp_float(gain["default"])},
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
    processor_h = processor_h.replace("__PRODUCT_NAME__", _cpp_string(plugin["name"]))
    show_version = "true" if ui["show_version"] else "false"
    editor_cpp = f'''#include "PluginEditor.h"

FactoryPluginAudioProcessorEditor::FactoryPluginAudioProcessorEditor(FactoryPluginAudioProcessor& p)
    : juce::AudioProcessorEditor(&p), processor(p)
{{
    gainSlider.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    gainSlider.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 90, 24);
    gainLabel.setText("Gain", juce::dontSendNotification);
    gainLabel.setJustificationType(juce::Justification::centred);

    versionLabel.setText("__PLUGIN_VERSION__", juce::dontSendNotification);
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

    editor_cpp = editor_cpp.replace("__PLUGIN_VERSION__", _cpp_string(plugin["version"]))

    sample_rates_cpp = ", ".join(format(float(rate), ".1f") for rate in sample_rates)
    block_sizes_cpp = ", ".join(str(int(size)) for size in block_sizes)
    validation_cpp = r'''#include "../Source/PluginProcessor.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <string>

namespace
{
int failures = 0;

void require(bool condition, const std::string& label)
{
    if (condition)
    {
        std::cout << "PASS " << label << "\n";
        return;
    }

    ++failures;
    std::cerr << "FAIL " << label << "\n";
}

void setGainDb(FactoryPluginAudioProcessor& processor, float db)
{
    auto* parameter = processor.apvts.getParameter("gain_db");
    if (parameter == nullptr)
    {
        require(false, "gain_db parameter exists");
        return;
    }

    parameter->setValueNotifyingHost(parameter->convertTo0to1(db));
}

bool isFinite(const juce::AudioBuffer<float>& buffer)
{
    for (int channel = 0; channel < buffer.getNumChannels(); ++channel)
        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
            if (!std::isfinite(buffer.getSample(channel, sample)))
                return false;
    return true;
}

float maxAbsError(const juce::AudioBuffer<float>& buffer, float expected)
{
    float result = 0.0f;
    for (int channel = 0; channel < buffer.getNumChannels(); ++channel)
        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
            result = std::max(result, std::abs(buffer.getSample(channel, sample) - expected));
    return result;
}

void fill(juce::AudioBuffer<float>& buffer, float value)
{
    for (int channel = 0; channel < buffer.getNumChannels(); ++channel)
        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
            buffer.setSample(channel, sample, value);
}
}

int main()
{
    juce::ScopedJuceInitialiser_GUI initialiseJuce;

    constexpr std::array<double, __SAMPLE_RATE_COUNT__> sampleRates { __SAMPLE_RATES__ };
    constexpr std::array<int, __BLOCK_SIZE_COUNT__> blockSizes { __BLOCK_SIZES__ };

    {
        FactoryPluginAudioProcessor processor;

        if constexpr (__RUN_LAYOUT__)
        {
            juce::AudioProcessor::BusesLayout mono;
            mono.inputBuses.add(juce::AudioChannelSet::mono());
            mono.outputBuses.add(juce::AudioChannelSet::mono());
            require(processor.isBusesLayoutSupported(mono), "mono layout accepted");

            juce::AudioProcessor::BusesLayout stereo;
            stereo.inputBuses.add(juce::AudioChannelSet::stereo());
            stereo.outputBuses.add(juce::AudioChannelSet::stereo());
            require(processor.isBusesLayoutSupported(stereo), "stereo layout accepted");

            juce::AudioProcessor::BusesLayout mismatch;
            mismatch.inputBuses.add(juce::AudioChannelSet::mono());
            mismatch.outputBuses.add(juce::AudioChannelSet::stereo());
            require(!processor.isBusesLayoutSupported(mismatch), "mismatched layout rejected");
        }

        if constexpr (__RUN_LATENCY__)
            require(processor.getLatencySamples() == 0, "Golden Gain reports zero latency");

        if constexpr (__RUN_STATE__)
        {
            setGainDb(processor, -12.0f);
            juce::MemoryBlock state;
            processor.getStateInformation(state);
            require(state.getSize() > 0, "state serialization produced data");

            setGainDb(processor, 6.0f);
            processor.setStateInformation(state.getData(), static_cast<int>(state.getSize()));
            const auto restored = processor.apvts.getRawParameterValue("gain_db")->load();
            require(std::abs(restored + 12.0f) < 0.001f, "state restore returns exact parameter value");

            const std::array<unsigned char, 8> corruptState { 0, 1, 2, 3, 4, 5, 6, 7 };
            processor.setStateInformation(corruptState.data(), static_cast<int>(corruptState.size()));
            require(std::isfinite(processor.apvts.getRawParameterValue("gain_db")->load()),
                    "corrupt state is ignored safely");
        }
    }

    for (const double sampleRate : sampleRates)
    {
        for (const int blockSize : blockSizes)
        {
            FactoryPluginAudioProcessor processor;
            processor.setRateAndBufferSizeDetails(sampleRate, blockSize);
            processor.prepareToPlay(sampleRate, blockSize);

            juce::MidiBuffer midi;
            juce::AudioBuffer<float> buffer(2, blockSize);

            if constexpr (__RUN_SILENCE__)
            {
                buffer.clear();
                processor.processBlock(buffer, midi);
                require(isFinite(buffer), "silence finite sr=" + std::to_string(static_cast<int>(sampleRate))
                                         + " bs=" + std::to_string(blockSize));
                require(buffer.getMagnitude(0, 0, blockSize) == 0.0f
                        && buffer.getMagnitude(1, 0, blockSize) == 0.0f,
                        "silence remains silent sr=" + std::to_string(static_cast<int>(sampleRate))
                        + " bs=" + std::to_string(blockSize));
            }

            setGainDb(processor, 0.0f);
            fill(buffer, 0.25f);
            processor.processBlock(buffer, midi);
            require(isFinite(buffer) && maxAbsError(buffer, 0.25f) < 0.00001f,
                    "unity gain sr=" + std::to_string(static_cast<int>(sampleRate))
                    + " bs=" + std::to_string(blockSize));

            if constexpr (__RUN_DENORMAL__)
            {
                fill(buffer, 1.0e-39f);
                processor.processBlock(buffer, midi);
                require(isFinite(buffer), "denormal-safe finite output sr="
                                         + std::to_string(static_cast<int>(sampleRate))
                                         + " bs=" + std::to_string(blockSize));
            }

            if constexpr (__RUN_AUTOMATION__)
            {
                bool finiteAutomation = true;
                for (int iteration = 0; iteration < 128; ++iteration)
                {
                    const float gainDb = (iteration % 2 == 0) ? -24.0f : 24.0f;
                    setGainDb(processor, gainDb);
                    fill(buffer, 0.1f);
                    processor.processBlock(buffer, midi);
                    finiteAutomation = finiteAutomation && isFinite(buffer)
                        && buffer.getMagnitude(0, 0, blockSize) < 2.0f
                        && buffer.getMagnitude(1, 0, blockSize) < 2.0f;
                }
                require(finiteAutomation, "automation stress bounded/finite sr="
                                          + std::to_string(static_cast<int>(sampleRate))
                                          + " bs=" + std::to_string(blockSize));
            }

            setGainDb(processor, 6.0f);
            const int settleBlocks = std::max(1, static_cast<int>(std::ceil(sampleRate * 0.05 / blockSize)));
            for (int i = 0; i < settleBlocks; ++i)
            {
                fill(buffer, 0.1f);
                processor.processBlock(buffer, midi);
            }
            const float expected = 0.1f * juce::Decibels::decibelsToGain(6.0f);
            require(std::abs(buffer.getSample(0, blockSize - 1) - expected) < 0.001f,
                    "settled +6 dB gain sr=" + std::to_string(static_cast<int>(sampleRate))
                    + " bs=" + std::to_string(blockSize));

            processor.releaseResources();
        }
    }

    if constexpr (__RUN_BYPASS__)
    {
        FactoryPluginAudioProcessor processor;
        constexpr int blockSize = 257;
        processor.setRateAndBufferSizeDetails(48000.0, blockSize);
        processor.prepareToPlay(48000.0, blockSize);
        juce::AudioBuffer<float> buffer(2, blockSize);
        fill(buffer, 0.123f);
        juce::MidiBuffer midi;
        processor.processBlockBypassed(buffer, midi);
        require(maxAbsError(buffer, 0.123f) < 0.000001f, "default bypass preserves signal");
    }

    std::cout << "FACTORY_VALIDATION_SUMMARY failures=" << failures << "\n";
    return failures == 0 ? 0 : 1;
}
'''
    validation_cpp = validation_cpp.replace("__SAMPLE_RATE_COUNT__", str(len(sample_rates)))
    validation_cpp = validation_cpp.replace("__SAMPLE_RATES__", sample_rates_cpp)
    validation_cpp = validation_cpp.replace("__BLOCK_SIZE_COUNT__", str(len(block_sizes)))
    validation_cpp = validation_cpp.replace("__BLOCK_SIZES__", block_sizes_cpp)
    validation_cpp = validation_cpp.replace("__RUN_LAYOUT__", "true" if validation.get("mono_stereo_layouts", True) else "false")
    validation_cpp = validation_cpp.replace("__RUN_LATENCY__", "true" if validation.get("latency", True) else "false")
    validation_cpp = validation_cpp.replace("__RUN_STATE__", "true" if validation.get("state_restore", True) else "false")
    validation_cpp = validation_cpp.replace("__RUN_SILENCE__", "true" if validation.get("silence", True) else "false")
    validation_cpp = validation_cpp.replace("__RUN_DENORMAL__", "true" if validation.get("denormal", True) else "false")
    validation_cpp = validation_cpp.replace("__RUN_AUTOMATION__", "true" if validation.get("automation", True) else "false")
    validation_cpp = validation_cpp.replace("__RUN_BYPASS__", "true" if validation.get("bypass", True) else "false")

    cmake += f'''

juce_add_console_app({target}FactoryValidation
    PRODUCT_NAME "{_cpp_string(plugin["name"])} Factory Validation"
)

juce_generate_juce_header({target}FactoryValidation)

target_sources({target}FactoryValidation
    PRIVATE
        Tests/FactoryValidation.cpp
        Source/PluginProcessor.cpp
        Source/PluginProcessor.h
        Source/PluginEditor.cpp
        Source/PluginEditor.h
)

target_compile_definitions({target}FactoryValidation
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries({target}FactoryValidation
    PRIVATE
        juce::juce_audio_utils
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
)
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
        "validation_matrix": {
            "sample_rates": sample_rates,
            "block_sizes": block_sizes,
            "state_restore": validation.get("state_restore", True),
            "automation": validation.get("automation", True),
            "silence": validation.get("silence", True),
            "nan_inf": validation.get("nan_inf", True),
            "official_vst3_validator": validation.get("official_vst3_validator", True),
            "latency": validation.get("latency", True),
            "mono_stereo_layouts": validation.get("mono_stereo_layouts", True),
            "denormal": validation.get("denormal", True),
            "bypass": validation.get("bypass", True),
        },
    }

    (out / "CMakeLists.txt").write_text(cmake, encoding="utf-8")
    (source / "PluginProcessor.h").write_text(processor_h, encoding="utf-8")
    (source / "PluginProcessor.cpp").write_text(processor_cpp, encoding="utf-8")
    (source / "PluginEditor.h").write_text(editor_h, encoding="utf-8")
    (source / "PluginEditor.cpp").write_text(editor_cpp, encoding="utf-8")
    (tests / "FactoryValidation.cpp").write_text(validation_cpp, encoding="utf-8")
    (out / "plugin_contract.json").write_text(
        json.dumps(contract, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "factory_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out

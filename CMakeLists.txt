cmake_minimum_required(VERSION 3.24)
project(CIPI VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

option(CIPI_ENABLE_LTO "Enable link-time optimisation for release candidates" OFF)

include(FetchContent)
FetchContent_Declare(
    JUCE
    GIT_REPOSITORY https://github.com/juce-framework/JUCE.git
    GIT_TAG 9.0.2
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(JUCE)

function(cipi_add_plugin TARGET_NAME PRODUCT_NAME PLUGIN_CODE SOURCE_DIR)
    juce_add_plugin(${TARGET_NAME}
        COMPANY_NAME "CIPI Audio"
        BUNDLE_ID "audio.cipi.${TARGET_NAME}"
        PLUGIN_MANUFACTURER_CODE Cipi
        PLUGIN_CODE ${PLUGIN_CODE}
        FORMATS VST3
        PRODUCT_NAME "${PRODUCT_NAME}"
        COPY_PLUGIN_AFTER_BUILD FALSE
        NEEDS_MIDI_INPUT FALSE
        NEEDS_MIDI_OUTPUT FALSE
        IS_MIDI_EFFECT FALSE
        EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    )

    juce_generate_juce_header(${TARGET_NAME})

    target_sources(${TARGET_NAME}
        PRIVATE
            ${SOURCE_DIR}/PluginProcessor.cpp
            ${SOURCE_DIR}/PluginProcessor.h
    )

    target_include_directories(${TARGET_NAME} PRIVATE src)

    target_compile_definitions(${TARGET_NAME}
        PUBLIC
            JUCE_WEB_BROWSER=0
            JUCE_USE_CURL=0
            JUCE_VST3_CAN_REPLACE_VST2=0
    )

    target_link_libraries(${TARGET_NAME}
        PRIVATE
            juce::juce_audio_utils
            juce::juce_dsp
        PUBLIC
            juce::juce_recommended_config_flags
            juce::juce_recommended_warning_flags
    )

    if (CIPI_ENABLE_LTO)
        target_link_libraries(${TARGET_NAME} PUBLIC juce::juce_recommended_lto_flags)
    endif()
endfunction()

cipi_add_plugin(CIPIVoxLevel "CIPI VoxLevel" VxL1 "${CMAKE_CURRENT_SOURCE_DIR}/src/plugins/VoxLevel")
cipi_add_plugin(CIPIAirGuard "CIPI AirGuard" ArG1 "${CMAKE_CURRENT_SOURCE_DIR}/src/plugins/AirGuard")
cipi_add_plugin(CIPIDensity "CIPI Density" Dns1 "${CMAKE_CURRENT_SOURCE_DIR}/src/plugins/Density")


juce_add_console_app(CIPITests
    PRODUCT_NAME "CIPI DSP Tests"
)

juce_generate_juce_header(CIPITests)

target_sources(CIPITests PRIVATE tests/DspTests.cpp)
target_include_directories(CIPITests PRIVATE src)

target_link_libraries(CIPITests
    PRIVATE
        juce::juce_audio_basics
        juce::juce_core
        juce::juce_dsp
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
)

set_target_properties(CIPITests PROPERTIES OUTPUT_NAME "CIPITests")

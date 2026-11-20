cmake_minimum_required(VERSION 3.22)
project(Vocal73ResearchProbe LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Explicit, user-provided checkouts; do not fetch dependencies or write to product repo.
if(NOT DEFINED JUCE_DIR OR NOT EXISTS "${JUCE_DIR}/CMakeLists.txt")
    message(FATAL_ERROR "Set -DJUCE_DIR=/path/to/verified/JUCE-9.0.2")
endif()
if(NOT DEFINED VOCAL73_SOURCE_DIR OR NOT EXISTS "${VOCAL73_SOURCE_DIR}/Vocal73DSP.cpp")
    message(FATAL_ERROR "Set -DVOCAL73_SOURCE_DIR=/path/to/VocalPrepComp/Vocal73Pre/Source")
endif()
add_subdirectory("${JUCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/juce" EXCLUDE_FROM_ALL)
juce_add_console_app(vocal73_probe PRODUCT_NAME "Vocal73 research fixture")
juce_generate_juce_header(vocal73_probe)
target_sources(vocal73_probe PRIVATE
    juce_headless_v02_probe.cpp
    "${VOCAL73_SOURCE_DIR}/Vocal73DSP.cpp"
    "${VOCAL73_SOURCE_DIR}/Vocal73DSP.h")
target_include_directories(vocal73_probe PRIVATE "${VOCAL73_SOURCE_DIR}")
target_compile_definitions(vocal73_probe PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0)
target_link_libraries(vocal73_probe PRIVATE juce::juce_audio_basics juce::juce_dsp juce::juce_core)

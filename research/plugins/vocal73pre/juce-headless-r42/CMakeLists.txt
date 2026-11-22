cmake_minimum_required(VERSION 3.22)
project(Vocal73Headless LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT DEFINED VOCAL73_SOURCE_DIR)
  message(FATAL_ERROR "Pass -DVOCAL73_SOURCE_DIR=<checkout>/Vocal73Pre")
endif()
if(NOT EXISTS "${VOCAL73_SOURCE_DIR}/Source/Vocal73DSP.cpp")
  message(FATAL_ERROR "Vocal73DSP.cpp not found")
endif()
include(FetchContent)
FetchContent_Declare(JUCE GIT_REPOSITORY https://github.com/juce-framework/JUCE.git GIT_TAG 9.0.2 GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(JUCE)
juce_add_console_app(vocal73_headless PRODUCT_NAME "Vocal73 DSP Headless")
juce_generate_juce_header(vocal73_headless)
target_sources(vocal73_headless PRIVATE
  main.cpp
  "${VOCAL73_SOURCE_DIR}/Source/Vocal73DSP.cpp"
  "${VOCAL73_SOURCE_DIR}/Source/Vocal73DSP.h")
target_include_directories(vocal73_headless PRIVATE "${VOCAL73_SOURCE_DIR}/Source")
target_compile_definitions(vocal73_headless PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0)
target_link_libraries(vocal73_headless PRIVATE juce::juce_audio_utils juce::juce_dsp
  juce::juce_recommended_config_flags)

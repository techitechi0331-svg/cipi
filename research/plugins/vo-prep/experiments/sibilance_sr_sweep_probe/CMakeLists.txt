cmake_minimum_required(VERSION 3.22)

project(VoPrepSibilanceSrSweep VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(DEFINED JUCE_SOURCE_DIR)
    add_subdirectory("${JUCE_SOURCE_DIR}" juce)
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

juce_add_console_app(VoPrepSibilanceSrSweep
    PRODUCT_NAME "Vo.Prep Sibilance SR Sweep"
)

juce_generate_juce_header(VoPrepSibilanceSrSweep)

target_sources(VoPrepSibilanceSrSweep PRIVATE
    Main.cpp
)

target_compile_definitions(VoPrepSibilanceSrSweep PRIVATE
    JUCE_PLUGINHOST_VST=0
    JUCE_PLUGINHOST_VST3=1
    JUCE_PLUGINHOST_AU=0
    JUCE_PLUGINHOST_LADSPA=0
    JUCE_PLUGINHOST_LV2=0
    JUCE_PLUGINHOST_ARA=0
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
)

target_link_libraries(VoPrepSibilanceSrSweep PRIVATE
    juce::juce_audio_processors_headless
    juce::juce_audio_basics
    juce::juce_events
    juce::juce_recommended_config_flags
    juce::juce_recommended_warning_flags
)

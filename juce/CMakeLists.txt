# Isengard Plugins - CMake Configuration
# 
# This CMakeLists.txt file configures the build for both Isengard Delay and Isengard Verb
# plugins as AU and VST3 formats for macOS.
#
# Usage:
#   mkdir build
#   cd build
#   cmake .. -GXcode -DCMAKE_BUILD_TYPE=Release
#   cmake --build . --config Release
#
# Copyright (c) 2024 Isengard Audio

cmake_minimum_required(VERSION 3.15)

# Project name
project(IsengardPlugins VERSION 0.1.0 LANGUAGES CXX C)

# ============================================================================
# JUCE Configuration
# ============================================================================

# Find JUCE (must be installed on the system)
find_package(JUCE REQUIRED)

# Enable JUCE modules we need
target_link_libraries(
    juce::juce_core
    juce::juce_audio_basics
    juce::juce_audio_devices
    juce::juce_audio_formats
    juce::juce_audio_processors
    juce::juce_audio_utils
    juce::juce_data_structures
    juce::juce_events
    juce::juce_graphics
    juce::juce_gui_basics
    juce::juce_gui_extra
)

# ============================================================================
# Global Settings
# ============================================================================

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable optimizations
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g")

# macOS specific settings
if(APPLE)
    # Enable Apple Silicon support
    set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64")
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15")
    
    # Add framework search paths
    find_library(AUDIO_UNIT_FRAMEWORK AudioUnit)
    find_library(AUDIO_TOOLBOX_FRAMEWORK AudioToolbox)
    find_library(CORE_AUDIO_FRAMEWORK CoreAudio)
    find_library(CORE_FOUNDATION_FRAMEWORK CoreFoundation)
    find_library(CORE_SERVICES_FRAMEWORK CoreServices)
    
    # Link frameworks for AU
    set(AU_FRAMEWORKS 
        ${AUDIO_UNIT_FRAMEWORK}
        ${AUDIO_TOOLBOX_FRAMEWORK}
        ${CORE_AUDIO_FRAMEWORK}
        ${CORE_FOUNDATION_FRAMEWORK}
        ${CORE_SERVICES_FRAMEWORK}
    )
endif()

# ============================================================================
# Shared DSP Library
# ============================================================================

# Create shared DSP library
add_library(IsengardSharedDSP STATIC
    Shared/Include/Isengard_DSP.h
    Shared/Source/Isengard_DSP.cpp
    Shared/Include/Isengard_FDN.h
    Shared/Source/Isengard_FDN.cpp
)

# Include directories for shared library
target_include_directories(IsengardSharedDSP
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/Shared/Include
        ${JUCE_MODULES_DIR}
)

# Link JUCE to shared library
target_link_libraries(IsengardSharedDSP PRIVATE
    juce::juce_core
    juce::juce_audio_basics
)

# ============================================================================
# Isengard Delay Plugin
# ============================================================================

# Create AU version
add_library(IsengardDelay_AU MODULE
    IsengardDelay/Source/PluginProcessor.h
    IsengardDelay/Source/PluginProcessor.cpp
    IsengardDelay/Source/PluginEditor.h
    IsengardDelay/Source/PluginEditor.cpp
)

# Set AU properties
set_target_properties(IsengardDelay_AU PROPERTIES
    BUNDLE TRUE
    BUNDLE_IDENTIFIER "com.isengard.audio.IsengardDelay.AU"
    MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/IsengardDelay/Info.plist"
    MACOSX_BUNDLE_BINFO "AUPlugIn"
    MACOSX_BUNDLE_CFBUNDLEPACKAGE_TYPE "aubd"
    MACOSX_BUNDLE_CFBUNDLEGETINFOSTRING "Isengard Delay Audio Unit"
    MACOSX_BUNDLE_CFBUNDLEVERSION "0.1.0"
    MACOSX_BUNDLE_CFBUNDLESHORTVERSIONSTRING "0.1"
    MACOSX_BUNDLE_CFBUNDLENAME "Isengard Delay"
    MACOSX_BUNDLE_NSHUMANREADABLECOPYRIGHT "Copyright (c) 2024 Isengard Audio"
)

# Include directories for AU
target_include_directories(IsengardDelay_AU
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/IsengardDelay/Source
        ${CMAKE_CURRENT_SOURCE_DIR}/Shared/Include
        ${JUCE_MODULES_DIR}
)

# Link libraries for AU
target_link_libraries(IsengardDelay_AU PRIVATE
    IsengardSharedDSP
    juce::juce_audio_processors
    juce::juce_gui_basics
    ${AU_FRAMEWORKS}
)

# Install AU
install(TARGETS IsengardDelay_AU
    LIBRARY DESTINATION "/Library/Audio/Plug-Ins/Components"
    BUNDLE DESTINATION "/Library/Audio/Plug-Ins/Components"
)

# Create VST3 version
add_library(IsengardDelay_VST3 MODULE
    IsengardDelay/Source/PluginProcessor.h
    IsengardDelay/Source/PluginProcessor.cpp
    IsengardDelay/Source/PluginEditor.h
    IsengardDelay/Source/PluginEditor.cpp
)

# Set VST3 properties
set_target_properties(IsengardDelay_VST3 PROPERTIES
    BUNDLE TRUE
    BUNDLE_IDENTIFIER "com.isengard.audio.IsengardDelay.VST3"
    MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/IsengardDelay/Info.plist"
)

# Include directories for VST3
target_include_directories(IsengardDelay_VST3
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/IsengardDelay/Source
        ${CMAKE_CURRENT_SOURCE_DIR}/Shared/Include
        ${JUCE_MODULES_DIR}
)

# Link libraries for VST3
target_link_libraries(IsengardDelay_VST3 PRIVATE
    IsengardSharedDSP
    juce::juce_audio_processors
    juce::juce_gui_basics
)

# Install VST3
install(TARGETS IsengardDelay_VST3
    LIBRARY DESTINATION "/Library/Audio/Plug-Ins/VST3"
    BUNDLE DESTINATION "/Library/Audio/Plug-Ins/VST3"
)

# ============================================================================
# Isengard Verb Plugin
# ============================================================================

# Create AU version
add_library(IsengardVerb_AU MODULE
    IsengardVerb/Source/PluginProcessor.h
    IsengardVerb/Source/PluginProcessor.cpp
    IsengardVerb/Source/PluginEditor.h
    IsengardVerb/Source/PluginEditor.cpp
)

# Set AU properties
set_target_properties(IsengardVerb_AU PROPERTIES
    BUNDLE TRUE
    BUNDLE_IDENTIFIER "com.isengard.audio.IsengardVerb.AU"
    MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/IsengardVerb/Info.plist"
    MACOSX_BUNDLE_BINFO "AUPlugIn"
    MACOSX_BUNDLE_CFBUNDLEPACKAGE_TYPE "aubd"
    MACOSX_BUNDLE_CFBUNDLEGETINFOSTRING "Isengard Verb Audio Unit"
    MACOSX_BUNDLE_CFBUNDLEVERSION "0.1.0"
    MACOSX_BUNDLE_CFBUNDLESHORTVERSIONSTRING "0.1"
    MACOSX_BUNDLE_CFBUNDLENAME "Isengard Verb"
    MACOSX_BUNDLE_NSHUMANREADABLECOPYRIGHT "Copyright (c) 2024 Isengard Audio"
)

# Include directories for AU
target_include_directories(IsengardVerb_AU
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/IsengardVerb/Source
        ${CMAKE_CURRENT_SOURCE_DIR}/Shared/Include
        ${JUCE_MODULES_DIR}
)

# Link libraries for AU
target_link_libraries(IsengardVerb_AU PRIVATE
    IsengardSharedDSP
    juce::juce_audio_processors
    juce::juce_gui_basics
    ${AU_FRAMEWORKS}
)

# Install AU
install(TARGETS IsengardVerb_AU
    LIBRARY DESTINATION "/Library/Audio/Plug-Ins/Components"
    BUNDLE DESTINATION "/Library/Audio/Plug-Ins/Components"
)

# Create VST3 version
add_library(IsengardVerb_VST3 MODULE
    IsengardVerb/Source/PluginProcessor.h
    IsengardVerb/Source/PluginProcessor.cpp
    IsengardVerb/Source/PluginEditor.h
    IsengardVerb/Source/PluginEditor.cpp
)

# Set VST3 properties
set_target_properties(IsengardVerb_VST3 PROPERTIES
    BUNDLE TRUE
    BUNDLE_IDENTIFIER "com.isengard.audio.IsengardVerb.VST3"
    MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/IsengardVerb/Info.plist"
)

# Include directories for VST3
target_include_directories(IsengardVerb_VST3
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/IsengardVerb/Source
        ${CMAKE_CURRENT_SOURCE_DIR}/Shared/Include
        ${JUCE_MODULES_DIR}
)

# Link libraries for VST3
target_link_libraries(IsengardVerb_VST3 PRIVATE
    IsengardSharedDSP
    juce::juce_audio_processors
    juce::juce_gui_basics
)

# Install VST3
install(TARGETS IsengardVerb_VST3
    LIBRARY DESTINATION "/Library/Audio/Plug-Ins/VST3"
    BUNDLE DESTINATION "/Library/Audio/Plug-Ins/VST3"
)

# ============================================================================
# Info.plist files for AU plugins
# ============================================================================

# Use the actual Info.plist files we created
# IsengardDelay Info.plist is at: ${CMAKE_CURRENT_SOURCE_DIR}/IsengardDelay/Info.plist
# IsengardVerb Info.plist is at: ${CMAKE_CURRENT_SOURCE_DIR}/IsengardVerb/Info.plist

# Copy Info.plist files to build directory
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/IsengardDelay/Info.plist"
    "${CMAKE_CURRENT_BINARY_DIR}/IsengardDelay/Info.plist"
    COPYONLY
)

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/IsengardVerb/Info.plist"
    "${CMAKE_CURRENT_BINARY_DIR}/IsengardVerb/Info.plist"
    COPYONLY
)

# ============================================================================
# Build All Targets
# ============================================================================

# Message
message(STATUS "Isengard Plugins CMake Configuration Complete")
message(STATUS "Targets:")
message(STATUS "  - IsengardDelay_AU (Audio Unit)")
message(STATUS "  - IsengardDelay_VST3 (VST3)")
message(STATUS "  - IsengardVerb_AU (Audio Unit)")
message(STATUS "  - IsengardVerb_VST3 (VST3)")

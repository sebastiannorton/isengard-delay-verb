# Isengard Plugins - JUCE Project Structure

This directory contains the JUCE project files for building **Isengard Delay** and **Isengard Verb** as AU and VST3 plugins for macOS.

## Project Structure

```
juce/
├── CMakeLists.txt              - CMake build configuration
├── Templates/
│   └── Info.plist.in          - Template for AU Info.plist
├── Shared/
│   ├── Include/
│   │   ├── Isengard_DSP.h     - Shared DSP header (C++)
│   │   └── Isengard_FDN.h     - FDN reverb header (C++)
│   └── Source/
│       ├── Isengard_DSP.cpp   - Shared DSP implementation
│       └── Isengard_FDN.cpp   - FDN reverb implementation
├── IsengardDelay/
│   ├── Info.plist              - Audio Unit Info.plist
│   └── Source/
│       ├── PluginProcessor.h  - AU/VST3 processor header
│       ├── PluginProcessor.cpp- AU/VST3 processor implementation
│       ├── PluginEditor.h     - Plugin editor header
│       └── PluginEditor.cpp   - Plugin editor implementation
└── IsengardVerb/
    ├── Info.plist              - Audio Unit Info.plist
    └── Source/
        ├── PluginProcessor.h  - AU/VST3 processor header
        ├── PluginProcessor.cpp- AU/VST3 processor implementation
        ├── PluginEditor.h     - Plugin editor header
        └── PluginEditor.cpp   - Plugin editor implementation
```

## Building the Plugins

### Prerequisites

1. **JUCE Framework** (version 6.1 or later)
   - Download from: https://juce.com/get-juce/
   - Set up JUCE module path

2. **Xcode** (for macOS builds)
   - Install from Mac App Store
   - Command line tools: `xcode-select --install`

3. **CMake** (optional, for CMake builds)
   - Install from: https://cmake.org/download/

### Option 1: Using JUCE Projucer (Recommended)

1. Open the Projucer
2. Click "Open Existing Project" and select the juce directory
3. Configure the project:
   - Set JUCE module path
   - Select "Xcode (Mac OS X)" as the IDE
   - Enable "Audio Unit" and "VST3" formats
   - Set architectures to "x86_64 + arm64" for universal builds
4. Save and open in Xcode
5. Build the project

### Option 2: Using CMake

```bash
# Create build directory
mkdir build
cd build

# Configure with CMake
cmake .. -GXcode \
    -DCMAKE_BUILD_TYPE=Release \
    -DJUCE_MODULES_DIR=/path/to/JUCE/modules

# Build all targets
cmake --build . --config Release

# Or build specific targets
cmake --build . --config Release --target IsengardDelay_AU
cmake --build . --config Release --target IsengardDelay_VST3
cmake --build . --config Release --target IsengardVerb_AU
cmake --build . --config Release --target IsengardVerb_VST3
```

### Option 3: Manual Xcode Project

1. Create a new Xcode project
2. Add all source files from the `juce/` directory
3. Add JUCE as a dependency
4. Configure build settings:
   - C++ Language Standard: C++17
   - Architectures: arm64 x86_64
   - Deployment Target: macOS 10.15
5. Add required frameworks for AU:
   - AudioUnit.framework
   - AudioToolbox.framework
   - CoreAudio.framework
   - CoreFoundation.framework
   - CoreServices.framework

## Plugin Installation

After building, the plugins will be installed to:

### Audio Unit (AU)
- `/Library/Audio/Plug-Ins/Components/IsengardDelay.component`
- `/Library/Audio/Plug-Ins/Components/IsengardVerb.component`

### VST3
- `/Library/Audio/Plug-Ins/VST3/IsengardDelay.vst3`
- `/Library/Audio/Plug-Ins/VST3/IsengardVerb.vst3`

## DSP Architecture

The plugins use the following DSP architecture:

### Isengard Delay
- **Modes:** Tape, HiFi, BBD, Digital, Ghost, Pitch, RevPitch
- **Styles:** Single, Dual, Ratio, PingPong, Quad
- **Features:** Wow/Flutter modulation, tape saturation, bit crushing, frequency shifting, pitch shifting, reverse delay

### Isengard Verb
- **Modes:** 22 modes (1972-1995, NOW1, NOW2)
- **Colors:** 1970s, 1980s, Now
- **Features:** FDN reverb, early reflections, modulation matrix, color system

### Shared Components
- DelayLine with cubic interpolation
- OnePoleFilter (lowpass/highpass)
- BiquadFilter (multiple types)
- CombFilter
- AllpassFilter
- LFO (multiple waveforms)
- SmoothedParameter
- ParameterSystem

## File Descriptions

### Shared DSP Headers

| File | Description |
|------|-------------|
| `Isengard_DSP.h` | Core DSP components: DelayLine, filters, LFO, parameter smoothing |
| `Isengard_FDN.h` | FDN reverb: CombFilter, AllpassFilter, FDNReverb, EarlyReflections, ModulationMatrix, ColorSystem |

### Plugin Processors

| File | Description |
|------|-------------|
| `PluginProcessor.h` | AudioProcessor subclass with parameter definitions |
| `PluginProcessor.cpp` | Audio processing implementation |

### Plugin Editors

| File | Description |
|------|-------------|
| `PluginEditor.h` | AudioProcessorEditor subclass |
| `PluginEditor.cpp` | UI implementation with controls |

## Parameter List

### Isengard Delay Parameters

| ID | Name | Type | Range | Default |
|----|------|------|-------|---------|
| mode | Mode | Choice | 0-6 | 0 (Tape) |
| style | Style | Choice | 0-4 | 0 (Single) |
| mix | Mix | Float | 0-1 | 0.5 |
| feedback | Feedback | Float | 0-0.99 | 0.5 |
| delay_time_ms | Delay Time | Float | 1-5000 | 500 |
| delay_time_l_ms | Delay Time L | Float | 1-5000 | 500 |
| delay_time_r_ms | Delay Time R | Float | 1-5000 | 500 |
| ratio | Ratio | Float | 0-1 | 0.5 |
| spread | Spread | Float | 0-1 | 0.5 |
| mod_rate | Mod Rate | Float | 0.1-10 | 0.5 |
| mod_depth | Mod Depth | Float | 0-1 | 0.1 |
| age | Age | Float | 0-1 | 0 |
| drive | Drive | Float | 0-1 | 0 |
| diffusion | Diffusion | Float | 0-1 | 0.5 |
| diffusion_size | Diffusion Size | Float | 0-1 | 0.5 |
| eq_high | EQ High | Float | 100-20000 | 10000 |
| eq_low | EQ Low | Float | 20-1000 | 200 |
| era | Era | Float | 0-1 | 0.5 |
| ducking | Ducking | Float | 0-1 | 0 |
| pitch_shift | Pitch Shift | Float | -12-12 | 0 |
| pitch_detune | Pitch Detune | Float | -12-12 | 0 |
| frequency_shift | Freq Shift | Float | -1-1 | 0 |

### Isengard Verb Parameters

| ID | Name | Type | Range | Default |
|----|------|------|-------|---------|
| mode | Mode | Choice | 0-21 | 6 (1978) |
| color | Color | Choice | 0-2 | 1 (1980s) |
| mix | Mix | Float | 0-1 | 0.5 |
| decay | Decay | Float | 0-1 | 0.5 |
| size | Size | Float | 0-1 | 0.5 |
| damping | Damping | Float | 0-1 | 0.5 |
| damping_freq | Damping Freq | Float | 100-20000 | 10000 |
| diffusion | Diffusion | Float | 0-1 | 0.5 |
| mod_rate | Mod Rate | Float | 0.1-10 | 0.5 |
| mod_depth | Mod Depth | Float | 0-1 | 0.1 |
| pre_delay | Pre-Delay | Float | 0-200 | 50 |
| early_level | Early Level | Float | 0-1 | 0.5 |
| width | Width | Float | 0-1 | 0.5 |
| high_cut | High Cut | Float | 100-20000 | 10000 |
| low_cut | Low Cut | Float | 20-1000 | 200 |
| attack | Attack | Float | 0-1 | 0 |
| bass_mult | Bass Mult | Float | 0-2 | 1 |
| bass_xover | Bass Xover | Float | 20-1000 | 200 |

## Preset Management

Both plugins support preset management with factory presets stored in JSON format.

## Next Steps

1. **Complete C++ Port:** Finish porting all Python DSP code to C++
2. **Create Mode Implementations:** Implement all 7 delay modes and 22 verb modes in C++
3. **Test in DAW:** Load plugins in Logic Pro, Ableton Live, etc.
4. **Fine-tune DSP:** Compare with reference plugins and adjust parameters
5. **Design UI:** Apply Living Compass 12 principles to the plugin interface

## Notes

- This is a work in progress. The C++ code provides the framework, but the actual mode implementations need to be completed.
- The Python prototype (src/ directory) contains the complete DSP implementation and can be used as a reference.
- The JUCE project structure is set up for macOS with both AU and VST3 formats.

## License

Copyright (c) 2024 Isengard Audio

All source code is provided for educational and development purposes.

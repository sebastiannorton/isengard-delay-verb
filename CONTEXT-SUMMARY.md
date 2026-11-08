# Isengard Project - Condensed Context

## Objective
Develop **Isengard Delay** and **Isengard Verb** - two independent macOS audio plugins (AU/VST3) inspired by ValhallaDelay and ValhallaVintageVerb.

## Status: Phase E (JUCE Implementation) - COMPLETED

### Completed
- **Environment:** Python 3.12, numpy, scipy, soundfile, REA v6.8.0
- **Research:** 99 evidence entries, 2 DSP specs, 2 documentation files
- **Test Framework:** Signal generators, analysis tools, 114 test configs
- **Delay DSP:** 7 modes + 5 styles + unified DelayProcessor (Python)
- **Verb DSP:** 22 modes + color system + early reflections + modulation + unified VerbProcessor (Python)
- **Parameter Smoothing:** Integrated into both processors
- **Preset Management:** System with factory presets
- **JUCE Structure:** Complete C++ project structure with all plugin files

### Current Focus
- All JUCE plugin files created (processors, editors, Info.plist)
- Shared DSP headers/implementations in C++
- CMakeLists.txt configured for 4 targets (AU + VST3 for both plugins)

### Key Files

**JUCE Structure:**
- juce/CMakeLists.txt - Build configuration
- juce/README.md - Build instructions
- juce/Templates/Info.plist.in - AU template
- juce/Shared/Include/Isengard_DSP.h - DelayLine, filters, LFO, smoothing
- juce/Shared/Include/Isengard_FDN.h - FDN, EarlyReflections, Modulation, Color
- juce/Shared/Source/Isengard_DSP.cpp - Implementations
- juce/Shared/Source/Isengard_FDN.cpp - Implementations
- juce/IsengardDelay/ - Complete plugin
- juce/IsengardVerb/ - Complete plugin

**Python DSP (Reference):**
- src/isengard_delay/ - 7 modes + 5 styles
- src/isengard_verb/ - 22 modes + color system
- src/isengard_shared/ - Presets, delay line, filters, params

### Plugin Parameters

**Isengard Delay (20 params):**
- Mode (7), Style (5), Mix, Feedback
- Delay Time (L/R/Combined), Ratio, Spread
- Mod Rate, Mod Depth
- Age, Drive, Diffusion, Diffusion Size
- EQ High, EQ Low, Era, Ducking
- Pitch Shift, Pitch Detune, Frequency Shift

**Isengard Verb (17 params):**
- Mode (22), Color (3), Mix
- Decay, Size, Pre-Delay, Attack
- Bass Mult, Bass Xover, High Cut
- Damping, Damping Freq
- Mod Rate, Mod Depth
- Width, Early/Late Balance

### DSP Architecture

**Delay:**
- Wow/Flutter modulation (Tape)
- Bit crushing (Digital)
- BBD compander + noise tracking
- Frequency shifting (Ghost)
- Pitch shifting in feedback (Pitch, RevPitch)
- 8 cascaded allpass filters (diffusion)

**Verb:**
- FDN reverb (4 combs + 2 allpasses)
- Orthogonal feedback matrix
- Mode-specific early reflections
- Per-filter modulation matrix
- Color system (1970s/1980s/Now)

### Export
- **File:** `isengard-project-export.zip` (605KB)
- **Contains:** All project files (docs, research, src, tests, juce)

### Next Steps
1. Port Python DSP modes to C++ (7 delay + 22 verb modes)
2. Complete parameter attachment system
3. Implement UI with 12-principles design
4. Test builds with JUCE
5. Verify plugin functionality in DAW
6. Finalize preset system

### Test Results
```
VerbProcessor (All 22 modes): IR peaks 0.5146-0.5425
DelayProcessor (All 7 modes): IR peaks 0.4696-0.5000
```
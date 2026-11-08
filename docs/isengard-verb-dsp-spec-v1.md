# Isengard Verb - DSP Implementation Specification v1.0

**Status:** Draft  
**Date:** 2024-11-07  
**Phase:** B -> C Transition  
**Evidence Base:** E032-E033 (VERIFIED) + Official Documentation

---

## 1. Executive Summary

Independent algorithmic reverb processor inspired by ValhallaVintageVerb. Based on VERIFIED documentation evidence.

**22 Modes:** Categorized as Dirty, Smooth, Chaotic, Palace  
**3 Colors:** 1970s, 1980s, Now  
**Architecture:** Feedback Delay Network (FDN) with allpass/comb filters, modulation, and diffusion

---

## 2. Architecture Overview

### Design Principles

1. **Modular FDN Architecture:** Configurable network of delay lines, allpass filters, and feedback matrices
2. **Mode-Specific Configurations:** Each mode uses different network topology and parameters
3. **Color System:** Global spectral and temporal characteristics
4. **No Dynamic Allocation:** All buffers pre-allocated
5. **Sample Rate Independent:** Normalized processing
6. **Tail Preservation:** State maintained across host blocks

### Class Hierarchy

```
ReverbProcessor
├── ParameterSystem (SmoothedParameter, ParameterBuffer)
├── InputProcessing (Pre-delay, Input Filter, Ducking)
├── EarlyReflections
│   ├── ERGenerator (mode-specific)
│   └── ERFilter
├── LateReverb
│   ├── FDNNetwork (configurable)
│   │   ├── CombFilter (4-8 per mode)
│   │   ├── AllpassFilter (4-8 per mode)
│   │   └── FeedbackMatrix
│   ├── DiffusionNetwork
│   └── ModulationSystem
├── OutputProcessing (Output Filter, EQ, Mix)
└── ModeManager (22 mode configurations)
```

---

## 3. Signal Flow

### Global Path

```
Input (L/R)
  → InputProcessing (Pre-delay, Input Filter)
  → EarlyReflections
  → LateReverb (FDN Network)
  → DiffusionNetwork
  → OutputProcessing (Output Filter, EQ, Mix)
  → Output (L/R)
```

### Mode-Specific Path

Each mode configures:
- Early reflection pattern
- FDN network topology
- Comb filter delays and feedback
- Allpass filter parameters
- Feedback matrix coefficients
- Modulation characteristics

---

## 4. Core Components

### 4.1 Delay Line

Same implementation as Isengard Delay (see isengard-delay-dsp-spec-v1.md)

```cpp
class DelayLine {
    // Same as delay plugin
};
```

### 4.2 Comb Filter

**Purpose:** Creates dense echo patterns in FDN

```cpp
class CombFilter {
public:
    CombFilter(float delayMs, float feedback);
    void setDelay(float delayMs);
    void setFeedback(float fb); // -0.99 to +0.99
    float process(float input);
private:
    DelayLine delay;
    float feedback;
};
```

**Characteristics:**
- Delay times: Typically 10-100ms (mode-dependent)
- Feedback: Positive or negative (creates different characteristics)
- Lowpass filtering in feedback path (damping)

### 4.3 Allpass Filter

**Purpose:** Adds diffusion and density to the reverb tail

```cpp
class AllpassFilter {
public:
    AllpassFilter(float delayMs, float feedback);
    void setDelay(float delayMs);
    void setFeedback(float fb); // 0.0-0.99
    float process(float input);
private:
    DelayLine delay;
    float feedback;
};
```

**Characteristics:**
- Delay times: Typically 1-10ms
- Feedback: 0.5-0.99 (higher = more diffusion)

### 4.4 Feedback Matrix

**Purpose:** Routes signals between comb/allpass filters in FDN

```cpp
class FeedbackMatrix {
public:
    FeedbackMatrix(int size);
    void setCoefficient(int row, int col, float value);
    void processBlock(float** inputs, float** outputs, int numChannels, int numSamples);
private:
    std::vector<std::vector<float>> matrix;
};
```

**Characteristics:**
- Orthogonal or Householder matrices for stability
- Mode-specific configurations
- Controls energy distribution in FDN

### 4.5 FDN Network

**Purpose:** Core late reverb generator

```cpp
class FDNNetwork {
public:
    FDNNetwork(int numCombs, int numAllpasses);
    void configure(const FDNConfig& config);
    void setSampleRate(float sr);
    void processBlock(float* inputL, float* inputR,
                      float* outputL, float* outputR,
                      int numSamples);
private:
    std::vector<CombFilter> combs;
    std::vector<AllpassFilter> allpasses;
    FeedbackMatrix matrix;
    
    // Mode-specific configuration
    void configureForMode(ReverbMode mode);
};
```

---

## 5. Mode Implementations

### Mode Categories (E032)

Based on official documentation, ValhallaVintageVerb has **22 modes** organized into categories:

1. **Dirty Modes:** Vintage, gritty character
2. **Smooth Modes:** Clean, polished character
3. **Chaotic Modes:** Random, unpredictable character
4. **Palace Modes:** Large, spacious character

### Mode List with Characteristics

| Mode | Category | Characteristics | Inspired By |
|------|----------|-----------------|-------------|
| 1972 | Dirty | Early digital, grainy | Lexicon 224 |
| 1974 | Dirty | Vintage plate | EMT 140 |
| 1975 | Dirty | Non-linear | Eventide H949 |
| 1976 | Dirty | Tape delay verb | - |
| 1977 | Dirty | Gated reverb | - |
| 1978 | Dirty | Reverse | - |
| 1979 | Dirty | Flanged | - |
| 1980 | Smooth | Clean digital | Lexicon 224 |
| 1981 | Smooth | Bright hall | - |
| 1982 | Smooth | Warm hall | - |
| 1983 | Smooth | Plate | EMT 140 |
| 1984 | Smooth | Room | - |
| 1985 | Smooth | Chamber | - |
| 1986 | Smooth | Cathedral | - |
| 1987 | Chaotic | Random | - |
| 1988 | Chaotic | Shimmer | - |
| 1989 | Chaotic | Freeze | - |
| 1990 | Chaotic | Modulated | - |
| Now1 | Palace | Modern hall | - |
| Now2 | Palace | Modern plate | - |
| Now3 | Palace | Modern room | - |

### Mode Configuration Structure

```cpp
struct FDNConfig {
    // Comb filters
    std::vector<float> combDelaysMs;    // Delay times for each comb
    std::vector<float> combFeedbacks;   // Feedback for each comb
    std::vector<float> combDampings;    // Damping frequency for each comb
    
    // Allpass filters
    std::vector<float> allpassDelaysMs; // Delay times for each allpass
    std::vector<float> allpassFeedbacks; // Feedback for each allpass
    
    // Feedback matrix
    std::vector<std::vector<float>> matrix;
    
    // Modulation
    float modRateHz;
    float modDepth;
    ModulationType modType;
    
    // Early reflections
    bool useEarlyReflections;
    ERConfig erConfig;
};
```

### Mode-Specific Configurations

#### Example: 1972 Mode (Dirty)

```cpp
FDNConfig create1972ModeConfig() {
    FDNConfig config;
    
    // 4 comb filters with non-linear characteristics
    config.combDelaysMs = {47.3f, 59.2f, 71.1f, 83.4f};
    config.combFeedbacks = {0.82f, 0.78f, 0.74f, 0.70f};
    config.combDampings = {5000.0f, 4000.0f, 3000.0f, 2500.0f};
    
    // 4 allpass filters for diffusion
    config.allpassDelaysMs = {4.7f, 3.1f, 2.3f, 1.7f};
    config.allpassFeedbacks = {0.7f, 0.7f, 0.7f, 0.7f};
    
    // Feedback matrix (simplified 4x4)
    config.matrix = {
        {0.0f, 1.0f, 0.0f, 0.0f},
        {0.0f, 0.0f, 1.0f, 0.0f},
        {0.0f, 0.0f, 0.0f, 1.0f},
        {1.0f, 0.0f, 0.0f, 0.0f}
    };
    
    // Modulation: subtle random modulation
    config.modRateHz = 0.3f;
    config.modDepth = 0.005f;
    config.modType = ModulationType::Random;
    
    // Early reflections: short, dense
    config.useEarlyReflections = true;
    config.erConfig = createShortDenseERConfig();
    
    return config;
}
```

#### Example: 1980 Mode (Smooth)

```cpp
FDNConfig create1980ModeConfig() {
    FDNConfig config;
    
    // 8 comb filters for dense reverb
    config.combDelaysMs = {29.3f, 37.1f, 43.7f, 51.2f, 
                           59.8f, 67.3f, 75.1f, 82.7f};
    config.combFeedbacks = {0.85f, 0.82f, 0.79f, 0.76f,
                            0.73f, 0.70f, 0.67f, 0.64f};
    config.combDampings = {6000.0f, 5500.0f, 5000.0f, 4500.0f,
                           4000.0f, 3500.0f, 3000.0f, 2500.0f};
    
    // 4 allpass filters
    config.allpassDelaysMs = {5.3f, 4.1f, 3.3f, 2.7f};
    config.allpassFeedbacks = {0.6f, 0.6f, 0.6f, 0.6f};
    
    // More complex feedback matrix
    config.matrix = createOrthogonalMatrix(8);
    
    // Modulation: gentle sine modulation
    config.modRateHz = 0.5f;
    config.modDepth = 0.003f;
    config.modType = ModulationType::Sine;
    
    // Early reflections: medium, natural
    config.useEarlyReflections = true;
    config.erConfig = createNaturalERConfig();
    
    return config;
}
```

#### Example: 1987 Mode (Chaotic)

```cpp
FDNConfig create1987ModeConfig() {
    FDNConfig config;
    
    // Comb filters with random modulation
    config.combDelaysMs = {31.7f, 41.3f, 53.9f, 65.2f};
    config.combFeedbacks = {0.80f, 0.75f, 0.70f, 0.65f};
    config.combDampings = {5000.0f, 4000.0f, 3000.0f, 2000.0f};
    
    // Allpass filters
    config.allpassDelaysMs = {6.1f, 4.7f, 3.5f, 2.3f};
    config.allpassFeedbacks = {0.75f, 0.75f, 0.75f, 0.75f};
    
    // Feedback matrix with random variations
    config.matrix = createRandomOrthogonalMatrix(4, 0.1f); // 10% randomness
    
    // Modulation: deep random modulation
    config.modRateHz = 1.2f;
    config.modDepth = 0.02f;
    config.modType = ModulationType::Random;
    
    // Early reflections: randomized
    config.useEarlyReflections = true;
    config.erConfig = createRandomizedERConfig();
    
    return config;
}
```

### Mode Manager

```cpp
class ModeManager {
public:
    enum ReverbMode {
        Mode_1972, Mode_1974, Mode_1975, Mode_1976, Mode_1977, Mode_1978, Mode_1979,
        Mode_1980, Mode_1981, Mode_1982, Mode_1983, Mode_1984, Mode_1985, Mode_1986,
        Mode_1987, Mode_1988, Mode_1989, Mode_1990,
        Mode_Now1, Mode_Now2, Mode_Now3
    };
    
    enum ColorMode { Color_1970s, Color_1980s, Color_Now };
    
    ModeManager();
    void setMode(ReverbMode mode);
    void setColor(ColorMode color);
    FDNConfig getCurrentConfig() const;
    
private:
    ReverbMode currentMode;
    ColorMode currentColor;
    std::vector<FDNConfig> modeConfigs;
    std::vector<ColorConfig> colorConfigs;
    
    void applyColorModifications(FDNConfig& config) const;
};
```

---

## 6. Color System (E033)

### Color Characteristics

| Color | Characteristics | Spectral Effect | Temporal Effect |
|-------|----------------|-----------------|-----------------|
| 1970s | Vintage, warm | Lowpass filtering | Longer decay, slower attack |
| 1980s | Balanced | Flat frequency response | Medium decay, natural attack |
| Now | Modern, bright | Highpass filtering | Shorter decay, faster attack |

### Color Implementation

```cpp
struct ColorConfig {
    // Spectral modifications
    float lowCutHz;      // Highpass cutoff
    float highCutHz;     // Lowpass cutoff
    float damping;       // Overall damping
    
    // Temporal modifications
    float decayScale;    // Scale factor for decay times
    float attackScale;   // Scale factor for attack times
    
    // Modulation modifications
    float modRateScale;  // Scale factor for modulation rates
    float modDepthScale; // Scale factor for modulation depths
};

class ColorSystem {
public:
    ColorSystem();
    void setColor(ColorMode color);
    void applyToConfig(FDNConfig& config) const;
    
private:
    ColorMode currentColor;
    std::vector<ColorConfig> colorConfigs;
};
```

### Color Configurations

```cpp
ColorConfig create1970sColor() {
    ColorConfig config;
    config.lowCutHz = 20.0f;      // No highpass
    config.highCutHz = 8000.0f;   // Warm lowpass
    config.damping = 0.9f;        // More damping
    config.decayScale = 1.2f;     // Longer decay
    config.attackScale = 0.8f;    // Slower attack
    config.modRateScale = 0.8f;   // Slower modulation
    config.modDepthScale = 0.9f;   // Less modulation depth
    return config;
}

ColorConfig create1980sColor() {
    ColorConfig config;
    config.lowCutHz = 20.0f;      // No highpass
    config.highCutHz = 16000.0f;  // Neutral
    config.damping = 1.0f;        // Neutral damping
    config.decayScale = 1.0f;     // Neutral decay
    config.attackScale = 1.0f;    // Neutral attack
    config.modRateScale = 1.0f;   // Neutral modulation
    config.modDepthScale = 1.0f;   // Neutral modulation depth
    return config;
}

ColorConfig createNowColor() {
    ColorConfig config;
    config.lowCutHz = 100.0f;     // Highpass for brightness
    config.highCutHz = 20000.0f;  // No lowpass
    config.damping = 1.1f;        // Less damping
    config.decayScale = 0.8f;     // Shorter decay
    config.attackScale = 1.2f;    // Faster attack
    config.modRateScale = 1.2f;   // Faster modulation
    config.modDepthScale = 1.1f;   // More modulation depth
    return config;
}
```

---

## 7. Early Reflections

### ER Generator

```cpp
class ERGenerator {
public:
    ERGenerator();
    void setConfig(const ERConfig& config);
    void setSampleRate(float sr);
    void processBlock(float* inputL, float* inputR,
                      float* outputL, float* outputR,
                      int numSamples);
private:
    ERConfig config;
    std::vector<DelayLine> delayLines;
    std::vector<float> tapGains;
    
    void generateTaps();
};
```

### ER Configuration

```cpp
struct ERConfig {
    // Tap configuration
    std::vector<float> tapDelaysMs;  // Delay times for each tap
    std::vector<float> tapGains;     // Gain for each tap
    std::vector<int> tapChannels;    // Output channel for each tap (0=L, 1=R)
    
    // Overall characteristics
    float density;       // 0-1, tap density
    float spread;        // 0-1, stereo spread
    float preDelayMs;    // 0-200ms, pre-delay time
    
    // Filtering
    float lowCutHz;      // Highpass cutoff
    float highCutHz;     // Lowpass cutoff
};
```

### Mode-Specific ER Configurations

#### Short Dense (for Dirty modes)

```cpp
ERConfig createShortDenseERConfig() {
    ERConfig config;
    config.preDelayMs = 20.0f;
    config.density = 0.9f;
    config.spread = 0.8f;
    config.lowCutHz = 200.0f;
    config.highCutHz = 10000.0f;
    
    // Generate taps
    config.tapDelaysMs = {5.0f, 7.0f, 9.0f, 11.0f, 13.0f, 15.0f, 17.0f, 19.0f};
    config.tapGains = {0.8f, 0.7f, 0.6f, 0.5f, 0.4f, 0.3f, 0.2f, 0.1f};
    config.tapChannels = {0, 1, 0, 1, 0, 1, 0, 1}; // Alternate L/R
    
    return config;
}
```

#### Natural (for Smooth modes)

```cpp
ERConfig createNaturalERConfig() {
    ERConfig config;
    config.preDelayMs = 60.0f;
    config.density = 0.7f;
    config.spread = 0.9f;
    config.lowCutHz = 100.0f;
    config.highCutHz = 12000.0f;
    
    // Generate taps with more natural spacing
    config.tapDelaysMs = {10.0f, 20.0f, 30.0f, 40.0f, 50.0f, 60.0f, 70.0f, 80.0f};
    config.tapGains = {0.7f, 0.6f, 0.5f, 0.4f, 0.3f, 0.2f, 0.15f, 0.1f};
    config.tapChannels = {0, 1, 1, 0, 0, 1, 1, 0}; // Cross pattern
    
    return config;
}
```

#### Randomized (for Chaotic modes)

```cpp
ERConfig createRandomizedERConfig() {
    ERConfig config;
    config.preDelayMs = 40.0f;
    config.density = 0.8f;
    config.spread = 1.0f;
    config.lowCutHz = 50.0f;
    config.highCutHz = 15000.0f;
    
    // Random tap configuration (generated at runtime)
    // This would be regenerated periodically for true randomization
    config.tapDelaysMs = generateRandomTaps(8, 5.0f, 100.0f);
    config.tapGains = generateRandomGains(8, 0.1f, 0.8f);
    config.tapChannels = generateRandomChannels(8);
    
    return config;
}
```

---

## 8. Modulation System

### Modulation Architecture

```cpp
class ModulationSystem {
public:
    enum ModulationType { None, Sine, Triangle, Random, SampleHold };
    
    ModulationSystem();
    void setConfig(const ModulationConfig& config);
    void setSampleRate(float sr);
    float getModulationValue(int voice) const;
    void processBlock(int numSamples);
private:
    ModulationConfig config;
    std::vector<LFO> lfos;
    std::vector<float> randomValues;
    int currentSample;
};
```

### Modulation Configuration

```cpp
struct ModulationConfig {
    ModulationType type;
    float rateHz;
    float depth;
    float phase; // For deterministic behavior
    
    // For multi-voice modulation (one per comb/allpass)
    bool perVoice;
    float voiceSpread; // Spread between voices
};
```

### Modulation Application

Modulation can be applied to:
1. **Comb filter delays:** Creates pitch modulation (chorus effect)
2. **Comb filter feedback:** Creates amplitude modulation
3. **Allpass filter delays:** Creates phase modulation
4. **Feedback matrix:** Creates time-varying routing

```cpp
// Example: Applying modulation to comb filter delay
void applyModulationToComb(CombFilter& comb, const ModulationConfig& mod, int voiceIndex) {
    float modValue = modulationSystem.getModulationValue(voiceIndex);
    float delayMod = mod.depth * modValue;
    float modulatedDelay = comb.getDelay() * (1.0f + delayMod);
    comb.setDelay(modulatedDelay);
}
```

---

## 9. Parameter System

### Parameter Structure

```cpp
struct ReverbParameters {
    // Global
    float mix;           // 0-1, linear
    float predelay;      // 0-200ms, logarithmic
    float decay;         // 0.1-20s, logarithmic
    float size;          // 0-1, linear (scales all delays)
    float attack;        // 0-1, linear
    
    // Frequency
    float bassMult;      // 0.1-2.0, linear (low-frequency multiplier)
    float bassXover;     // 20-1000Hz, logarithmic
    float highCut;       // 200-20000Hz, logarithmic
    float damping;       // 0-1, linear
    float dampingFreq;   // 20-20000Hz, logarithmic
    
    // Modulation
    float modRate;       // 0.01-20Hz, logarithmic
    float modDepth;      // 0-1, linear
    
    // Stereo
    float earlyLate;     // 0-1, linear (early/late balance)
    float width;         // 0-1, linear
    
    // Mode/Color
    int mode;            // 0-21 (22 modes)
    int color;           // 0-2 (1970s, 1980s, Now)
    
    // Other
    float ducking;       // 0-1, linear
};
```

### Parameter Smoothing

Same smoothing system as Isengard Delay (see isengard-delay-dsp-spec-v1.md)

**Smoothing Times:**
- Mix, Early/Late, Width: 50ms
- Predelay, Decay, Size: 100ms
- Frequency parameters: 100ms
- Modulation: 50ms
- Mode/Color: Instant (but with crossfade)

### Mode/Color Transition

```cpp
class ModeTransition {
public:
    void setTargetMode(int mode);
    void setTargetColor(int color);
    void processBlock(int numSamples);
    float getCrossfadeFactor() const; // 0-1, 0=old mode, 1=new mode
private:
    int currentMode, targetMode;
    int currentColor, targetColor;
    float crossfadeFactor;
    float crossfadeSpeed; // Samples per crossfade
};
```

**Crossfade:** When mode or color changes, crossfade between old and new configurations over ~100ms to avoid clicks.

---

## 10. Diffusion Network

### Purpose

Adds density and smooths the reverb tail by diffusing the signal through allpass filters.

### Implementation

```cpp
class DiffusionNetwork {
public:
    DiffusionNetwork();
    void setSampleRate(float sr);
    void setAmount(float amount); // 0-1
    void processBlock(float* inputL, float* inputR,
                      float* outputL, float* outputR,
                      int numSamples);
private:
    static const int NUM_ALLPASSES = 4;
    AllpassFilter allpasses[NUM_ALLPASSES];
    LFO modulation[NUM_ALLPASSES];
    
    void updateParameters();
};
```

### Configuration

```cpp
void DiffusionNetwork::updateParameters() {
    // Amount controls feedback
    float feedback = 0.5f + 0.49f * amount;
    
    // Fixed delay times for diffusion
    float delaysMs[NUM_ALLPASSES] = {3.7f, 2.3f, 1.7f, 1.1f};
    
    for (int i = 0; i < NUM_ALLPASSES; i++) {
        allpasses[i].setDelay(delaysMs[i]);
        allpasses[i].setFeedback(feedback);
        
        // Subtle modulation
        modulation[i].setRate(0.1f + i * 0.05f);
        modulation[i].setDepth(0.005f);
    }
}
```

---

## 11. Output Processing

### Output Filter

```cpp
class OutputFilter {
public:
    void setLowCut(float hz);
    void setHighCut(float hz);
    void processBlock(float* inputL, float* inputR,
                      float* outputL, float* outputR,
                      int numSamples);
private:
    OnePoleFilter lowCutL, lowCutR;
    OnePoleFilter highCutL, highCutR;
};
```

### EQ

```cpp
class OutputEQ {
public:
    enum BandType { LowShelf, HighShelf, Peak };
    
    struct Band {
        BandType type;
        float freq;
        float gain;
        float q;
    };
    
    void setBand(int index, const Band& band);
    void processBlock(float* inputL, float* inputR,
                      float* outputL, float* outputR,
                      int numSamples);
private:
    std::vector<Band> bands;
    std::vector<BiquadFilter> filtersL, filtersR;
};
```

### Mix Control

```cpp
class MixControl {
public:
    void setMix(float mix); // 0-1
    void setDucking(float ducking); // 0-1
    void processBlock(float* dryL, float* dryR,
                      float* wetL, float* wetR,
                      float* outputL, float* outputR,
                      int numSamples);
private:
    float mix;
    float ducking;
    SmoothedParameter mixParam;
    SmoothedParameter duckingParam;
};
```

---

## 12. Implementation Roadmap

### Phase D: DSP Architecture (Weeks 1-8)

**Week 1: Core Infrastructure**
- [ ] DelayLine (reuse from Delay plugin)
- [ ] CombFilter implementation
- [ ] AllpassFilter implementation
- [ ] FeedbackMatrix implementation
- [ ] Parameter system

**Week 2: FDN Network**
- [ ] FDNNetwork class
- [ ] Mode configuration system
- [ ] Feedback matrix configurations
- [ ] Stability testing

**Week 3: Early Reflections**
- [ ] ERGenerator class
- [ ] Tap generation algorithms
- [ ] Mode-specific ER configurations
- [ ] Pre-delay implementation

**Week 4: Modulation System**
- [ ] ModulationSystem class
- [ ] Per-voice modulation
- [ ] Modulation application to FDN
- [ ] Random modulation

**Week 5: Color System**
- [ ] ColorSystem class
- [ ] Color configurations (1970s, 1980s, Now)
- [ ] Color application to FDN
- [ ] Crossfade between colors

**Week 6: Mode Implementations**
- [ ] All 22 mode configurations
- [ ] Mode-specific FDN parameters
- [ ] Mode-specific ER configurations
- [ ] Mode-specific modulation

**Week 7: Output Processing**
- [ ] OutputFilter (lowpass/highpass)
- [ ] OutputEQ (shelving filters)
- [ ] MixControl (wet/dry mix, ducking)
- [ ] Stereo width control

**Week 8: Integration**
- [ ] Complete signal flow
- [ ] Parameter routing
- [ ] Preset system
- [ ] State save/load
- [ ] Mode/color transition

### Phase E: Interface Design (Week 9)
- [ ] Apply Living Compass 12 principles
- [ ] Create interface mockups
- [ ] Design Norse-inspired elements
- [ ] Color palette and typography
- [ ] Parameter layout for 22 modes + 3 colors

### Phase F: Plugin Implementation (Weeks 10-12)
- [ ] JUCE project setup
- [ ] AU/VST3 wrapper
- [ ] Parameter automation
- [ ] Host communication
- [ ] GUI implementation

### Phase G: Comparison & Refinement (Week 13)
- [ ] Reference comparison tests
- [ ] Impulse response analysis
- [ ] Frequency response analysis
- [ ] Decay curve analysis
- [ ] Listening tests
- [ ] Implementation refinement

### Phase H: Delivery (Week 14)
- [ ] Final builds (AU/VST3)
- [ ] Apple Silicon support
- [ ] Intel support
- [ ] Documentation
- [ ] Installation instructions
- [ ] Preset libraries

---

## 13. Evidence Mapping

| Component | Evidence | Status |
|-----------|----------|--------|
| 22 Modes | E032 | VERIFIED |
| 3 Colors | E033 | VERIFIED |
| Mode Categories | E032 | VERIFIED |
| Mode Characteristics | Official Documentation | VERIFIED |

---

## 14. Performance Considerations

### CPU Optimization
- **FDN Processing:** Optimize matrix operations (use SIMD)
- **Comb/Allpass:** Efficient delay line access
- **Modulation:** Pre-compute modulation values per block
- **Stereo Processing:** Process both channels in parallel

### Memory Optimization
- **Buffer Reuse:** Reuse temporary buffers
- **Pre-allocation:** All filters and delays pre-allocated
- **Cache Locality:** Arrange FDN data for cache efficiency

### Sample Rate Independence
- **Normalized Delays:** All delays in samples, recalculated on rate change
- **Resampling:** Reallocate delay lines on rate change

---

## 15. Testing Requirements

### Unit Tests
- [ ] CombFilter: Verify feedback and delay
- [ ] AllpassFilter: Verify phase response
- [ ] FeedbackMatrix: Verify orthogonality
- [ ] FDNNetwork: Verify stability
- [ ] ERGenerator: Verify tap generation
- [ ] ModulationSystem: Verify modulation application

### Integration Tests
- [ ] Mode configurations: Verify each mode produces expected characteristics
- [ ] Color system: Verify color modifications
- [ ] Parameter interactions: Verify parameter mappings
- [ ] State save/load: Verify preset recall

### Reference Comparison
- [ ] Impulse response comparison for each mode
- [ ] Frequency response comparison
- [ ] Decay time measurement
- [ ] Density measurement
- [ ] Modulation analysis
- [ ] Listening tests

---

## 16. Mode-Specific Notes

### Dirty Modes (1972-1979)
- **Characteristics:** Gritty, vintage, non-linear
- **Implementation:** Higher modulation depth, non-linear feedback, limited bandwidth
- **Inspirations:** Early digital reverbs, analog devices

### Smooth Modes (1980-1986)
- **Characteristics:** Clean, polished, natural
- **Implementation:** Lower modulation depth, linear feedback, full bandwidth
- **Inspirations:** Classic digital reverbs (Lexicon, EMT)

### Chaotic Modes (1987-1990)
- **Characteristics:** Random, unpredictable, experimental
- **Implementation:** Deep modulation, randomized parameters, time-varying configurations
- **Inspirations:** Experimental reverb algorithms

### Palace Modes (Now1-3)
- **Characteristics:** Large, spacious, modern
- **Implementation:** Long delays, deep modulation, wide stereo image
- **Inspirations:** Modern concert halls, cathedrals

---

*Version: 1.0 | Date: 2024-11-07 | Next: Phase D Start*

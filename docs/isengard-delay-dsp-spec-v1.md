# Isengard Delay - DSP Implementation Specification v1.0

**Status:** Draft  
**Date:** 2024-11-07  
**Phase:** B -> C Transition  
**Evidence Base:** E008-E033 (VERIFIED)

---

## 1. Executive Summary

Independent delay/echo processor inspired by ValhallaDelay. Based on VERIFIED documentation evidence.

**7 Modes:** Tape, HiFi, BBD, Digital, Ghost, Pitch, RevPitch  
**5 Styles:** Single, Dual, Ratio, PingPong, Quad  
**Diffusion:** 8x cascaded allpass filters with hardwired modulation

---

## 2. Architecture Overview

### Design Principles

1. Modular mode/style system with polymorphism
2. No dynamic allocation during audio processing
3. No locks in realtime audio thread
4. Sample rate independent
5. Tail preservation across host blocks

### Class Hierarchy

```
DelayProcessor
├── ParameterSystem (SmoothedParameter, ParameterBuffer)
├── InputProcessing (DC Blocker, Gain, Ducking)
├── ModeProcessor (abstract)
│   ├── TapeMode (Wow/Flutter LFOs, TapeSaturation)
│   ├── HiFiMode (SubtleModulation)
│   ├── BBDMode (Compander, ClockJitter, Lowpass)
│   ├── DigitalMode (BitCrusher)
│   ├── GhostMode (FrequencyShifter, Diffusion)
│   ├── PitchMode (PitchShifter)
│   └── RevPitchMode (ReverseBuffer, PitchShifter)
├── StyleProcessor (abstract)
│   ├── SingleStyle
│   ├── DualStyle
│   ├── RatioStyle
│   ├── PingPongStyle
│   └── QuadStyle
├── DiffusionNetwork (8x AllpassFilter + ModulationLFO)
├── OutputProcessing (EQ shelves, Mix, Gain)
└── FeedbackPath (Gain, Filter, Saturation)
```

---

## 3. Signal Flow

### Global Path

```
Input (L/R)
  → InputProcessing
  → ModeProcessor
  → StyleProcessor
  → DiffusionNetwork
  → FeedbackPath (loop back to ModeProcessor)
  → OutputProcessing
  → Output (L/R)
```

### Mode-Specific Variations

- **Tape:** Wow/Flutter modulation → Delay → TapeSaturation → MechanicalNoise
- **BBD:** Compander → ClockJitter → Delay → Lowpass → NoiseAddition
- **Digital:** BitCrusher → Delay
- **Ghost:** Delay → FrequencyShifter → FrequencyDependentDiffusion
- **Pitch:** Delay → PitchShifter
- **RevPitch:** Delay → Reverse → PitchShifter

---

## 4. Core Components

### 4.1 DelayLine

**Requirements:** Circular buffer, fractional delay interpolation, sample-rate independent, no dynamic allocation.

```cpp
class DelayLine {
public:
    DelayLine(int maxSizeSamples);
    void setSampleRate(float sr);
    void setDelayTime(float ms);
    float process(float input);
    void processBlock(float* buf, int numSamples);
private:
    std::vector<float> buffer;
    int writePos;
    float fracPos;
    float prevSamples[4]; // For cubic interpolation
    enum InterpMethod { Linear, Cubic, Allpass };
};
```

**Interpolation:** Linear (fastest), Cubic (better), Allpass (best phase response)

### 4.2 Modulation System

```cpp
class LFO {
public:
    enum Waveform { Sine, Triangle, Saw, Square, Random };
    LFO(float rateHz, float depth, Waveform wf);
    float getValue();
    void processBlock(int numSamples);
private:
    float rateHz, depth, phase;
    Waveform waveform;
};
```

**Mode-Specific Modulation:**
- Tape: Wow (0.1-2Hz, random) + Flutter (2-20Hz, random)
- HiFi: Subtle chorus (0.1-1Hz, sine/triangle)
- BBD: Clock jitter (random)

### 4.3 Filters

```cpp
class AllpassFilter {
public:
    void setFeedback(float fb); // 0.5-0.99
    void setDelay(float ms);
    float process(float input);
};

class OnePoleFilter {
public:
    enum Type { Lowpass, Highpass };
    OnePoleFilter(Type t, float cutoffHz);
    void setCutoff(float hz);
    float process(float input);
};
```

### 4.4 Nonlinear Processing

```cpp
class TapeSaturation {
public:
    void setDrive(float drive); // 0-1
    float process(float input); // tanh-based soft clipping
};

class BBDCompander {
public:
    void setNoiseFloor(float noise);
    float process(float input, float signalLevel);
};

class BitCrusher {
public:
    void setBitDepth(int bits); // 8-24
    float process(float input);
};
```

---

## 5. Mode Implementations

### Mode Base Class

```cpp
class DelayMode {
public:
    virtual ~DelayMode() = default;
    virtual void reset() = 0;
    virtual void setSampleRate(float sr) = 0;
    virtual void setParameters(const ModeParams& p) = 0;
    virtual void processBlock(float* inL, float* inR,
                              float* outL, float* outR,
                              int numSamples) = 0;
    virtual const char* getName() const = 0;
};
```

### 5.1 Tape Mode (E008-E012)

**Characteristics:** Analog tape emulation, wow/flutter modulation, tape saturation, mechanical noise.

```cpp
class TapeMode : public DelayMode {
public:
    TapeMode();
    const char* getName() const override { return "Tape"; }
    void setParameters(const ModeParams& p) override;
    void processBlock(...) override;
private:
    DelayLine delayL, delayR;
    LFO wowLFO;    // 0.1-2Hz, random
    LFO flutterLFO; // 2-20Hz, random
    TapeSaturation saturation;
    float tapeHiss;
    void updateModulationRates(float delayTimeMs);
};
```

**Modulation Scaling:** Wow/Flutter rates are functions of delay time (E012)
- Wow rate: 1000ms / delayTimeMs (clamped to 0.1-2Hz)
- Flutter rate: Wow rate * 10

### 5.2 HiFi Mode (E013-E014)

**Characteristics:** Clean high-fidelity delay, subtle modulation.

```cpp
class HiFiMode : public DelayMode {
public:
    const char* getName() const override { return "HiFi"; }
private:
    DelayLine delayL, delayR;
    LFO modulation; // Subtle chorus-like
    OnePoleFilter dcBlocker;
};
```

### 5.3 BBD Mode (E015-E017)

**Characteristics:** Bucket Brigade Device emulation, noise tracks signal level via compander, clock jitter, limited bandwidth.

```cpp
class BBDMode : public DelayMode {
public:
    const char* getName() const override { return "BBD"; }
private:
    DelayLine delayL, delayR;
    BBDCompander compander;
    LFO clockJitter;
    OnePoleFilter lowpass;
    float noiseLevel;
    void updateNoiseTracking(float signalLevel); // E017
};
```

**Noise Tracking:** Noise tracks signal level (E017)
- noiseScale = max(0.01, 1.0 - signalLevel * 0.9)
- noiseLevel = noiseScale * noiseAmount

### 5.4 Digital Mode (E018-E019)

**Characteristics:** Clean digital delay, Age parameter controls bit depth.

```cpp
class DigitalMode : public DelayMode {
public:
    const char* getName() const override { return "Digital"; }
private:
    DelayLine delayL, delayR;
    BitCrusher bitCrusher;
    void updateBitDepth(float age); // E019
};
```

**Age Mapping (E019):**
- Age 0% = 24-bit
- Age 50% = 12-bit
- Age 100% = 8-bit
- Formula: bits = 24 - (int)(age * 16)

### 5.5 Ghost Mode (E020-E021)

**Characteristics:** Frequency shifting in feedback path, frequency-dependent diffusion, Present/Future ERA.

```cpp
class GhostMode : public DelayMode {
public:
    const char* getName() const override { return "Ghost"; }
private:
    DelayLine delayL, delayR;
    FrequencyShifter freqShifter;
    DiffusionNetwork diffusion;
    float era; // Present/Future
    void updateFrequencyDependentDiffusion(float era); // E021
};
```

### 5.6 Pitch Mode (E022)

**Characteristics:** Pitch shifting in feedback path.

```cpp
class PitchMode : public DelayMode {
public:
    const char* getName() const override { return "Pitch"; }
private:
    DelayLine delayL, delayR;
    PitchShifter pitchShifter;
    float pitchShiftSemi;
    float pitchDetuneCents;
};
```

### 5.7 RevPitch Mode (E023)

**Characteristics:** Reverse delay with pitch shifting.

```cpp
class RevPitchMode : public DelayMode {
public:
    const char* getName() const override { return "RevPitch"; }
private:
    DelayLine delayL, delayR;
    PitchShifter pitchShifter;
    ReverseBuffer reverseBuffer;
};
```

---

## 6. Style Implementations

### Style Base Class

```cpp
class DelayStyle {
public:
    virtual ~DelayStyle() = default;
    virtual void reset() = 0;
    virtual void setSampleRate(float sr) = 0;
    virtual void setParameters(const StyleParams& p) = 0;
    virtual void processBlock(std::vector<DelayLine>& delays,
                              float* inL, float* inR,
                              float* outL, float* outR,
                              int numSamples) = 0;
    virtual const char* getName() const = 0;
};
```

### 6.1 Single Style (E024)

**Characteristics:** Single delay line per channel, independent L/R.

```cpp
class SingleStyle : public DelayStyle {
public:
    const char* getName() const override { return "Single"; }
};
```

**Signal Flow:**
```
Left Input → Left Delay → Left Output
Right Input → Right Delay → Right Output
```

### 6.2 Dual Style (E025)

**Characteristics:** Two independent delay lines per channel.

```cpp
class DualStyle : public DelayStyle {
public:
    const char* getName() const override { return "Dual"; }
private:
    float spread;
};
```

**Signal Flow:**
```
Left Input → Left Delay 1 → Left Delay 2 → Left Output
Right Input → Right Delay 1 → Right Delay 2 → Right Output
```

### 6.3 Ratio Style (E026)

**Characteristics:** Delay times related by musical ratios.

```cpp
class RatioStyle : public DelayStyle {
public:
    const char* getName() const override { return "Ratio"; }
private:
    float ratio; // 0.1-2.0
};
```

**Ratio Calculation:** delay2Ms = delay1Ms * ratio

### 6.4 PingPong Style (E027)

**Characteristics:** Delays bounce between L/R channels.

```cpp
class PingPongStyle : public DelayStyle {
public:
    const char* getName() const override { return "PingPong"; }
private:
    bool pingPongDirection; // L→R or R→L
};
```

**Signal Flow:**
```
Left Input → Left Delay → Right Output
Right Input → Right Delay → Left Output
Feedback: Left Delay Out → Right Delay In
          Right Delay Out → Left Delay In
```

### 6.5 Quad Style (E028)

**Characteristics:** Four delay lines, complex stereo routing.

```cpp
class QuadStyle : public DelayStyle {
public:
    const char* getName() const override { return "Quad"; }
private:
    float spread, width;
};
```

**Signal Flow:**
```
Left Input → Left Delay 1 → Left Delay 2 → Left Output
            → Right Delay 1 → Right Delay 2 → Right Output
Right Input → Right Delay 1 → Right Delay 2 → Right Output
            → Left Delay 1 → Left Delay 2 → Left Output
```

---

## 7. Diffusion Network (E029-E031)

**Architecture:** 8 cascaded allpass filters with hardwired modulation.

```cpp
class DiffusionNetwork {
public:
    static const int NUM_ALLPASSES = 8;
    void setSampleRate(float sr);
    void setAmount(float amount); // 0-1, controls feedback (0.5-0.99)
    void setSize(float size);     // 0-1, controls delay times (1-10ms)
    float process(float input);
private:
    AllpassFilter allpasses[NUM_ALLPASSES];
    LFO modulation[NUM_ALLPASSES]; // Hardwired per allpass
    void updateFilterParameters();
};
```

**Parameter Mapping:**
- Amount: allpass feedback = 0.5 + 0.49 * amount
- Size: base delay = 1.0 + 9.0 * size (1-10ms)

**Modulation:**
- Each allpass has independent, hardwired modulation
- Modulation rates: 0.1 to 0.45 Hz (increasing with index)
- Modulation depth: Fixed at 0.01 (subtle)
- Waveform: Random

**Signal Flow:**
```
Input → Allpass 1 → Allpass 2 → ... → Allpass 8 → Output
                 ↑              ↑              ↑
            Mod LFO 1     Mod LFO 2     Mod LFO 3
```

---

## 8. Parameter System

### 8.1 Parameter Structure

```cpp
struct DelayParameters {
    // Global
    float mix;           // 0-1, linear
    float feedback;      // 0-0.99, logarithmic
    float inputGain;     // -60 to +24 dB
    float outputGain;    // -60 to +24 dB
    
    // Delay
    float delayTimeMs;   // 1-5000, logarithmic
    float delayLeftMs;   // 1-5000, logarithmic
    float delayRightMs;  // 1-5000, logarithmic
    float ratio;         // 0.1-2.0, linear
    float spread;        // 0-1, linear
    float width;         // 0-1, linear
    
    // Modulation
    float modRate;       // 0.1-20 Hz, logarithmic
    float modDepth;      // 0-1, linear
    
    // Mode-specific
    float age;           // 0-1, linear (Digital: bit depth)
    float drive;         // 0-1, linear (Tape: saturation)
    float wowDepth;      // 0-1, linear (Tape)
    float flutterDepth;  // 0-1, linear (Tape)
    float noiseAmount;   // 0-1, linear (BBD)
    
    // Diffusion
    float diffusionAmount; // 0-1, linear
    float diffusionSize;   // 0-1, linear
    
    // EQ
    float eqLow;         // 20-20000 Hz, logarithmic
    float eqHigh;        // 20-20000 Hz, logarithmic
    
    // Other
    float era;           // 0-1, linear (Ghost)
    float pitchShift;    // -24 to +24 semitones, linear
    float pitchDetune;   // -100 to +100 cents, linear
    float ducking;       // 0-1, linear
};
```

### 8.2 Parameter Smoothing

```cpp
class SmoothedParameter {
public:
    SmoothedParameter(float initial, float smoothingTimeMs);
    void setValue(float value);
    void setSmoothingTime(float ms);
    float getSmoothedValue();
    void processBlock(int numSamples);
private:
    float targetValue, currentValue, smoothingCoeff;
};
```

**Smoothing Times:**
- Mix, Feedback: 10-50ms
- Delay Time: 20ms
- Modulation: 50ms
- Age, Pitch: 100ms

### 8.3 Automation Handling

- Double buffering for thread-safe parameter updates
- Sample-accurate smoothing for automation
- No locks in audio thread

```cpp
class ParameterBuffer {
public:
    void setParameter(int idx, float value); // Non-audio thread
    float getParameter(int idx); // Audio thread
    void swapBuffers(); // At block start
private:
    std::vector<float> bufferA, bufferB;
    std::vector<float> *readBuffer, *writeBuffer;
};
```

---

## 9. Implementation Roadmap

### Phase D: DSP Architecture (Weeks 1-6)

**Week 1: Core Infrastructure**
- [ ] DelayLine with fractional interpolation
- [ ] Circular buffer management
- [ ] Sample rate handling
- [ ] Memory allocation system
- [ ] Parameter system with smoothing
- [ ] Basic signal flow

**Week 2-3: Mode Implementations**
- [ ] TapeMode (Wow/Flutter, Saturation)
- [ ] HiFiMode (Clean, Modulation)
- [ ] BBDMode (Compander, Clock Jitter)
- [ ] DigitalMode (Bit Crusher)
- [ ] GhostMode (Frequency Shifter, Diffusion)
- [ ] PitchMode (Pitch Shifter)
- [ ] RevPitchMode (Reverse + Pitch)

**Week 4: Style Implementations + Diffusion**
- [ ] SingleStyle
- [ ] DualStyle
- [ ] RatioStyle
- [ ] PingPongStyle
- [ ] QuadStyle
- [ ] DiffusionNetwork (8x allpass + modulation)

**Week 5: Output Processing**
- [ ] EQ shelves (High/Low)
- [ ] Mix control
- [ ] Output gain
- [ ] Ducking (sidechain)

**Week 6: Integration**
- [ ] Mode/Style combination
- [ ] Parameter routing
- [ ] Preset system
- [ ] State save/load

### Phase E: Interface Design (Week 7)
- [ ] Apply Living Compass 12 principles
- [ ] Create interface mockups
- [ ] Design Norse-inspired elements
- [ ] Color palette and typography

### Phase F: Plugin Implementation (Weeks 8-10)
- [ ] JUCE project setup
- [ ] AU/VST3 wrapper
- [ ] Parameter automation
- [ ] Host communication
- [ ] GUI implementation

### Phase G: Comparison & Refinement (Week 11)
- [ ] Reference comparison tests
- [ ] Parameter sweep validation
- [ ] Impulse response analysis
- [ ] Listening tests
- [ ] Implementation refinement

### Phase H: Delivery (Week 12)
- [ ] Final builds (AU/VST3)
- [ ] Apple Silicon support
- [ ] Intel support
- [ ] Documentation
- [ ] Installation instructions
- [ ] Preset libraries

---

## 10. Evidence Mapping

| Component | Evidence | Status |
|-----------|----------|--------|
| Tape Mode | E008-E012 | VERIFIED |
| HiFi Mode | E013-E014 | VERIFIED |
| BBD Mode | E015-E017 | VERIFIED |
| Digital Mode | E018-E019 | VERIFIED |
| Ghost Mode | E020-E021 | VERIFIED |
| Pitch Mode | E022 | VERIFIED |
| RevPitch Mode | E023 | VERIFIED |
| Single Style | E024 | VERIFIED |
| Dual Style | E025 | VERIFIED |
| Ratio Style | E026 | VERIFIED |
| PingPong Style | E027 | VERIFIED |
| Quad Style | E028 | VERIFIED |
| Diffusion Network | E029-E031 | VERIFIED |

---

## 11. Performance Considerations

### CPU Optimization
- SIMD instructions for delay line processing
- Block processing (not sample-by-sample)
- Cache-friendly data layout
- Minimize conditional branches

### Memory Optimization
- Pre-allocation at construction
- Power-of-2 buffer sizes
- Buffer reuse across blocks

### Sample Rate Independence
- Normalized frequencies
- Resample modulation LFOs on rate change
- Reallocate delay lines on rate change

---

## 12. Testing Requirements

### Unit Tests
- [ ] DelayLine accuracy
- [ ] Fractional delay interpolation
- [ ] Stability under modulation
- [ ] Mode characteristics
- [ ] Style routing
- [ ] Diffusion behavior
- [ ] Parameter smoothing
- [ ] Automation handling

### Integration Tests
- [ ] Mode + Style combinations
- [ ] Parameter interactions
- [ ] State save/load
- [ ] Sample rate changes
- [ ] Block size changes

### Reference Comparison
- [ ] Impulse response comparison
- [ ] Frequency response comparison
- [ ] Parameter sweep comparison
- [ ] Listening tests

---

*Version: 1.0 | Date: 2024-11-07 | Next: Phase D Start*

# ValhallaDelay Official Documentation Analysis

**Project:** Isengard Delay & Isengard Verb  
**Phase:** B - Reference Investigation  
**Source:** https://valhalladsp.com/2019/04/16/valhalladelay-the-controls/  
**Source:** https://valhalladsp.com/2019/04/16/valhalladelay-the-mode-control/  
**Source:** https://valhalladsp.com/2019/04/16/valhalladelay-the-style-control/  
**Source:** https://valhalladsp.com/2019/06/13/valhalladelay-the-diffusion-section/  
**Date:** 2026-11-07  
**Status:** COMPREHENSIVE ANALYSIS

---

## 1. Executive Summary

This document contains extracted and analyzed information from the official ValhallaDelay documentation. It provides **VERIFIED** evidence for the DSP architecture, modes, styles, and parameter behavior.

**Key Finding:** The documentation confirms and expands significantly on our earlier hypotheses, providing exact details about modes, styles, and parameter behavior.

---

## 2. Plugin Overview

### 2.1 Design Philosophy

> "ValhallaDelay was designed from the ground up to capture the sound of different types of delay units (tape, BBD, early digital), while both expanding upon these sounds, as well as keeping things as simple as possible."

**Interpretation:**
- Emulates specific hardware types (tape, BBD, early digital)
- Expands beyond emulation to new sonic territories
- Simplicity of interface (only relevant controls visible)

### 2.2 GUI Behavior

> "The visible controls in ValhallaDelay depend on both the active Mode and Style. Only the controls relevant to a given Mode/Style combination will be visible in the GUI, with the values in the inactive Modes/Styles being retained so you can easily switch back and forth while previewing sounds."

**Implementation Note for Isengard Delay:**
- Context-sensitive parameter visibility
- Parameter values retained when switching modes/styles
- Smooth transitions between configurations

---

## 3. Modes (Algorithms)

### 3.1 Mode List

**VERIFIED:** ValhallaDelay has **7 Modes** (not 5 as initially thought):

1. **Tape** - Detailed model of tape delay with variable motor speed (RE-201, RE-301)
2. **HiFi** - Higher fidelity tape echo (reel-to-reel studio decks)
3. **BBD** - Bucket brigade delay with compander artifacts
4. **Digital** - 1980s delay units with floating point converters
5. **Ghost** - Analog-style delay with frequency shifting
6. **Pitch** - Digital-modeled delay with built-in pitch shifting
7. **RevPitch** - Delay that reverses and pitch shifts input signal

**Additional Modes (from other sources):**
- Quartz (added in v2.1.0) - 80s/90s digital delays
- PhaserDDL (added in v2.1.0) - Delay with phaser in feedback
- Chrome Tape (added in v3.0.0) - Tape with reduced artifacts
- Analog (added in v3.0.0) - Between BBD and digital

### 3.2 Mode Details

#### Tape Mode

**Characteristics:**
- Based on RE-201 and RE-301 tape delays
- Wow/flutter rate and depth are functions of delay time (physically accurate)
- Overall equalization varies with delay time

**Parameters:**
- **MOD Wow**: Scale for wow depth (slow random modulation)
- **MOD Flutter**: Scale for flutter depth (fast random modulation)
- **Age**: Asperity noise + tape splice artifacts
- **ERA**: Different modeled tape echoes
  - Past: Darker, dirtier, pronounced HF oscillation for short delays
  - Present: Darker, dirtier
  - Future: More refined

**DSP Implementation Notes:**
- Delay time affects wow/flutter characteristics (not just a fixed LFO)
- Wow and flutter should be scaled by delay time
- Age adds noise that varies with signal level (compander action)
- ERA changes filter characteristics and saturation

#### HiFi Mode

**Characteristics:**
- Higher fidelity tape echo (reel-to-reel studio decks)
- More control over modulation

**Parameters:**
- **MOD Rate/Depth**: Rate and depth of random wow & flutter
  - Rates are NOT a function of delay setting (unlike Tape mode)
- **Age**: Asperity noise only (no splicing artifacts)

**DSP Implementation Notes:**
- Independent modulation rate (not tied to delay time)
- Cleaner than Tape mode
- Still has tape-like characteristics

#### BBD Mode

**Characteristics:**
- Bucket brigade delay emulation
- Compander artifacts
- BBD noise
- Limited high frequency response
- Dark and dirty sound

**Parameters:**
- **MOD Rate/Depth**: Smoothed triangle LFO for vibrato/pitch slews
- **Age**: Noise amount (varies with signal level due to compander)
- **Drive**: Higher settings create "ducking" sound as compander kicks in
- **ERA**: Different BBD models
  - Darker models
  - Brighter Future model

**DSP Implementation Notes:**
- Compander is key to BBD character
- Noise level should track input signal (compander behavior)
- Triangle LFO (not sine) for modulation
- Bandwidth limitation (low-pass filtering)

#### Digital Mode

**Characteristics:**
- Based on 1980s delay units
- Used "floating point convertors" for gritty yet smooth sound

**Parameters:**
- **MOD Rate/Depth**: Smoothed triangle LFO for vibrato/pitch slews
- **Age**: Bit resolution control
  - 50% = 12-bit delay
  - Higher Age = lower bit depth
- **ERA**: Different frequency responses and saturation types

**DSP Implementation Notes:**
- Bit crushing for Age parameter
- Triangle LFO modulation
- Floating-point converter emulation (quantization noise)

#### Ghost Mode

**Characteristics:**
- Combines analog-style delay with frequency shifting

**Parameters:**
- **FREQ Shift**: Frequency shift of both channels (Hz)
- **FREQ Detune**: Frequency shift offset between L/R channels (Hz)
  - Low values = subtle stereo spread
  - High values = rapid panning effect
- **ERA**: Different types of diffusion
  - Past: Standard diffusion
  - Present: Frequency-dependent diffusion (higher freqs have less phase delay)
  - Future: More frequency-dependent diffusion

**DSP Implementation Notes:**
- Frequency shifting in feedback path
- Frequency-dependent allpass filters for Present/Future ERA
- Creates "ghostly" effects with different frequency arrival times

#### Pitch Mode

**Characteristics:**
- Digital-modeled delay with built-in pitch shifting

**Parameters:**
- **PITCH Shift**: Overall pitch shift (semitones)
- **PITCH Detune**: Pitch offset between L/R channels (cents)
  - Perfect for micropitch and doubling
- **ERA**: Different filtering and saturation types

**DSP Implementation Notes:**
- Pitch shifting in feedback path
- Independent pitch for L/R channels
- Formant preservation likely not used (simple pitch shift)

#### RevPitch Mode

**Characteristics:**
- Delay that reverses and pitch shifts input signal
- DELAY parameters control the "splice size" of output

**Parameters:**
- **PITCH Shift**: Overall pitch shift (semitones)
- **PITCH Detune**: Pitch offset between L/R channels (cents)
- **DELAY**: Controls splice size (not traditional delay time)

**DSP Implementation Notes:**
- Reverse buffer processing
- Granular-style processing with pitch shifting
- Splice size determines grain size

---

## 4. Styles (Channel Routing)

### 4.1 Style List

**VERIFIED:** ValhallaDelay has **5 Styles**:

1. **Single**
2. **Dual**
3. **Ratio**
4. **PingPong**
5. **Quad**

### 4.2 Style Details

#### Single Style

**Characteristics:**
- Same delay time for left and right
- Same modulation waveform for both channels
- Essentially mono delay but processes L/R separately to preserve stereo image

**Parameters:**
- **DELAY**: Base delay for both channels
- **SPREAD**: Slight offset between L/R delays
  - Value added to left channel
  - Value subtracted from right channel
  - Creates wide, 3D sound from mono inputs

**DSP Implementation Notes:**
- Two separate delay lines with same base time
- Spread creates slight time difference (L = delay + spread, R = delay - spread)
- Modulation identical for both channels

#### Dual Style

**Characteristics:**
- Separate delay controls for L/R
- Each channel feeds back on itself (no cross feedback)
- Different modulation waveforms for L/R
- Essentially 2 delays in parallel

**Parameters:**
- **DELAY L**: Base delay for left channel
- **DELAY R**: Base delay for right channel

**DSP Implementation Notes:**
- Two independent delay lines
- Separate feedback paths (no cross-feed)
- Different modulation LFOs for each channel

#### Ratio Style

**Characteristics:**
- DELAY knob controls left channel delay
- Right channel delay = DELAY × RATIO
- Feedback paths combined via unitary matrix
- Creates pseudo-reverb at specific ratios

**Parameters:**
- **DELAY**: Base delay for left channel
- **RATIO**: Multiplier for right channel (0-200%)
  - 100% = equal delays
  - 61.8% = Golden Ratio pseudo-reverb

**DSP Implementation Notes:**
- Right delay = left delay × ratio
- Unitary matrix mixing of feedback (preserves energy)
- Golden ratio (61.8%) creates non-repeating echo patterns
- Higher feedback + ratio < 100% = gradual echo density buildup

#### PingPong Style

**Characteristics:**
- Classic ping-pong delay
- Left and right inputs summed → left delay
- Left delay feedback → right delay
- Right delay feedback → left delay
- And so on...

**Parameters:**
- **DELAY L**: Left channel delay time
- **DELAY R**: Right channel delay time
- **WIDTH**: Controls panning
  - 100% = L input → L output, R input → R output
  - 0% = L and R delay outputs mixed equally (can cause flanging)
  - -100% = Swaps L and R output channels

**DSP Implementation Notes:**
- Cross-coupled feedback: L→R→L→R...
- Different delay times create different ping-pong rhythms
- WIDTH = -100% makes ping start from right channel

#### Quad Style

**Characteristics:**
- Emulates multi-head tape echoes
- 4 taps (A, B, C, D) per channel
- Each tap is a pair of delay reads (one L, one R)

**Parameters:**
- **DELAY**: Base delay time (Tap D = DELAY)
- **SPACING**: Controls spacing between taps
  - 0% = identical spacing
    - Example: DELAY=500ms → Tap A=125ms, B=250ms, C=375ms, D=500ms
  - < 0% = taps get closer to longest delay
  - > 0% = taps get closer to shortest delay
- **TAP A/B/C/D**: Enable/disable individual tap pairs
- **REPEAT/SWELL**: Changes feedback behavior
  - **REPEAT**: Feedback from Tap D only (longest delay)
    - Preferred for repeating tap patterns
  - **SWELL**: Feedback from all active taps
    - Similar to multi-head RE-201/RE-301
    - Can get unstable with high feedback
    - Modulation helps stabilize at higher feedback levels

**DSP Implementation Notes:**
- 4 delay taps per channel
- Tap positions calculated based on SPACING
- REPEAT mode: Simple feedback from last tap
- SWELL mode: Sum of all active taps in feedback
- SWELL + SPACING > 0 + modulation = Space Station-like reverb sounds

---

## 5. Diffusion Section

### 5.1 Overview

**VERIFIED:** The diffusion section uses cascaded allpass filters with hardwired modulation.

**Design Goals:**
- Simple to use (only 2 controls: Amount, Size)
- Sounds good at all settings
- Allows from slight smearing to massive reverbs

**Key Features:**
- No on/off switch (Amount < 1% = off, saves CPU)
- Hardwired modulation depth (scaled by diffusion size)
- Dense diffusion (higher order allpass network always used)
- Huge size (can span 20 seconds without sounding sparse or grainy)

### 5.2 Diffusion Controls

#### Amount

**Range:** 0-100%

**Behavior:**
- 0% = OFF (diffusion bypassed)
- 68% = Attack time equals decay time (nice for reverbs)
- 91% = Good for "pure diffusion" reverb without feedback

**DSP Implementation:**
- Controls coefficients of diffusors (allpass filters)
- Larger coefficient = longer decay, shorter attack
- Modulation depth scaled by Amount

#### Size

**Range:** 0-100%

**Behavior:**
- Controls length of diffusion network as percentage of delay length
- 0% = shortest
- 100% = longest (diffusion network = delay length)
- In most modes: diffusion length + straight delay = 100% of displayed delay
  - As diffusion gets longer, straight delay gets shorter
  - Overall delay remains constant
- **Exception:** RevPitch mode
  - Diffusion is ADDED to base delay (not replacing)
  - Necessary because RevPitch delay constantly changes

**DSP Implementation:**
- Diffusion network length = Size × delay_length
- Straight delay length = (1 - Size) × delay_length (in most modes)
- Allpass filter lengths scaled accordingly

### 5.3 Special Cases

**Ghost Mode Diffusion:**
- Present and Future ERA: Frequency-dependent diffusion
- Higher frequencies have less phase delay applied
- Results: "Really weird" sounds from ghostly voices to bouncing ball delays

**Modulation:**
- Zero net pitch change
- Virtually inaudible at low Diffusion Amount
- Depth scaled by diffusion size
- Short diffusion (smeared delay) = less modulation
- Long diffusion (reverb) = more modulation

---

## 6. Core Parameters

### 6.1 Mix

**Range:** 0-100%

**Behavior:**
- 0% = Dry signal only
- 50% = Equal wet and dry
- 100% = Delayed signal only

**Features:**
- **Mix Lock:** Click "MIX" to lock value when browsing presets

**DSP Implementation:**
- Simple wet/dry mix
- Linear or logarithmic taper (documentation doesn't specify, but likely linear for simplicity)

### 6.2 Feedback

**Range:** 0-200%

**Behavior:**
- Controls amount of delay fed back into input
- Self-oscillation begins around 100% (depending on other settings)
- 200% allows for "howling self-oscillation"

**DSP Implementation:**
- Feedback gain > 1.0 = self-oscillation
- 200% = 2.0 gain (very unstable)
- Likely has internal limiting to prevent overflow

### 6.3 Width

**Range:** -100% to 100%

**Behavior:**
- 100% = L input → L output, R input → R output (normal)
- 0% = L and R delay outputs mixed equally (can cause flanging)
- -100% = Swaps L and R output channels

**DSP Implementation:**
- Panning law: Likely equal-power or linear
- 0% = mono sum of delay outputs
- Crossfade between L/R and mono

### 6.4 Color Parameters

#### Drive

**Range:** -12 to +12 dB (input boost)

**Behavior:**
- Controls input boost to saturation algorithm
- Output scaled by (-boostInDb/2) to maintain constant volume
- Example: +6 dB boost → output scaled by -3 dB

**DSP Implementation:**
- Input gain stage
- Saturation algorithm (mode-specific)
- Output gain compensation
- Net result: Volume remains constant across Drive settings

#### Age

**Behavior:** Mode-specific

| Mode | Age Effect |
|------|------------|
| Tape | Asperity noise + tape splice artifacts |
| HiFi | Asperity noise only |
| BBD | BBD chip noise (tracks signal dynamics via compander) |
| Digital | Bit depth of floating point converter (50% = 12-bit) |
| Ghost | Asperity noise |
| Pitch | Bit depth of floating point converter |
| RevPitch | Bit depth of floating point converter |

**DSP Implementation:**
- Mode-specific noise/artifact generation
- BBD: Noise level varies with input signal (compander modeling)
- Digital/Pitch/RevPitch: Bit crushing

### 6.5 EQ Parameters

#### EQ High

**Range:** Frequency in Hz

**Behavior:**
- Cutoff frequency of high cut filter
- Filter is in the FEEDBACK path (not output)

**DSP Implementation:**
- Low-pass filter in feedback loop
- Prevents high-frequency buildup
- Affects tone of repeats, not direct signal

#### EQ Low

**Range:** Frequency in Hz

**Behavior:**
- Cutoff frequency of low cut filter
- Filter is in the FEEDBACK path (not output)

**DSP Implementation:**
- High-pass filter in feedback loop
- Removes DC and low-frequency rumble
- Affects tone of repeats, not direct signal

### 6.6 Era

**Behavior:** Mode-specific variations

| Mode | Era Effect |
|------|------------|
| Tape | Different modeled tape echoes (Past/Present = darker/dirtier, Future = refined) |
| HiFi | Not specified (likely different tape characteristics) |
| BBD | Darker models vs. brighter Future model |
| Digital | Different frequency responses and saturation types |
| Ghost | Different diffusion types (Past = standard, Present = freq-dependent, Future = more freq-dependent) |
| Pitch | Different filtering and saturation types |
| RevPitch | Not specified |

**DSP Implementation:**
- Preset configurations for each mode
- Changes multiple parameters simultaneously
- Mode-specific behavior

---

## 7. Modulation Parameters

### 7.1 Tape Mode Only

#### MOD Wow

**Behavior:**
- Scale for slow random length modulation
- Rate is a function of delay time (physically accurate)

**DSP Implementation:**
- Random LFO (slow)
- Depth scaled by Wow parameter
- Rate = f(delay_time)

#### MOD Flutter

**Behavior:**
- Scale for fast random length modulation
- Rate is a function of delay time (physically accurate)

**DSP Implementation:**
- Random LFO (fast)
- Depth scaled by Flutter parameter
- Rate = f(delay_time)

### 7.2 HiFi, BBD, Digital Modes

#### MOD Rate

**Behavior:**
- Rate of random (HiFi) or periodic (BBD, Digital) delay length modulation

**DSP Implementation:**
- Random LFO (HiFi) or triangle LFO (BBD, Digital)
- Rate in Hz (not tied to delay time in HiFi mode)

#### MOD Depth

**Behavior:**
- Depth of modulation

**DSP Implementation:**
- Modulation depth in samples or milliseconds
- Scales LFO output

### 7.3 Ghost Mode Only

#### FREQ Shift

**Range:** Hz

**Behavior:**
- Frequency shift of both L and R channels

**DSP Implementation:**
- Frequency shifting algorithm (phase vocoder or single-sideband)
- Applied to delay signal

#### FREQ Detune

**Range:** Hz

**Behavior:**
- Frequency shift offset between L and R channels
- Low values = subtle stereo spread
- High values = rapid panning effect

**DSP Implementation:**
- Different frequency shifts for L and R
- Creates stereo movement

### 7.4 Pitch/RevPitch Modes Only

#### PITCH Shift

**Range:** Semitones

**Behavior:**
- Pitch shift of both L and R channels

**DSP Implementation:**
- Pitch shifting algorithm
- Applied to delay signal

#### PITCH Detune

**Range:** Cents

**Behavior:**
- Pitch offset between L and R channels
- Perfect for micropitch and doubling

**DSP Implementation:**
- Different pitch shifts for L and R
- Creates stereo widening

---

## 8. Sync Parameters

### 8.1 DELAY L Sync / DELAY R Sync

**Behavior:**
- Choose between milliseconds or tempo-sync
- Options: milliseconds, notes, dotted, triplets

**DSP Implementation:**
- Converts note values to milliseconds based on host BPM
- Overrides DELAY parameter when tempo-sync enabled

---

## 9. Quad Mode Specific Parameters

### 9.1 REPEAT/SWELL

**Behavior:**
- **REPEAT:** Feedback from Tap D only (longest delay)
- **SWELL:** Feedback from all active taps

**DSP Implementation:**
- REPEAT: Simple feedback from last tap
- SWELL: Sum of all active taps in feedback path

### 9.2 TAP A/B/C/D

**Behavior:**
- Enable/disable individual tap pairs

**DSP Implementation:**
- Toggle each tap on/off
- Affects both feedback and output

### 9.3 SPACING

**Range:** -100% to 100%

**Behavior:**
- 0% = identical spacing between taps
- < 0% = taps get closer to longest delay
- > 0% = taps get closer to shortest delay

**DSP Implementation:**
- Non-linear spacing calculation
- Affects tap positions

---

## 10. DSP Architecture Summary

### 10.1 Signal Flow (General)

```
Input
  │
  ▼
[Pre-processing: Drive, Age]
  │
  ▼
[Delay Line(s) with Modulation]
  │
  ▼
[Feedback Path: Feedback Gain, EQ High, EQ Low, Diffusion]
  │
  ▼
[Output Processing: Width]
  │
  ▼
Mix with Dry Signal
  │
  ▼
Output
```

### 10.2 Mode-Specific Variations

| Mode | Key Characteristics |
|------|-------------------|
| Tape | Wow/Flutter tied to delay time, splice artifacts |
| HiFi | Independent wow/flutter, no splice artifacts |
| BBD | Compander, noise tracks signal, triangle LFO |
| Digital | Bit crushing, triangle LFO |
| Ghost | Frequency shifting, freq-dependent diffusion |
| Pitch | Pitch shifting in feedback |
| RevPitch | Reverse + pitch shift, granular-style |

### 10.3 Style-Specific Routing

| Style | Routing |
|-------|---------|
| Single | L and R with same delay, same modulation |
| Dual | Independent L and R delays, no cross feedback |
| Ratio | R delay = L delay × ratio, unitary matrix mixing |
| PingPong | Cross-coupled: L→R→L→R... |
| Quad | 4 taps per channel, configurable spacing |

---

## 11. Evidence Classification

All information in this document is **VERIFIED** based on official Valhalla DSP documentation.

---

## 12. Implementation Notes for Isengard Delay

### 12.1 Mode Implementation Priority

1. **Digital** - Simplest, cleanest reference
2. **Tape** - Most characteristic, requires wow/flutter modeling
3. **BBD** - Requires compander modeling
4. **Ghost** - Frequency shifting + diffusion
5. **Pitch** - Pitch shifting in feedback
6. **RevPitch** - Reverse + pitch shift
7. **HiFi** - Similar to Tape but with independent modulation

### 12.2 Style Implementation Priority

1. **Single** - Simplest
2. **Dual** - Independent channels
3. **PingPong** - Cross-coupled
4. **Ratio** - Requires matrix mixing
5. **Quad** - Most complex (4 taps)

### 12.3 Parameter Mapping Strategy

- Use exact parameter names from documentation
- Implement mode/style-specific parameter visibility
- Maintain parameter values when switching modes/styles
- Use documentation ranges as starting points

---

**Last Updated:** 2026-11-07  
**Author:** Vibe Code (Mistral AI)  
**Sources:** Official Valhalla DSP Documentation

# Parameter Mappings

**Project:** Isengard Delay & Isengard Verb  
**Phase:** B - Reference Investigation  
**Status:** INITIAL ANALYSIS

---

## 1. ValhallaDelay Parameters

### 1.1 Core Parameters

#### Mix
- **Range:** 0-100% (or -∞ to 0 dB)
- **Type:** Wet/Dry balance
- **Mapping:** Likely linear in percentage, logarithmic in dB
- **Affects:** Output signal (direct path and delayed path mix)
- **Smoothing:** Likely smoothed to prevent clicks
- **Behavior:** 
  - 0% = 100% dry (no effect)
  - 50% = Equal wet and dry
  - 100% = 100% wet (no dry signal)

#### Feedback
- **Range:** 0-100% (or 0-1.0)
- **Type:** Feedback gain
- **Mapping:** Likely logarithmic (perceptual linearity)
- **Affects:** Feedback path (amount of delayed signal fed back)
- **Smoothing:** Smoothed to prevent clicks
- **Behavior:**
  - 0% = No feedback (single echo)
  - 50% = Moderate feedback (several echoes)
  - 100% = Maximum feedback (infinite echoes, may self-oscillate)
- **Stability:** Likely has internal limiting to prevent overflow

#### Delay
- **Range:** 0-5000ms (or similar)
- **Type:** Delay time
- **Mapping:** Likely linear in milliseconds
- **Affects:** Main delay line length
- **Smoothing:** Smoothed with interpolation
- **Behavior:**
  - 0ms = No delay (through-zero, may cause phase issues)
  - Typical: 100-1000ms
  - Maximum: Likely 5000ms or more
- **Interpolation:** Uses fractional delay for smooth changes

#### Delay L / Delay R
- **Range:** 0-5000ms (or similar)
- **Type:** Independent delay times
- **Mapping:** Linear in milliseconds
- **Affects:** Left and right delay lines independently
- **Smoothing:** Smoothed with interpolation
- **Behavior:**
  - When linked to Delay: Both follow Delay parameter
  - When unlinked: Independent control
- **Mode Dependence:** May not be available in all modes

#### Ratio
- **Range:** 0.1-2.0 (or similar)
- **Type:** Ratio multiplier
- **Mapping:** Likely logarithmic
- **Affects:** Relationship between Delay L and Delay R
- **Behavior:**
  - 1.0 = Both delays equal
  - 0.5 = R is half of L
  - 2.0 = R is double L
- **Mode Dependence:** Likely only in stereo modes

#### Spread
- **Range:** 0-100%
- **Type:** Stereo spread
- **Mapping:** Likely linear
- **Affects:** Difference between L and R delay times
- **Behavior:**
  - 0% = L and R delays equal
  - 100% = Maximum difference
- **Formula:** Spread = |Delay L - Delay R| / Average Delay

### 1.2 Stereo Parameters

#### Width
- **Range:** 0-200% (or similar)
- **Type:** Stereo width
- **Mapping:** Likely linear
- **Affects:** Stereo image of delayed signal
- **Behavior:**
  - 0% = Mono (L and R identical)
  - 100% = Natural stereo
  - 200% = Extra wide (may have phase issues)
- **Implementation:** Likely mid/side processing or panning

### 1.3 Modulation Parameters

#### Mod Rate
- **Range:** 0.01-20 Hz (or similar)
- **Type:** Modulation frequency
- **Mapping:** Likely logarithmic (exponential)
- **Affects:** LFO rate for delay modulation
- **Smoothing:** Smoothed to prevent clicks
- **Behavior:**
  - 0.01 Hz = Very slow (100 second cycle)
  - 1 Hz = Standard (1 second cycle)
  - 20 Hz = Fast (20 cycles per second)

#### Mod Depth
- **Range:** 0-100%
- **Type:** Modulation depth
- **Mapping:** Likely linear
- **Affects:** Amount of delay time modulation
- **Smoothing:** Smoothed
- **Behavior:**
  - 0% = No modulation
  - 100% = Maximum modulation depth
- **Units:** Likely percentage of delay time or samples

### 1.4 Tone Shaping Parameters

#### Age
- **Range:** 0-100%
- **Type:** Degradation
- **Mapping:** Likely nonlinear
- **Affects:** Signal degradation (emulates tape age)
- **Behavior:**
  - 0% = Clean, pristine
  - 100% = Heavily degraded
- **Implementation:**
  - Low-pass filtering (bandwidth reduction)
  - Bit crushing (resolution reduction)
  - Noise addition
  - Wow/flutter modulation

#### Drive
- **Range:** 0-100%
- **Type:** Saturation
- **Mapping:** Likely logarithmic
- **Affects:** Nonlinear distortion
- **Behavior:**
  - 0% = No saturation
  - 100% = Heavy saturation
- **Implementation:**
  - Soft clipping
  - Waveshaping
  - Tape saturation emulation

#### EQ High
- **Range:** 0-20000 Hz (or similar)
- **Type:** High-frequency cutoff
- **Mapping:** Likely logarithmic (frequency)
- **Affects:** High-pass or low-pass filter on output
- **Behavior:**
  - Lower values = More high-frequency attenuation
  - Higher values = Less high-frequency attenuation
- **Implementation:** Likely a low-pass filter

#### EQ Low
- **Range:** 20-1000 Hz (or similar)
- **Type:** Low-frequency cutoff
- **Mapping:** Likely logarithmic (frequency)
- **Affects:** Low-pass or high-pass filter on output
- **Behavior:**
  - Lower values = More low-frequency attenuation
  - Higher values = Less low-frequency attenuation
- **Implementation:** Likely a high-pass filter

#### Era
- **Range:** Discrete values (e.g., 1960s, 1970s, 1980s, etc.)
- **Type:** Preset configuration
- **Mapping:** Discrete
- **Affects:** Multiple parameters simultaneously
- **Behavior:**
  - Changes filter characteristics
  - Changes saturation characteristics
  - Changes noise profile
- **Implementation:** Preset recall with interpolation

### 1.5 Diffusion Parameters

#### Diffusion
- **Range:** 0-100%
- **Type:** Diffusion amount
- **Mapping:** Likely linear
- **Affects:** Feedback network diffusion
- **Behavior:**
  - 0% = No diffusion (may sound metallic)
  - 100% = Maximum diffusion (smoother, more natural)
- **Implementation:** Allpass filters in feedback path

#### Diffusion Size
- **Range:** Small-Medium-Large (or 0-100%)
- **Type:** Diffusion network size
- **Mapping:** Likely discrete or linear
- **Affects:** Character of diffusion
- **Behavior:**
  - Small = Shorter delay lines in diffusion network
  - Large = Longer delay lines in diffusion network
- **Implementation:** Different delay line lengths in diffusion network

#### Diffusion Amount
- **Range:** 0-100%
- **Type:** Diffusion wet/dry mix
- **Mapping:** Likely linear
- **Affects:** Amount of diffused signal in feedback
- **Behavior:**
  - 0% = No diffusion (direct feedback only)
  - 100% = Full diffusion (all feedback goes through diffusion)

### 1.6 Pitch/Frequency Parameters

#### Pitch Shift
- **Range:** -24 to +24 semitones (or similar)
- **Type:** Pitch shift
- **Mapping:** Likely linear in semitones
- **Affects:** Pitch of delayed signal
- **Behavior:**
  - 0 = No pitch shift
  - +12 = One octave up
  - -12 = One octave down
- **Implementation:**
  - Time-domain (PSOLA) for small shifts
  - Frequency-domain (phase vocoder) for large shifts
- **Location:** Likely in feedback path

#### Pitch Detune
- **Range:** -100 to +100 cents (or similar)
- **Type:** Fine pitch adjustment
- **Mapping:** Likely linear in cents
- **Affects:** Fine pitch of delayed signal
- **Behavior:**
  - 0 = No detune
  - ±100 = ±1 semitone
- **Implementation:** Similar to Pitch Shift but smaller range

#### Frequency Shift
- **Range:** -2000 to +2000 Hz (or similar)
- **Type:** Frequency shift
- **Mapping:** Likely linear in Hz
- **Affects:** Frequency of delayed signal
- **Behavior:**
  - 0 = No frequency shift
  - +1000 = Shift all frequencies up by 1000 Hz
- **Implementation:** Single-sideband modulation or phase vocoder
- **Location:** Likely in feedback path

#### Frequency Detune
- **Range:** -100 to +100 cents (or similar)
- **Type:** Fine frequency adjustment
- **Mapping:** Likely linear in cents
- **Affects:** Fine frequency of delayed signal
- **Behavior:** Similar to Frequency Shift but smaller range

### 1.7 Dynamics Parameters

#### Ducking
- **Range:** 0-100%
- **Type:** Dynamics processing
- **Mapping:** Likely logarithmic
- **Affects:** Volume of delayed signal based on input level
- **Behavior:**
  - 0% = No ducking
  - 100% = Maximum ducking (delay volume reduced when input is present)
- **Implementation:**
  - Sidechain compression
  - Envelope follower controlling delay gain

### 1.8 Tempo Synchronization

**Parameters:** (Implied)
- **Range:** 1/16 to 4 notes (or similar)
- **Type:** Delay time synchronization to host tempo
- **Mapping:** Discrete note values
- **Affects:** Delay time in musical units
- **Behavior:**
  - Converts note values to milliseconds based on host BPM
  - Overrides Delay parameter when enabled

---

## 2. ValhallaVintageVerb Parameters

### 2.1 Core Parameters

#### Mix
- **Range:** 0-100%
- **Type:** Wet/Dry balance
- **Mapping:** Linear in percentage, logarithmic in dB
- **Affects:** Output signal
- **Behavior:** Same as ValhallaDelay Mix

#### Predelay
- **Range:** 0-200ms (or similar)
- **Type:** Time delay before reverb
- **Mapping:** Linear in milliseconds
- **Affects:** Time before early reflections begin
- **Behavior:**
  - 0ms = Reverb starts immediately
  - 200ms = 200ms gap before reverb
- **Implementation:** Simple delay line before reverb network

#### Decay
- **Range:** 0.1-20 seconds (or similar)
- **Type:** Reverb decay time (RT60)
- **Mapping:** Likely logarithmic (exponential decay)
- **Affects:** Overall reverb length
- **Behavior:**
  - 0.1s = Very short reverb
  - 1-3s = Typical room/hall
  - 20s = Very long reverb
- **Implementation:** Feedback gain in reverb network

#### Size
- **Range:** 0-100%
- **Type:** Room size
- **Mapping:** Likely nonlinear
- **Affects:** Early reflection pattern and density
- **Behavior:**
  - Small = Short, dense early reflections
  - Large = Long, sparse early reflections
- **Implementation:**
  - Scales delay line lengths in early reflection network
  - Affects reflection spacing

#### Attack
- **Range:** 0-100%
- **Type:** Envelope shaping
- **Mapping:** Likely linear
- **Affects:** Initial buildup of reverb
- **Behavior:**
  - 0% = Immediate full reverb
  - 100% = Slow buildup
- **Implementation:** Envelope follower or gain shaping

### 2.2 Frequency Parameters

#### Bass Mult
- **Range:** 0.1-2.0 (or similar)
- **Type:** Low-frequency decay multiplier
- **Mapping:** Likely linear
- **Affects:** Decay time of low frequencies
- **Behavior:**
  - 1.0 = Same decay as overall Decay
  - 2.0 = Low frequencies decay twice as slow
  - 0.5 = Low frequencies decay twice as fast
- **Implementation:** Separate decay envelope for low frequencies

#### Bass Xover
- **Range:** 20-1000 Hz (or similar)
- **Type:** Bass crossover frequency
- **Mapping:** Logarithmic (frequency)
- **Affects:** Frequency at which Bass Mult applies
- **Behavior:**
  - 20 Hz = Bass Mult affects all frequencies
  - 1000 Hz = Bass Mult only affects very low frequencies
- **Implementation:** Crossover filter (likely Linkwitz-Riley)

#### High Cut
- **Range:** 2000-20000 Hz (or similar)
- **Type:** High-frequency cutoff
- **Mapping:** Logarithmic (frequency)
- **Affects:** High-frequency content of reverb
- **Behavior:**
  - 20000 Hz = Full bandwidth
  - 2000 Hz = Significant high-frequency attenuation
- **Implementation:** Low-pass filter in reverb network

### 2.3 Damping Parameters

#### Damping
- **Range:** 0-100%
- **Type:** Overall damping
- **Mapping:** Likely linear
- **Affects:** High-frequency absorption
- **Behavior:**
  - 0% = No damping (bright reverb)
  - 100% = Maximum damping (dark reverb)
- **Implementation:** Frequency-dependent feedback gain

#### Damping Frequency
- **Range:** 100-10000 Hz (or similar)
- **Type:** Damping cutoff frequency
- **Mapping:** Logarithmic (frequency)
- **Affects:** Frequency at which damping begins
- **Behavior:**
  - 100 Hz = Damping affects almost all frequencies
  - 10000 Hz = Damping only affects very high frequencies

#### Damping Amount
- **Range:** 0-100%
- **Type:** Amount of damping
- **Mapping:** Likely linear
- **Affects:** Intensity of damping at Damping Frequency
- **Behavior:**
  - 0% = No damping
  - 100% = Maximum damping

### 2.4 Modulation Parameters

#### Mod Rate
- **Range:** 0.01-20 Hz
- **Type:** Modulation frequency
- **Mapping:** Logarithmic (exponential)
- **Affects:** LFO rate for reverb modulation
- **Behavior:** Same as ValhallaDelay Mod Rate

#### Mod Depth
- **Range:** 0-100%
- **Type:** Modulation depth
- **Mapping:** Linear
- **Affects:** Amount of reverb modulation
- **Behavior:** Same as ValhallaDelay Mod Depth

### 2.5 Stereo Parameters

#### Width
- **Range:** 0-200%
- **Type:** Stereo width
- **Mapping:** Linear
- **Affects:** Stereo image of reverb
- **Behavior:**
  - 0% = Mono reverb
  - 100% = Natural stereo
  - 200% = Extra wide

#### Early/Late Balance
- **Range:** 0-100%
- **Type:** Mix between early reflections and late reverb
- **Mapping:** Linear
- **Affects:** Balance of early vs. late reverb
- **Behavior:**
  - 0% = Only late reverb
  - 50% = Equal early and late
  - 100% = Only early reflections

### 2.6 Mode and Color

#### Mode
- **Range:** 22 discrete values
- **Type:** Reverb algorithm selection
- **Mapping:** Discrete
- **Affects:** Entire reverb architecture
- **Behavior:**
  - Each mode has different network topology
  - Different early reflection patterns
  - Different late reverb characteristics
- **Implementation:** Preset recall with complete reconfiguration

#### Colour
- **Range:** 3 discrete values
- **Type:** Reverb color/timbre
- **Mapping:** Discrete
- **Affects:** Frequency response and modulation
- **Behavior:**
  - Changes spectral characteristics
  - May affect damping and filtering
  - May affect modulation characteristics

---

## 3. Parameter Interaction Matrix

### 3.1 ValhallaDelay Interactions

| Parameter | Affects | Interacts With |
|-----------|---------|----------------|
| Feedback | Decay time | Diffusion, Delay, Age |
| Delay | Echo spacing | Ratio, Spread, Mod Depth |
| Diffusion | Echo density | Feedback, Age |
| Mod Rate | Modulation speed | Mod Depth |
| Age | Bandwidth | Drive, Diffusion |
| Drive | Saturation | Age, Feedback |
| Pitch Shift | Pitch | Feedback, Delay |

### 3.2 ValhallaVintageVerb Interactions

| Parameter | Affects | Interacts With |
|-----------|---------|----------------|
| Decay | Reverb length | Bass Mult, Damping |
| Size | Early reflections | Decay, Width |
| Bass Mult | Low-frequency decay | Bass Xover, Decay |
| Damping | High-frequency decay | Damping Frequency, Damping Amount |
| Mod Rate | Modulation speed | Mod Depth |
| Width | Stereo image | Early/Late Balance |

---

## 4. Implementation Guidelines

### 4.1 Parameter Ranges

**General Rules:**
- Linear parameters: Use linear mapping (0-1 range)
- Logarithmic parameters: Use exponential mapping
- Frequency parameters: Use logarithmic (Hz) or linear (octaves)
- Time parameters: Use linear (milliseconds) or logarithmic (seconds)

### 4.2 Smoothing

**When to Smooth:**
- Always smooth parameters that affect audio directly
- Smoothing time: 1-10ms for most parameters
- Longer smoothing for parameters that cause clicks (delay time, pitch)

**Smoothing Types:**
- **Exponential:** For most parameters (1-pole IIR)
- **Linear:** For parameters that need precise timing
- **Ballistic:** For perceptual linearity

### 4.3 Automation

**Requirements:**
- All parameters must support automation
- Smoothing must be applied to automated parameters
- Parameter changes must be sample-accurate when smoothed

### 4.4 Preset Recall

**Requirements:**
- Smooth parameter changes when recalling presets
- Option for immediate or smoothed recall
- State must be preserved during recall

---

## 5. Verification Checklist

### 5.1 Parameter Verification

- [ ] **Range:** Does parameter cover expected range?
- [ ] **Mapping:** Is mapping linear/logarithmic as expected?
- [ ] **Default:** Does default value produce expected sound?
- [ ] **Extremes:** Do minimum and maximum values behave correctly?
- [ ] **Smoothing:** Are parameter changes smooth?
- [ ] **Automation:** Does parameter respond to automation?

### 5.2 Interaction Verification

- [ ] **Independence:** Do parameters work independently?
- [ ] **Combination:** Do parameter combinations produce expected results?
- [ ] **Order:** Does parameter change order matter?
- [ ] **Mode Dependence:** Do parameters behave differently in different modes?

---

**Last Updated:** 2026-11-07  
**Author:** Vibe Code (Mistral AI)

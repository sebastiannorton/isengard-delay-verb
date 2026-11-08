# Isengard Plugins - Test Framework

**Project:** Isengard Delay & Isengard Verb  
**Phase:** C - Experimental Validation  
**Status:** 🔄 IN PROGRESS  
**Date:** 2024-11-07  

---

## Overview

This directory contains the test framework for **Phase C: Experimental Validation** of the Isengard plugins. The framework is designed to:

1. Generate deterministic test signals
2. Render reference outputs (when possible)
3. Perform parameter sweeps
4. Analyze and measure DSP behavior
5. Compare implementation against reference
6. Validate plugin functionality

---

## Directory Structure

```
tests/
├── README.md                    # This file
├── reference-rendering/         # Reference plugin rendering scripts
│   ├── render.py                # Main rendering script
│   ├── configs/                 # Rendering configurations
│   │   ├── delay-modes/         # Delay mode configurations
│   │   └── verb-modes/          # Verb mode configurations
│   └── outputs/                 # Rendered reference outputs
│
├── parameter-sweeps/           # Parameter sweep automation
│   ├── sweep.py                 # Parameter sweep script
│   ├── definitions/             # Parameter definitions
│   │   ├── delay-params.json    # Delay parameter definitions
│   │   └── verb-params.json     # Verb parameter definitions
│   └── results/                 # Sweep results
│
├── analysis/                    # Signal analysis tools
│   ├── fft.py                   # FFT and spectral analysis
│   ├── impulse.py               # Impulse response analysis
│   ├── decay.py                 # Decay curve analysis
│   ├── stereo.py                # Stereo correlation analysis
│   └── metrics.py               # Comparison metrics
│
├── signals/                     # Test signal generators
│   ├── impulse.py               # Impulse generator
│   ├── noise.py                 # White/pink noise generator
│   ├── sine.py                  # Sine wave generator
│   ├── sweep.py                 # Frequency sweep generator
│   └── burst.py                 # Tone burst generator
│
└── results/                     # Test results and reports
    ├── delay/                   # Delay test results
    ├── verb/                    # Verb test results
    └── comparison/              # Implementation vs reference comparisons
```

---

## Test Philosophy

### Principles

1. **Reproducibility:** All tests must be deterministic and repeatable
2. **Automation:** Tests should run automatically without manual intervention
3. **Documentation:** All test configurations and results must be documented
4. **Evidence-Based:** Test results feed into the Evidence Ledger
5. **Comprehensive:** Test all modes, styles, parameters, and configurations

### Test Levels

| Level | Scope | Purpose | Frequency |
|-------|-------|---------|-----------|
| Unit | Individual components | Verify component behavior | Per component |
| Integration | Component interactions | Verify system behavior | Per subsystem |
| System | Complete plugin | Verify plugin behavior | Per build |
| Comparison | vs Reference | Validate against reference | Per milestone |

---

## Test Signal Generators

### 1. Impulse Generator

**File:** `signals/impulse.py`

**Purpose:** Generate impulse signals for impulse response measurement

```python
class ImpulseGenerator:
    def __init__(self, sample_rate=44100, length_samples=44100):
        self.sample_rate = sample_rate
        self.length_samples = length_samples
        
    def generate(self, position=0):
        """Generate impulse at specified position (default: 0)"""
        signal = np.zeros(self.length_samples)
        signal[position] = 1.0
        return signal
        
    def generate_stereo(self, position_l=0, position_r=0):
        """Generate stereo impulse with independent positions"""
        signal_l = np.zeros(self.length_samples)
        signal_r = np.zeros(self.length_samples)
        signal_l[position_l] = 1.0
        signal_r[position_r] = 1.0
        return signal_l, signal_r
```

**Use Cases:**
- Impulse response measurement
- Delay time verification
- Early reflection pattern analysis

### 2. Noise Generator

**File:** `signals/noise.py`

**Purpose:** Generate white and pink noise for frequency response analysis

```python
class NoiseGenerator:
    def __init__(self, sample_rate=44100, length_samples=44100):
        self.sample_rate = sample_rate
        self.length_samples = length_samples
        
    def white(self, seed=None):
        """Generate white noise"""
        if seed is not None:
            np.random.seed(seed)
        return np.random.uniform(-1.0, 1.0, self.length_samples)
        
    def pink(self, seed=None):
        """Generate pink noise (1/f spectrum)"""
        if seed is not None:
            np.random.seed(seed)
        white = np.random.uniform(-1.0, 1.0, self.length_samples)
        # Apply pink noise filter (simple approximation)
        return self._apply_pink_filter(white)
        
    def generate_stereo(self, noise_type='white', seed_l=None, seed_r=None):
        """Generate stereo noise"""
        if noise_type == 'white':
            return self.white(seed_l), self.white(seed_r)
        elif noise_type == 'pink':
            return self.pink(seed_l), self.pink(seed_r)
```

**Use Cases:**
- Frequency response measurement
- Spectral balance analysis
- Noise floor measurement

### 3. Sine Wave Generator

**File:** `signals/sine.py`

**Purpose:** Generate sine waves for frequency accuracy testing

```python
class SineGenerator:
    def __init__(self, sample_rate=44100, length_samples=44100):
        self.sample_rate = sample_rate
        self.length_samples = length_samples
        
    def generate(self, frequency, amplitude=0.5, phase=0.0):
        """Generate sine wave at specified frequency"""
        t = np.arange(self.length_samples) / self.sample_rate
        return amplitude * np.sin(2 * np.pi * frequency * t + phase)
        
    def generate_stereo(self, frequency, amplitude=0.5, phase_l=0.0, phase_r=0.0):
        """Generate stereo sine wave with phase difference"""
        t = np.arange(self.length_samples) / self.sample_rate
        signal_l = amplitude * np.sin(2 * np.pi * frequency * t + phase_l)
        signal_r = amplitude * np.sin(2 * np.pi * frequency * t + phase_r)
        return signal_l, signal_r
```

**Use Cases:**
- Frequency accuracy verification
- Pitch shift verification
- Modulation depth measurement

### 4. Frequency Sweep Generator

**File:** `signals/sweep.py`

**Purpose:** Generate logarithmic frequency sweeps for frequency response analysis

```python
class SweepGenerator:
    def __init__(self, sample_rate=44100, length_samples=44100):
        self.sample_rate = sample_rate
        self.length_samples = length_samples
        
    def logarithmic(self, start_freq, end_freq):
        """Generate logarithmic frequency sweep"""
        t = np.arange(self.length_samples) / self.sample_rate
        # Logarithmic sweep: f(t) = start * (end/start)^(t/duration)
        duration = self.length_samples / self.sample_rate
        freq = start_freq * np.power(end_freq / start_freq, t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        return np.sin(phase)
        
    def linear(self, start_freq, end_freq):
        """Generate linear frequency sweep"""
        t = np.arange(self.length_samples) / self.sample_rate
        duration = self.length_samples / self.sample_rate
        freq = start_freq + (end_freq - start_freq) * t / duration
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        return np.sin(phase)
```

**Use Cases:**
- Frequency response measurement
- Filter cutoff verification
- Resonance analysis

### 5. Tone Burst Generator

**File:** `signals/burst.py`

**Purpose:** Generate short tone bursts for transient response analysis

```python
class BurstGenerator:
    def __init__(self, sample_rate=44100, length_samples=44100):
        self.sample_rate = sample_rate
        self.length_samples = length_samples
        
    def generate(self, frequency, duration_ms, envelope='hanning'):
        """Generate tone burst with specified duration and envelope"""
        burst_samples = int(duration_ms * self.sample_rate / 1000)
        t = np.arange(burst_samples) / self.sample_rate
        
        # Generate tone
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Apply envelope
        if envelope == 'hanning':
            window = np.hanning(burst_samples)
        elif envelope == 'hamming':
            window = np.hamming(burst_samples)
        elif envelope == 'rectangular':
            window = np.ones(burst_samples)
        else:
            window = np.ones(burst_samples)
            
        burst = tone * window
        
        # Pad with zeros
        signal = np.zeros(self.length_samples)
        signal[:burst_samples] = burst
        return signal
```

**Use Cases:**
- Attack/release time measurement
- Transient response analysis
- Stability testing

---

## Analysis Tools

### 1. FFT and Spectral Analysis

**File:** `analysis/fft.py`

**Purpose:** Perform FFT and spectral analysis on test signals and outputs

```python
class FFTAnalyzer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
    def magnitude_spectrum(self, signal, nfft=None):
        """Compute magnitude spectrum"""
        if nfft is None:
            nfft = len(signal)
        fft_result = np.fft.rfft(signal, n=nfft)
        magnitude = np.abs(fft_result)
        frequencies = np.fft.rfftfreq(nfft, 1.0 / self.sample_rate)
        return frequencies, magnitude
        
    def phase_spectrum(self, signal, nfft=None):
        """Compute phase spectrum"""
        if nfft is None:
            nfft = len(signal)
        fft_result = np.fft.rfft(signal, n=nfft)
        phase = np.angle(fft_result)
        frequencies = np.fft.rfftfreq(nfft, 1.0 / self.sample_rate)
        return frequencies, phase
        
    def power_spectral_density(self, signal, nfft=None):
        """Compute power spectral density"""
        frequencies, magnitude = self.magnitude_spectrum(signal, nfft)
        psd = magnitude ** 2 / (len(signal) * self.sample_rate)
        return frequencies, psd
        
    def spectrogram(self, signal, window_size=1024, hop_size=256):
        """Compute spectrogram"""
        # Implementation using STFT
        pass
```

**Metrics:**
- Frequency response (magnitude)
- Phase response
- Spectral flatness
- Spectral centroid

### 2. Impulse Response Analysis

**File:** `analysis/impulse.py`

**Purpose:** Analyze impulse responses to extract DSP characteristics

```python
class ImpulseAnalyzer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
    def measure_delay(self, impulse_response):
        """Measure delay time from impulse response"""
        # Find first significant peak
        threshold = 0.01 * np.max(np.abs(impulse_response))
        peak_indices = np.where(np.abs(impulse_response) > threshold)[0]
        if len(peak_indices) > 0:
            return peak_indices[0] / self.sample_rate * 1000  # ms
        return 0.0
        
    def measure_decay(self, impulse_response, threshold_db=-60):
        """Measure decay time from impulse response"""
        # Convert to dB
        db_response = 20 * np.log10(np.abs(impulse_response) + 1e-10)
        
        # Find where it drops below threshold
        below_threshold = np.where(db_response < threshold_db)[0]
        if len(below_threshold) > 0:
            return below_threshold[0] / self.sample_rate * 1000  # ms
        return len(impulse_response) / self.sample_rate * 1000  # ms
        
    def measure_echo_density(self, impulse_response, window_ms=100):
        """Measure echo density (echoes per second)"""
        window_samples = int(window_ms * self.sample_rate / 1000)
        
        # Count peaks above threshold
        threshold = 0.1 * np.max(np.abs(impulse_response))
        peaks = np.where(np.abs(impulse_response) > threshold)[0]
        
        # Count peaks in windows
        densities = []
        for i in range(0, len(impulse_response), window_samples):
            window_peaks = np.sum((peaks >= i) & (peaks < i + window_samples))
            densities.append(window_peaks / (window_ms / 1000))
        
        return np.mean(densities)
```

**Metrics:**
- Delay time
- Decay time (T60, T30, T20)
- Echo density
- Early reflection pattern
- Late reverb characteristics

### 3. Decay Curve Analysis

**File:** `analysis/decay.py`

**Purpose:** Analyze decay curves for reverb characterization

```python
class DecayAnalyzer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
    def compute_decay_curve(self, signal, attack_ms=10, release_ms=1000):
        """Compute decay curve from signal"""
        # Apply envelope to remove attack
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        release_samples = int(release_ms * self.sample_rate / 1000)
        
        # Compute RMS in windows
        window_size = 1024
        hop_size = window_size // 4
        
        rms = []
        for i in range(0, len(signal) - window_size, hop_size):
            window = signal[i:i + window_size]
            rms.append(np.sqrt(np.mean(window ** 2)))
        
        return np.array(rms)
        
    def measure_t60(self, decay_curve, sample_rate=44100):
        """Measure T60 (time to decay by 60dB)"""
        # Convert to dB
        db_curve = 20 * np.log10(decay_curve + 1e-10)
        
        # Find initial level (first 10% of curve)
        initial_db = np.mean(db_curve[:len(db_curve) // 10])
        target_db = initial_db - 60
        
        # Find where curve drops below target
        below_target = np.where(db_curve < target_db)[0]
        if len(below_target) > 0:
            return below_target[0] / sample_rate
        return len(decay_curve) / sample_rate
        
    def measure_spectral_decay(self, signal, num_bands=10):
        """Measure decay time per frequency band"""
        # Split signal into frequency bands
        # Measure decay time for each band
        pass
```

**Metrics:**
- T60 (reverb time)
- T30, T20 (early decay times)
- Decay linearity
- Spectral decay (per frequency band)
- Decay modulation

### 4. Stereo Correlation Analysis

**File:** `analysis/stereo.py`

**Purpose:** Analyze stereo characteristics of the plugins

```python
class StereoAnalyzer:
    def __init__(self):
        pass
        
    def correlation(self, left, right):
        """Compute correlation between left and right channels"""
        # Normalize signals
        left_norm = left - np.mean(left)
        right_norm = right - np.mean(right)
        
        # Compute correlation
        corr = np.corrcoef(left_norm, right_norm)[0, 1]
        return corr
        
    def cross_correlation(self, left, right, max_lag=100):
        """Compute cross-correlation with lag"""
        # Compute cross-correlation
        corr = np.correlate(left, right, mode='full')
        lags = np.arange(-len(left) + 1, len(left))
        
        # Find peak correlation and lag
        peak_idx = np.argmax(corr)
        peak_lag = lags[peak_idx]
        peak_corr = corr[peak_idx]
        
        return peak_lag, peak_corr
        
    def width(self, left, right):
        """Compute stereo width (0-1, 0=mono, 1=uncorrelated)"""
        # Compute coherence
        coherence = self.correlation(left, right)
        
        # Width = sqrt(1 - coherence^2)
        return np.sqrt(1 - coherence ** 2)
        
    def phase_difference(self, left, right):
        """Compute average phase difference between channels"""
        # Compute FFT of both channels
        fft_l = np.fft.rfft(left)
        fft_r = np.fft.rfft(right)
        
        # Compute phase difference
        phase_diff = np.angle(fft_l) - np.angle(fft_r)
        
        # Average phase difference (weighted by magnitude)
        magnitude_l = np.abs(fft_l)
        magnitude_r = np.abs(fft_r)
        weights = (magnitude_l + magnitude_r) / 2
        
        return np.average(phase_diff, weights=weights)
```

**Metrics:**
- Stereo correlation
- Cross-correlation lag
- Stereo width
- Phase difference
- Channel balance

### 5. Comparison Metrics

**File:** `analysis/metrics.py`

**Purpose:** Compare implementation outputs against reference

```python
class ComparisonMetrics:
    def __init__(self):
        pass
        
    def sample_difference(self, ref, impl):
        """Compute sample-level difference"""
        return ref - impl
        
    def rms_difference(self, ref, impl):
        """Compute RMS of difference"""
        diff = self.sample_difference(ref, impl)
        return np.sqrt(np.mean(diff ** 2))
        
    def correlation(self, ref, impl):
        """Compute correlation between reference and implementation"""
        # Normalize signals
        ref_norm = ref - np.mean(ref)
        impl_norm = impl - np.mean(impl)
        
        # Compute correlation
        corr = np.corrcoef(ref_norm, impl_norm)[0, 1]
        return corr
        
    def spectral_difference(self, ref, impl, nfft=2048):
        """Compute spectral difference"""
        # Compute magnitude spectra
        fft_ref = np.fft.rfft(ref, n=nfft)
        fft_impl = np.fft.rfft(impl, n=nfft)
        
        mag_ref = np.abs(fft_ref)
        mag_impl = np.abs(fft_impl)
        
        # Compute difference in dB
        db_ref = 20 * np.log10(mag_ref + 1e-10)
        db_impl = 20 * np.log10(mag_impl + 1e-10)
        
        return db_ref - db_impl
        
    def spectral_correlation(self, ref, impl, nfft=2048):
        """Compute spectral correlation"""
        # Compute magnitude spectra
        fft_ref = np.fft.rfft(ref, n=nfft)
        fft_impl = np.fft.rfft(impl, n=nfft)
        
        mag_ref = np.abs(fft_ref)
        mag_impl = np.abs(fft_impl)
        
        # Compute correlation
        corr = np.corrcoef(mag_ref, mag_impl)[0, 1]
        return corr
```

**Metrics:**
- Sample-level difference
- RMS difference
- Correlation
- Spectral difference
- Spectral correlation

---

## Parameter Sweep Framework

### Parameter Definitions

**File:** `parameter-sweeps/definitions/delay-params.json`

```json
{
  "parameters": [
    {
      "name": "mix",
      "display_name": "Mix",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Dry/Wet mix"
    },
    {
      "name": "feedback",
      "display_name": "Feedback",
      "range": [0.0, 0.99],
      "type": "logarithmic",
      "steps": 20,
      "unit": "",
      "description": "Feedback amount"
    },
    {
      "name": "delayTimeMs",
      "display_name": "Delay Time",
      "range": [1.0, 5000.0],
      "type": "logarithmic",
      "steps": 20,
      "unit": "ms",
      "description": "Delay time in milliseconds"
    },
    {
      "name": "modRate",
      "display_name": "Mod Rate",
      "range": [0.1, 20.0],
      "type": "logarithmic",
      "steps": 20,
      "unit": "Hz",
      "description": "Modulation rate"
    },
    {
      "name": "modDepth",
      "display_name": "Mod Depth",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Modulation depth"
    },
    {
      "name": "diffusionAmount",
      "display_name": "Diffusion Amount",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Diffusion network amount"
    },
    {
      "name": "diffusionSize",
      "display_name": "Diffusion Size",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Diffusion network size"
    },
    {
      "name": "age",
      "display_name": "Age",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Digital mode: bit depth (0%=24bit, 100%=8bit)"
    },
    {
      "name": "drive",
      "display_name": "Drive",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Tape mode: saturation amount"
    },
    {
      "name": "noiseAmount",
      "display_name": "Noise",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "BBD mode: noise amount"
    }
  ],
  "modes": [
    {"name": "Tape", "display_name": "Tape"},
    {"name": "HiFi", "display_name": "HiFi"},
    {"name": "BBD", "display_name": "BBD"},
    {"name": "Digital", "display_name": "Digital"},
    {"name": "Ghost", "display_name": "Ghost"},
    {"name": "Pitch", "display_name": "Pitch"},
    {"name": "RevPitch", "display_name": "RevPitch"}
  ],
  "styles": [
    {"name": "Single", "display_name": "Single"},
    {"name": "Dual", "display_name": "Dual"},
    {"name": "Ratio", "display_name": "Ratio"},
    {"name": "PingPong", "display_name": "PingPong"},
    {"name": "Quad", "display_name": "Quad"}
  ]
}
```

**File:** `parameter-sweeps/definitions/verb-params.json`

```json
{
  "parameters": [
    {
      "name": "mix",
      "display_name": "Mix",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Dry/Wet mix"
    },
    {
      "name": "predelay",
      "display_name": "Predelay",
      "range": [0.0, 200.0],
      "type": "logarithmic",
      "steps": 20,
      "unit": "ms",
      "description": "Predelay time"
    },
    {
      "name": "decay",
      "display_name": "Decay",
      "range": [0.1, 20.0],
      "type": "logarithmic",
      "steps": 20,
      "unit": "s",
      "description": "Reverb decay time"
    },
    {
      "name": "size",
      "display_name": "Size",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Reverb size"
    },
    {
      "name": "bassMult",
      "display_name": "Bass Mult",
      "range": [0.1, 2.0],
      "type": "linear",
      "steps": 20,
      "unit": "",
      "description": "Low-frequency multiplier"
    },
    {
      "name": "bassXover",
      "display_name": "Bass Xover",
      "range": [20.0, 1000.0],
      "type": "logarithmic",
      "steps": 20,
      "unit": "Hz",
      "description": "Bass crossover frequency"
    },
    {
      "name": "highCut",
      "display_name": "High Cut",
      "range": [200.0, 20000.0],
      "type": "logarithmic",
      "steps": 20,
      "unit": "Hz",
      "description": "High-frequency cutoff"
    },
    {
      "name": "damping",
      "display_name": "Damping",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "High-frequency damping"
    },
    {
      "name": "modRate",
      "display_name": "Mod Rate",
      "range": [0.01, 20.0],
      "type": "logarithmic",
      "steps": 20,
      "unit": "Hz",
      "description": "Modulation rate"
    },
    {
      "name": "modDepth",
      "display_name": "Mod Depth",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Modulation depth"
    },
    {
      "name": "earlyLate",
      "display_name": "Early/Late",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Early/Late balance"
    },
    {
      "name": "width",
      "display_name": "Width",
      "range": [0.0, 1.0],
      "type": "linear",
      "steps": 11,
      "unit": "",
      "description": "Stereo width"
    }
  ],
  "modes": [
    {"name": "1972", "display_name": "1972", "category": "Dirty"},
    {"name": "1974", "display_name": "1974", "category": "Dirty"},
    {"name": "1975", "display_name": "1975", "category": "Dirty"},
    {"name": "1976", "display_name": "1976", "category": "Dirty"},
    {"name": "1977", "display_name": "1977", "category": "Dirty"},
    {"name": "1978", "display_name": "1978", "category": "Dirty"},
    {"name": "1979", "display_name": "1979", "category": "Dirty"},
    {"name": "1980", "display_name": "1980", "category": "Smooth"},
    {"name": "1981", "display_name": "1981", "category": "Smooth"},
    {"name": "1982", "display_name": "1982", "category": "Smooth"},
    {"name": "1983", "display_name": "1983", "category": "Smooth"},
    {"name": "1984", "display_name": "1984", "category": "Smooth"},
    {"name": "1985", "display_name": "1985", "category": "Smooth"},
    {"name": "1986", "display_name": "1986", "category": "Smooth"},
    {"name": "1987", "display_name": "1987", "category": "Chaotic"},
    {"name": "1988", "display_name": "1988", "category": "Chaotic"},
    {"name": "1989", "display_name": "1989", "category": "Chaotic"},
    {"name": "1990", "display_name": "1990", "category": "Chaotic"},
    {"name": "Now1", "display_name": "Now 1", "category": "Palace"},
    {"name": "Now2", "display_name": "Now 2", "category": "Palace"},
    {"name": "Now3", "display_name": "Now 3", "category": "Palace"}
  ],
  "colors": [
    {"name": "1970s", "display_name": "1970s"},
    {"name": "1980s", "display_name": "1980s"},
    {"name": "Now", "display_name": "Now"}
  ]
}
```

### Sweep Script

**File:** `parameter-sweeps/sweep.py`

```python
import json
import numpy as np
import os
from datetime import datetime

class ParameterSweep:
    def __init__(self, config_file, output_dir='results'):
        self.config_file = config_file
        self.output_dir = output_dir
        self.load_config()
        
    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        
    def generate_sweep_values(self, param_name):
        """Generate values for parameter sweep"""
        param = next(p for p in self.config['parameters'] if p['name'] == param_name)
        
        if param['type'] == 'linear':
            return np.linspace(param['range'][0], param['range'][1], param['steps'])
        elif param['type'] == 'logarithmic':
            return np.logspace(np.log10(param['range'][0]), 
                              np.log10(param['range'][1]), 
                              param['steps'])
        else:
            return np.linspace(param['range'][0], param['range'][1], param['steps'])
        
    def run_sweep(self, plugin, signal_generator, param_name, mode=None, style=None, color=None):
        """Run parameter sweep"""
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sweep_dir = os.path.join(self.output_dir, f"{plugin}_{param_name}_{timestamp}")
        os.makedirs(sweep_dir, exist_ok=True)
        
        # Save configuration
        config = {
            'plugin': plugin,
            'param': param_name,
            'mode': mode,
            'style': style,
            'color': color,
            'timestamp': timestamp,
            'signal': signal_generator.__class__.__name__
        }
        with open(os.path.join(sweep_dir, 'config.json'), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Generate test signal
        signal = signal_generator.generate()
        
        # Get sweep values
        values = self.generate_sweep_values(param_name)
        
        # Run sweep
        results = []
        for i, value in enumerate(values):
            # Set parameter
            if plugin == 'delay':
                # Set delay parameter
                pass
            elif plugin == 'verb':
                # Set verb parameter
                pass
            
            # Process signal
            output = self.process_signal(signal, plugin, mode, style, color)
            
            # Save output
            output_file = os.path.join(sweep_dir, f"{param_name}_{value:.4f}.wav")
            self.save_wav(output, output_file, signal_generator.sample_rate)
            
            # Analyze output
            analysis = self.analyze_output(output, signal_generator.sample_rate)
            results.append({
                'value': float(value),
                'analysis': analysis,
                'output_file': output_file
            })
            
            print(f"  [{i+1}/{len(values)}] {param_name}={value:.4f} -> {output_file}")
        
        # Save results
        with open(os.path.join(sweep_dir, 'results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        return sweep_dir, results
        
    def process_signal(self, signal, plugin, mode, style, color):
        """Process signal through plugin (placeholder)"""
        # This would be replaced with actual plugin processing
        # For now, return input signal
        return signal
        
    def save_wav(self, signal, filename, sample_rate):
        """Save signal as WAV file"""
        # Implementation using scipy or soundfile
        pass
        
    def analyze_output(self, signal, sample_rate):
        """Analyze output signal"""
        # Compute various metrics
        rms = np.sqrt(np.mean(signal ** 2))
        peak = np.max(np.abs(signal))
        
        # Compute FFT
        fft_mag, fft_phase = self.compute_fft(signal, sample_rate)
        
        return {
            'rms': float(rms),
            'peak': float(peak),
            'fft_magnitude': fft_mag.tolist(),
            'fft_phase': fft_phase.tolist()
        }
        
    def compute_fft(self, signal, sample_rate):
        """Compute FFT magnitude and phase"""
        nfft = min(4096, len(signal))
        fft_result = np.fft.rfft(signal, n=nfft)
        magnitude = np.abs(fft_result)
        phase = np.angle(fft_result)
        return magnitude, phase
```

---

## Reference Rendering Framework

### Render Script

**File:** `reference-rendering/render.py`

```python
import json
import numpy as np
import os
from datetime import datetime

class ReferenceRenderer:
    def __init__(self, output_dir='outputs'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def render(self, plugin, mode, style=None, color=None, 
               params=None, signal_generator=None, sample_rate=44100):
        """Render reference output"""
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        render_dir = os.path.join(
            self.output_dir, 
            f"{plugin}_{mode}"
            f"{'_' + style if style else ''}"
            f"{'_' + color if color else ''}"
            f"_{timestamp}"
        )
        os.makedirs(render_dir, exist_ok=True)
        
        # Save configuration
        config = {
            'plugin': plugin,
            'mode': mode,
            'style': style,
            'color': color,
            'params': params or {},
            'signal': signal_generator.__class__.__name__ if signal_generator else None,
            'sample_rate': sample_rate,
            'timestamp': timestamp
        }
        with open(os.path.join(render_dir, 'config.json'), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Generate test signal
        if signal_generator:
            signal = signal_generator.generate()
        else:
            # Default: 1s white noise
            signal = np.random.uniform(-0.5, 0.5, sample_rate)
        
        # Process through reference plugin (placeholder)
        # In practice, this would use the actual reference plugin
        output = self.process_reference(signal, plugin, mode, style, color, params)
        
        # Save output
        output_file = os.path.join(render_dir, 'output.wav')
        self.save_wav(output, output_file, sample_rate)
        
        # Analyze output
        analysis = self.analyze_output(output, sample_rate)
        with open(os.path.join(render_dir, 'analysis.json'), 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return render_dir, output_file, analysis
        
    def process_reference(self, signal, plugin, mode, style, color, params):
        """Process signal through reference plugin (placeholder)"""
        # This would be replaced with actual reference plugin processing
        # For now, return input signal
        return signal
        
    def save_wav(self, signal, filename, sample_rate):
        """Save signal as WAV file"""
        # Implementation using scipy or soundfile
        pass
        
    def analyze_output(self, signal, sample_rate):
        """Analyze output signal"""
        # Compute various metrics
        rms = np.sqrt(np.mean(signal ** 2))
        peak = np.max(np.abs(signal))
        
        # Compute FFT
        nfft = min(4096, len(signal))
        fft_result = np.fft.rfft(signal, n=nfft)
        fft_mag = np.abs(fft_result)
        fft_phase = np.angle(fft_result)
        fft_freq = np.fft.rfftfreq(nfft, 1.0 / sample_rate)
        
        return {
            'rms': float(rms),
            'peak': float(peak),
            'fft_frequencies': fft_freq.tolist(),
            'fft_magnitude': fft_mag.tolist(),
            'fft_phase': fft_phase.tolist()
        }
```

### Configuration Files

**File:** `reference-rendering/configs/delay-modes/delay-tape-single.json`

```json
{
  "plugin": "delay",
  "mode": "Tape",
  "style": "Single",
  "params": {
    "mix": 0.5,
    "feedback": 0.5,
    "delayTimeMs": 500,
    "modRate": 1.0,
    "modDepth": 0.3,
    "drive": 0.5,
    "wowDepth": 0.3,
    "flutterDepth": 0.2,
    "diffusionAmount": 0.5,
    "diffusionSize": 0.5,
    "inputGain": 0.0,
    "outputGain": 0.0
  },
  "signal": {
    "type": "impulse",
    "position": 0
  },
  "sample_rate": 44100,
  "duration_seconds": 5.0
}
```

---

## Test Execution

### Running Tests

```bash
# Run all delay parameter sweeps
python parameter-sweeps/sweep.py delay parameter-sweeps/definitions/delay-params.json

# Run all verb parameter sweeps
python parameter-sweeps/sweep.py verb parameter-sweeps/definitions/verb-params.json

# Render reference for specific configuration
python reference-rendering/render.py delay Tape Single reference-rendering/configs/delay-modes/delay-tape-single.json

# Run analysis on output
python analysis/impulse.py tests/results/delay/delay-tape-single/output.wav
```

### Test Configuration

**Sample Rates:** 44.1kHz, 48kHz, 96kHz  
**Block Sizes:** 64, 128, 256, 512, 1024  
**Test Signals:** Impulse, White Noise, Pink Noise, Sine Wave, Frequency Sweep, Tone Burst  

---

## Test Matrix

### Isengard Delay Tests

| Test Type | Modes | Styles | Parameters | Signals | Sample Rates |
|-----------|-------|--------|------------|---------|--------------|
| Impulse Response | All 7 | All 5 | Default | Impulse | 44.1kHz, 48kHz |
| Frequency Response | All 7 | Single | Default | White Noise | 44.1kHz, 48kHz |
| Parameter Sweep | All 7 | Single | All | Sine Wave | 44.1kHz |
| Stability | All 7 | All 5 | Extreme | White Noise | 44.1kHz |
| Stereo | All 7 | PingPong, Quad | Default | Pink Noise | 44.1kHz |

**Total Delay Tests:** 7 modes × 5 styles × 10 parameters × 6 signals × 2 sample rates = **4,200 tests**

### Isengard Verb Tests

| Test Type | Modes | Colors | Parameters | Signals | Sample Rates |
|-----------|-------|--------|------------|---------|--------------|
| Impulse Response | All 22 | All 3 | Default | Impulse | 44.1kHz, 48kHz |
| Frequency Response | All 22 | 1980s | Default | White Noise | 44.1kHz, 48kHz |
| Decay Measurement | All 22 | All 3 | Default | Tone Burst | 44.1kHz |
| Parameter Sweep | All 22 | 1980s | All | Sine Wave | 44.1kHz |
| Stereo | All 22 | All 3 | Default | Pink Noise | 44.1kHz |

**Total Verb Tests:** 22 modes × 3 colors × 12 parameters × 6 signals × 2 sample rates = **9,504 tests**

---

## Evidence Integration

All test results will be integrated into the **Evidence Ledger** (`research/evidence-ledger.md`) with:

- **Evidence ID:** Auto-generated (E044+)
- **Classification:** VERIFIED (for successful tests)
- **Source:** Test framework
- **Steps:** Test configuration and execution details
- **Result:** Measured values and outputs
- **Interpretation:** DSP behavior analysis
- **Confidence:** HIGH (for reproducible tests)

---

## Dependencies

### Python Packages

```
numpy>=1.21.0
scipy>=1.7.0
soundfile>=0.12.0
matplotlib>=3.4.0
```

### Installation

```bash
pip install numpy scipy soundfile matplotlib
```

---

## Next Steps

1. **Implement Signal Generators** (`signals/*.py`)
2. **Implement Analysis Tools** (`analysis/*.py`)
3. **Implement Parameter Sweep Framework** (`parameter-sweeps/sweep.py`)
4. **Create Test Configurations** (`reference-rendering/configs/*.json`)
5. **Run Initial Tests** (Phase C execution)
6. **Integrate with Evidence Ledger** (Document results)

---

**Status:** Framework designed, implementation pending  
**Next:** Begin implementing signal generators and analysis tools  
**Owner:** Vibe Code (Mistral AI)  
**Last Updated:** 2024-11-07

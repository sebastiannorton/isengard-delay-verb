# Frequency Sweep Signal Generator
# For frequency response analysis

"""
Frequency sweep signal generator for frequency response analysis.

Features:
- Logarithmic frequency sweeps (standard for audio)
- Linear frequency sweeps
- Exponential sweeps
- Mono and stereo generation
- Configurable start/end frequencies
- Configurable sweep duration
- Deterministic output
- Sample-rate independent

Usage:
    from signals.sweep import SweepGenerator
    
    # Create generator
    gen = SweepGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate logarithmic sweep from 20Hz to 20kHz
    signal = gen.logarithmic(start_freq=20.0, end_freq=20000.0)
    
    # Generate linear sweep from 100Hz to 1000Hz
    signal = gen.linear(start_freq=100.0, end_freq=1000.0)
    
    # Generate exponential sweep
    signal = gen.exponential(start_freq=20.0, end_freq=20000.0, exponent=2.0)
    
    # Generate stereo sweep with different ranges
    signal_l, signal_r = gen.generate_stereo(
        start_freq_l=20.0, end_freq_l=20000.0,
        start_freq_r=100.0, end_freq_r=10000.0
    )
"""

import numpy as np


class SweepGenerator:
    """
    Generate frequency sweep signals for frequency response analysis.
    
    A frequency sweep is a signal where the frequency changes over time.
    Logarithmic sweeps (where frequency changes exponentially) are standard
    in audio for measuring frequency responses, as they provide equal
    resolution per octave.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
        length_samples (int): Length of generated signals in samples (default: 44100)
    """
    
    def __init__(self, sample_rate=44100, length_samples=44100):
        """
        Initialize the sweep generator.
        
        Args:
            sample_rate: Sample rate in Hz
            length_samples: Length of generated signals in samples
        """
        self.sample_rate = float(sample_rate)
        self.length_samples = int(length_samples)
    
    def logarithmic(self, start_freq, end_freq):
        """
        Generate a logarithmic frequency sweep.
        
        In a logarithmic sweep, the frequency changes exponentially over time:
        f(t) = start_freq * (end_freq / start_freq)^(t / duration)
        
        This provides equal resolution per octave, which is ideal for audio
        frequency response measurements.
        
        Args:
            start_freq: Starting frequency in Hz (must be > 0)
            end_freq: Ending frequency in Hz (must be > 0)
            
        Returns:
            numpy.ndarray: Logarithmic sweep signal of length length_samples
        """
        # Validate frequencies
        if start_freq <= 0 or end_freq <= 0:
            raise ValueError("Start and end frequencies must be positive")
        
        # Calculate duration in seconds
        duration = self.length_samples / self.sample_rate
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Calculate instantaneous frequency: f(t) = start * (end/start)^(t/duration)
        # Using log/exp for numerical stability
        log_start = np.log(start_freq)
        log_end = np.log(end_freq)
        log_freq = log_start + (log_end - log_start) * t / duration
        instantaneous_freq = np.exp(log_freq)
        
        # Calculate phase by integrating instantaneous frequency
        # phase(t) = 2 * pi * integral(f(t)) dt
        # For logarithmic sweep: phase(t) = 2 * pi * start * duration / ln(end/start) * (end/start)^(t/duration)
        if np.isclose(start_freq, end_freq):
            # Edge case: constant frequency
            phase = 2 * np.pi * start_freq * t
        else:
            ratio = end_freq / start_freq
            phase = 2 * np.pi * start_freq * duration / np.log(ratio) * (np.power(ratio, t / duration) - 1)
        
        # Generate signal
        signal = 0.5 * np.sin(phase)
        
        return signal
    
    def linear(self, start_freq, end_freq):
        """
        Generate a linear frequency sweep.
        
        In a linear sweep, the frequency changes linearly over time:
        f(t) = start_freq + (end_freq - start_freq) * t / duration
        
        This provides equal resolution per Hz, which can be useful for
        testing specific frequency ranges.
        
        Args:
            start_freq: Starting frequency in Hz (must be > 0)
            end_freq: Ending frequency in Hz (must be > 0)
            
        Returns:
            numpy.ndarray: Linear sweep signal of length length_samples
        """
        # Validate frequencies
        if start_freq <= 0 or end_freq <= 0:
            raise ValueError("Start and end frequencies must be positive")
        
        # Check Nyquist limit
        if end_freq > self.sample_rate / 2:
            raise ValueError(f"End frequency {end_freq} Hz exceeds Nyquist frequency ({self.sample_rate/2} Hz)")
        
        # Calculate duration in seconds
        duration = self.length_samples / self.sample_rate
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Calculate instantaneous frequency: f(t) = start + (end - start) * t / duration
        instantaneous_freq = start_freq + (end_freq - start_freq) * t / duration
        
        # Calculate phase by integrating instantaneous frequency
        # phase(t) = 2 * pi * integral(f(t)) dt = 2 * pi * (start * t + (end - start) * t^2 / (2 * duration))
        phase = 2 * np.pi * (start_freq * t + (end_freq - start_freq) * t**2 / (2 * duration))
        
        # Generate signal
        signal = 0.5 * np.sin(phase)
        
        return signal
    
    def exponential(self, start_freq, end_freq, exponent=2.0):
        """
        Generate an exponential frequency sweep.
        
        In an exponential sweep, the frequency changes according to a power law:
        f(t) = start_freq + (end_freq - start_freq) * (t / duration)^exponent
        
        Args:
            start_freq: Starting frequency in Hz (must be > 0)
            end_freq: Ending frequency in Hz (must be > 0)
            exponent: Exponent for the sweep (default: 2.0)
            
        Returns:
            numpy.ndarray: Exponential sweep signal of length length_samples
        """
        # Validate frequencies
        if start_freq <= 0 or end_freq <= 0:
            raise ValueError("Start and end frequencies must be positive")
        
        # Check Nyquist limit
        if end_freq > self.sample_rate / 2:
            raise ValueError(f"End frequency {end_freq} Hz exceeds Nyquist frequency ({self.sample_rate/2} Hz)")
        
        # Calculate duration in seconds
        duration = self.length_samples / self.sample_rate
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Calculate instantaneous frequency: f(t) = start + (end - start) * (t / duration)^exponent
        normalized_time = np.clip(t / duration, 0.0, 1.0)
        instantaneous_freq = start_freq + (end_freq - start_freq) * (normalized_time ** exponent)
        
        # Calculate phase by numerical integration
        phase = 2 * np.pi * np.cumsum(instantaneous_freq) / self.sample_rate
        
        # Generate signal
        signal = 0.5 * np.sin(phase)
        
        return signal
    
    def generate_stereo(self, start_freq_l, end_freq_l, start_freq_r=None, end_freq_r=None,
                        sweep_type='logarithmic'):
        """
        Generate a stereo frequency sweep.
        
        Args:
            start_freq_l: Starting frequency for left channel in Hz
            end_freq_l: Ending frequency for left channel in Hz
            start_freq_r: Starting frequency for right channel in Hz (default: same as left)
            end_freq_r: Ending frequency for right channel in Hz (default: same as left)
            sweep_type: Type of sweep ('logarithmic', 'linear', 'exponential') (default: 'logarithmic')
            
        Returns:
            tuple: (left_signal, right_signal) - Two numpy arrays of length length_samples
        """
        # Use left frequencies for right if not specified
        if start_freq_r is None:
            start_freq_r = start_freq_l
        if end_freq_r is None:
            end_freq_r = end_freq_l
        
        # Generate left and right signals
        if sweep_type == 'logarithmic':
            signal_l = self.logarithmic(start_freq_l, end_freq_l)
            signal_r = self.logarithmic(start_freq_r, end_freq_r)
        elif sweep_type == 'linear':
            signal_l = self.linear(start_freq_l, end_freq_l)
            signal_r = self.linear(start_freq_r, end_freq_r)
        elif sweep_type == 'exponential':
            signal_l = self.exponential(start_freq_l, end_freq_l)
            signal_r = self.exponential(start_freq_r, end_freq_r)
        else:
            raise ValueError(f"Unknown sweep type: {sweep_type}. Use 'logarithmic', 'linear', or 'exponential'.")
        
        return signal_l, signal_r
    
    def generate_octave_sweep(self, start_freq, num_octaves, sweep_type='logarithmic'):
        """
        Generate a sweep covering a specified number of octaves.
        
        Args:
            start_freq: Starting frequency in Hz
            num_octaves: Number of octaves to sweep (e.g., 10 octaves = 20Hz to ~20kHz)
            sweep_type: Type of sweep ('logarithmic', 'linear', 'exponential') (default: 'logarithmic')
            
        Returns:
            numpy.ndarray: Sweep signal covering specified octaves
        """
        # Calculate end frequency: each octave doubles the frequency
        end_freq = start_freq * (2 ** num_octaves)
        
        # Check Nyquist limit
        if end_freq > self.sample_rate / 2:
            # Reduce number of octaves to stay within Nyquist
            max_octaves = np.log2(self.sample_rate / (2 * start_freq))
            end_freq = start_freq * (2 ** max_octaves)
            print(f"Warning: Reduced end frequency to {end_freq:.1f} Hz to stay within Nyquist limit")
        
        # Generate sweep
        if sweep_type == 'logarithmic':
            return self.logarithmic(start_freq, end_freq)
        elif sweep_type == 'linear':
            return self.linear(start_freq, end_freq)
        elif sweep_type == 'exponential':
            return self.exponential(start_freq, end_freq)
        else:
            raise ValueError(f"Unknown sweep type: {sweep_type}")
    
    def set_length(self, length_samples):
        """
        Set the length of generated signals.
        
        Args:
            length_samples: New length in samples
        """
        self.length_samples = int(length_samples)
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
    
    @property
    def duration_seconds(self):
        """Return the duration of generated signals in seconds."""
        return self.length_samples / self.sample_rate
    
    @property
    def nyquist_frequency(self):
        """Return the Nyquist frequency (maximum representable frequency)."""
        return self.sample_rate / 2.0


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Create generator
    gen = SweepGenerator(sample_rate=44100, length_samples=44100)
    
    print(f"Sample rate: {gen.sample_rate} Hz")
    print(f"Length: {gen.length_samples} samples ({gen.duration_seconds:.2f} seconds)")
    print(f"Nyquist frequency: {gen.nyquist_frequency:.1f} Hz")
    
    # Generate logarithmic sweep from 20Hz to 20kHz
    log_sweep = gen.logarithmic(start_freq=20.0, end_freq=20000.0)
    print(f"\nGenerated logarithmic sweep (20Hz-20kHz): max={log_sweep.max():.3f}, min={log_sweep.min():.3f}")
    
    # Generate linear sweep from 100Hz to 1000Hz
    linear_sweep = gen.linear(start_freq=100.0, end_freq=1000.0)
    print(f"Generated linear sweep (100Hz-1000Hz): max={linear_sweep.max():.3f}, min={linear_sweep.min():.3f}")
    
    # Generate exponential sweep
    exp_sweep = gen.exponential(start_freq=20.0, end_freq=20000.0, exponent=2.0)
    print(f"Generated exponential sweep: max={exp_sweep.max():.3f}, min={exp_sweep.min():.3f}")
    
    # Generate stereo sweep
    sweep_l, sweep_r = gen.generate_stereo(
        start_freq_l=20.0, end_freq_l=20000.0,
        start_freq_r=100.0, end_freq_r=10000.0
    )
    print(f"Generated stereo sweep: L max={sweep_l.max():.3f}, R max={sweep_r.max():.3f}")
    
    # Generate octave sweep (10 octaves = 20Hz to ~20kHz)
    octave_sweep = gen.generate_octave_sweep(start_freq=20.0, num_octaves=10.0)
    print(f"Generated 10-octave sweep: max={octave_sweep.max():.3f}, min={octave_sweep.min():.3f}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 10))
        
        plt.subplot(4, 1, 1)
        plt.plot(log_sweep[:5000])
        plt.title("Logarithmic Sweep (20Hz - 20kHz)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(4, 1, 2)
        plt.plot(linear_sweep[:5000])
        plt.title("Linear Sweep (100Hz - 1000Hz)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(4, 1, 3)
        plt.plot(exp_sweep[:5000])
        plt.title("Exponential Sweep (20Hz - 20kHz, exponent=2)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(4, 1, 4)
        plt.plot(sweep_l[:5000], label='Left (20Hz-20kHz)')
        plt.plot(sweep_r[:5000], label='Right (100Hz-10kHz)', alpha=0.7)
        plt.title("Stereo Sweep")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

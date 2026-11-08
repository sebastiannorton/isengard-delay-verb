# Sine Wave Signal Generator
# For frequency accuracy testing and tonal analysis

"""
Sine wave signal generator for frequency accuracy testing.

Features:
- Single frequency sine waves
- Mono and stereo generation
- Configurable frequency, amplitude, and phase
- Configurable signal length
- Deterministic output
- Sample-rate independent

Usage:
    from signals.sine import SineGenerator
    
    # Create generator
    gen = SineGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate mono sine wave at 440Hz
    signal = gen.generate(frequency=440.0)
    
    # Generate mono sine wave with custom parameters
    signal = gen.generate(frequency=1000.0, amplitude=0.5, phase=np.pi/4)
    
    # Generate stereo sine wave
    signal_l, signal_r = gen.generate_stereo(frequency=440.0)
    
    # Generate stereo with phase difference (creates stereo width)
    signal_l, signal_r = gen.generate_stereo(frequency=440.0, phase_l=0.0, phase_r=np.pi/2)
"""

import numpy as np


class SineGenerator:
    """
    Generate sine wave signals for frequency accuracy testing.
    
    Sine waves are pure tones at a single frequency, making them ideal for
    testing frequency accuracy, pitch shifting, modulation, and other
    frequency-dependent DSP behaviors.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
        length_samples (int): Length of generated signals in samples (default: 44100)
    """
    
    def __init__(self, sample_rate=44100, length_samples=44100):
        """
        Initialize the sine generator.
        
        Args:
            sample_rate: Sample rate in Hz
            length_samples: Length of generated signals in samples
        """
        self.sample_rate = float(sample_rate)
        self.length_samples = int(length_samples)
    
    def generate(self, frequency, amplitude=0.5, phase=0.0):
        """
        Generate a mono sine wave signal.
        
        Args:
            frequency: Frequency of the sine wave in Hz
            amplitude: Amplitude of the sine wave (default: 0.5)
            phase: Phase offset in radians (default: 0.0)
            
        Returns:
            numpy.ndarray: Mono sine wave signal of length length_samples
        """
        # Validate frequency
        if frequency <= 0:
            raise ValueError(f"Frequency must be positive, got {frequency}")
        
        # Nyquist theorem: maximum frequency is sample_rate / 2
        if frequency > self.sample_rate / 2:
            raise ValueError(f"Frequency {frequency} Hz exceeds Nyquist frequency ({self.sample_rate/2} Hz)")
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Generate sine wave: A * sin(2 * pi * f * t + phase)
        signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        
        return signal
    
    def generate_stereo(self, frequency, amplitude_l=0.5, amplitude_r=0.5, 
                        phase_l=0.0, phase_r=0.0):
        """
        Generate a stereo sine wave signal.
        
        Args:
            frequency: Frequency of the sine wave in Hz
            amplitude_l: Amplitude for left channel (default: 0.5)
            amplitude_r: Amplitude for right channel (default: 0.5)
            phase_l: Phase offset for left channel in radians (default: 0.0)
            phase_r: Phase offset for right channel in radians (default: 0.0)
            
        Returns:
            tuple: (left_signal, right_signal) - Two numpy arrays of length length_samples
        """
        # Validate frequency
        if frequency <= 0:
            raise ValueError(f"Frequency must be positive, got {frequency}")
        
        if frequency > self.sample_rate / 2:
            raise ValueError(f"Frequency {frequency} Hz exceeds Nyquist frequency ({self.sample_rate/2} Hz)")
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Generate left and right channels
        signal_l = amplitude_l * np.sin(2 * np.pi * frequency * t + phase_l)
        signal_r = amplitude_r * np.sin(2 * np.pi * frequency * t + phase_r)
        
        return signal_l, signal_r
    
    def generate_multi(self, frequencies, amplitudes=None, phases=None):
        """
        Generate a signal with multiple sine waves (additive synthesis).
        
        Args:
            frequencies: List of frequencies in Hz
            amplitudes: List of amplitudes (default: all 0.5 / len(frequencies))
            phases: List of phase offsets in radians (default: all 0.0)
            
        Returns:
            numpy.ndarray: Mono signal with multiple sine waves
        """
        if amplitudes is None:
            # Default: equal amplitude for all, scaled so total is ~0.5
            amplitudes = [0.5 / len(frequencies)] * len(frequencies)
        
        if phases is None:
            phases = [0.0] * len(frequencies)
        
        if len(frequencies) != len(amplitudes) or len(frequencies) != len(phases):
            raise ValueError("Frequencies, amplitudes, and phases must have the same length")
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Sum all sine waves
        signal = np.zeros(self.length_samples, dtype=np.float32)
        for freq, amp, phase in zip(frequencies, amplitudes, phases):
            if freq > 0 and freq <= self.sample_rate / 2:
                signal += amp * np.sin(2 * np.pi * freq * t + phase)
        
        return signal
    
    def generate_chord(self, root_frequency, intervals, amplitudes=None, phases=None):
        """
        Generate a chord (multiple sine waves at musical intervals).
        
        Args:
            root_frequency: Frequency of the root note in Hz
            intervals: List of intervals as ratios (e.g., [1.0, 1.25, 1.5] for major chord)
            amplitudes: List of amplitudes (default: all 0.5 / len(intervals))
            phases: List of phase offsets in radians (default: all 0.0)
            
        Returns:
            numpy.ndarray: Mono signal with chord
        """
        frequencies = [root_frequency * interval for interval in intervals]
        return self.generate_multi(frequencies, amplitudes, phases)
    
    def generate_frequency_modulated(self, carrier_freq, modulation_freq, modulation_depth, 
                                      modulation_phase=0.0):
        """
        Generate a frequency-modulated (FM) sine wave.
        
        FM synthesis: y(t) = A * sin(2 * pi * (f_c + I * sin(2 * pi * f_m * t + phi)) * t)
        where f_c is carrier frequency, I is modulation depth, f_m is modulation frequency
        
        Args:
            carrier_freq: Carrier frequency in Hz
            modulation_freq: Modulation frequency in Hz
            modulation_depth: Modulation depth (frequency deviation) in Hz
            modulation_phase: Phase offset for modulation in radians (default: 0.0)
            
        Returns:
            numpy.ndarray: FM sine wave signal
        """
        # Validate frequencies
        if carrier_freq <= 0 or modulation_freq <= 0:
            raise ValueError("Frequencies must be positive")
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Generate FM signal
        # Instantaneous frequency: f_c + I * sin(2 * pi * f_m * t + phi)
        instantaneous_freq = carrier_freq + modulation_depth * np.sin(
            2 * np.pi * modulation_freq * t + modulation_phase
        )
        
        # Phase integral
        phase = 2 * np.pi * np.cumsum(instantaneous_freq) / self.sample_rate
        
        # Generate signal
        signal = 0.5 * np.sin(phase)
        
        return signal
    
    def generate_amplitude_modulated(self, carrier_freq, modulation_freq, modulation_depth, 
                                     modulation_phase=0.0):
        """
        Generate an amplitude-modulated (AM) sine wave.
        
        AM synthesis: y(t) = A * (1 + I * sin(2 * pi * f_m * t + phi)) * sin(2 * pi * f_c * t)
        where A is amplitude, I is modulation depth, f_c is carrier, f_m is modulation
        
        Args:
            carrier_freq: Carrier frequency in Hz
            modulation_freq: Modulation frequency in Hz
            modulation_depth: Modulation depth (0.0 to 1.0)
            modulation_phase: Phase offset for modulation in radians (default: 0.0)
            
        Returns:
            numpy.ndarray: AM sine wave signal
        """
        # Validate frequencies and depth
        if carrier_freq <= 0 or modulation_freq <= 0:
            raise ValueError("Frequencies must be positive")
        
        if modulation_depth < 0 or modulation_depth > 1.0:
            raise ValueError("Modulation depth must be between 0.0 and 1.0")
        
        # Generate time array
        t = np.arange(self.length_samples, dtype=np.float32) / self.sample_rate
        
        # Generate AM signal
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        modulator = 1.0 + modulation_depth * np.sin(
            2 * np.pi * modulation_freq * t + modulation_phase
        )
        
        signal = 0.5 * carrier * modulator
        
        return signal
    
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
    gen = SineGenerator(sample_rate=44100, length_samples=44100)
    
    print(f"Sample rate: {gen.sample_rate} Hz")
    print(f"Length: {gen.length_samples} samples ({gen.duration_seconds:.2f} seconds)")
    print(f"Nyquist frequency: {gen.nyquist_frequency:.1f} Hz")
    
    # Generate mono sine wave at 440Hz
    sine_440 = gen.generate(frequency=440.0, amplitude=0.5)
    print(f"\nGenerated 440Hz sine: max={sine_440.max():.3f}, min={sine_440.min():.3f}")
    
    # Generate mono sine wave at 1000Hz
    sine_1000 = gen.generate(frequency=1000.0, amplitude=0.5)
    print(f"Generated 1000Hz sine: max={sine_1000.max():.3f}, min={sine_1000.min():.3f}")
    
    # Generate stereo sine with phase difference
    sine_l, sine_r = gen.generate_stereo(frequency=440.0, phase_l=0.0, phase_r=np.pi/2)
    print(f"\nGenerated stereo 440Hz: L max={sine_l.max():.3f}, R max={sine_r.max():.3f}")
    
    # Generate multi-frequency signal
    multi = gen.generate_multi(
        frequencies=[100.0, 200.0, 400.0],
        amplitudes=[0.3, 0.2, 0.1],
        phases=[0.0, np.pi/4, np.pi/2]
    )
    print(f"Generated multi-frequency: max={multi.max():.3f}, min={multi.min():.3f}")
    
    # Generate major chord
    chord = gen.generate_chord(
        root_frequency=220.0,
        intervals=[1.0, 1.25, 1.5]  # Root, major third, perfect fifth
    )
    print(f"Generated major chord: max={chord.max():.3f}, min={chord.min():.3f}")
    
    # Generate FM signal
    fm = gen.generate_frequency_modulated(
        carrier_freq=440.0,
        modulation_freq=5.0,
        modulation_depth=20.0
    )
    print(f"Generated FM signal: max={fm.max():.3f}, min={fm.min():.3f}")
    
    # Generate AM signal
    am = gen.generate_amplitude_modulated(
        carrier_freq=440.0,
        modulation_freq=5.0,
        modulation_depth=0.5
    )
    print(f"Generated AM signal: max={am.max():.3f}, min={am.min():.3f}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 10))
        
        plt.subplot(5, 1, 1)
        plt.plot(sine_440[:500])
        plt.title("440Hz Sine Wave")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(5, 1, 2)
        plt.plot(sine_1000[:500])
        plt.title("1000Hz Sine Wave")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(5, 1, 3)
        plt.plot(sine_l[:500], label='Left (0 rad)')
        plt.plot(sine_r[:500], label='Right (π/2 rad)')
        plt.title("Stereo Sine Wave with Phase Difference")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(5, 1, 4)
        plt.plot(multi[:500])
        plt.title("Multi-Frequency Signal (100+200+400Hz)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(5, 1, 5)
        plt.plot(fm[:500])
        plt.title("FM Signal (440Hz carrier, 5Hz mod, 20Hz depth)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

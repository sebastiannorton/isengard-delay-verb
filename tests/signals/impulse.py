# Impulse Signal Generator
# For impulse response measurement

"""
Impulse signal generator for measuring impulse responses.

Features:
- Mono and stereo impulse generation
- Configurable impulse position
- Configurable signal length
- Sample-rate independent
- Deterministic output

Usage:
    from signals.impulse import ImpulseGenerator
    
    # Create generator
    gen = ImpulseGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate mono impulse at position 0
    signal = gen.generate()
    
    # Generate mono impulse at position 1000
    signal = gen.generate(position=1000)
    
    # Generate stereo impulse
    signal_l, signal_r = gen.generate_stereo()
    
    # Generate stereo impulse with different positions
    signal_l, signal_r = gen.generate_stereo(position_l=0, position_r=100)
"""

import numpy as np


class ImpulseGenerator:
    """
    Generate impulse signals for impulse response measurement.
    
    An impulse is a single sample with value 1.0 at a specified position,
    with all other samples being 0.0. This is the standard test signal
    for measuring impulse responses of audio systems.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
        length_samples (int): Length of generated signals in samples (default: 44100)
    """
    
    def __init__(self, sample_rate=44100, length_samples=44100):
        """
        Initialize the impulse generator.
        
        Args:
            sample_rate: Sample rate in Hz
            length_samples: Length of generated signals in samples
        """
        self.sample_rate = float(sample_rate)
        self.length_samples = int(length_samples)
    
    def generate(self, position=0, amplitude=1.0):
        """
        Generate a mono impulse signal.
        
        Args:
            position: Sample position of the impulse (default: 0)
            amplitude: Amplitude of the impulse (default: 1.0)
            
        Returns:
            numpy.ndarray: Mono impulse signal of length length_samples
        """
        # Validate position
        position = int(position)
        if position < 0 or position >= self.length_samples:
            raise ValueError(f"Position {position} is out of range [0, {self.length_samples})")
        
        # Create signal
        signal = np.zeros(self.length_samples, dtype=np.float32)
        signal[position] = float(amplitude)
        
        return signal
    
    def generate_stereo(self, position_l=0, position_r=0, amplitude_l=1.0, amplitude_r=1.0):
        """
        Generate a stereo impulse signal.
        
        Args:
            position_l: Sample position of the left channel impulse (default: 0)
            position_r: Sample position of the right channel impulse (default: 0)
            amplitude_l: Amplitude of the left channel impulse (default: 1.0)
            amplitude_r: Amplitude of the right channel impulse (default: 1.0)
            
        Returns:
            tuple: (left_signal, right_signal) - Two numpy arrays of length length_samples
        """
        # Validate positions
        position_l = int(position_l)
        position_r = int(position_r)
        if position_l < 0 or position_l >= self.length_samples:
            raise ValueError(f"Left position {position_l} is out of range [0, {self.length_samples})")
        if position_r < 0 or position_r >= self.length_samples:
            raise ValueError(f"Right position {position_r} is out of range [0, {self.length_samples})")
        
        # Create signals
        signal_l = np.zeros(self.length_samples, dtype=np.float32)
        signal_r = np.zeros(self.length_samples, dtype=np.float32)
        signal_l[position_l] = float(amplitude_l)
        signal_r[position_r] = float(amplitude_r)
        
        return signal_l, signal_r
    
    def generate_multi(self, positions, amplitudes=None):
        """
        Generate a signal with multiple impulses at specified positions.
        
        Args:
            positions: List of sample positions for impulses
            amplitudes: List of amplitudes for each impulse (default: all 1.0)
            
        Returns:
            numpy.ndarray: Mono signal with multiple impulses
        """
        if amplitudes is None:
            amplitudes = [1.0] * len(positions)
        
        if len(positions) != len(amplitudes):
            raise ValueError("Positions and amplitudes must have the same length")
        
        signal = np.zeros(self.length_samples, dtype=np.float32)
        
        for pos, amp in zip(positions, amplitudes):
            pos = int(pos)
            if pos < 0 or pos >= self.length_samples:
                raise ValueError(f"Position {pos} is out of range [0, {self.length_samples})")
            signal[pos] = float(amp)
        
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


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Create generator
    gen = ImpulseGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate mono impulse
    signal = gen.generate(position=1000)
    print(f"Generated mono impulse: length={len(signal)}, impulse at={np.argmax(signal)}")
    
    # Generate stereo impulse
    signal_l, signal_r = gen.generate_stereo(position_l=1000, position_r=2000)
    print(f"Generated stereo impulse: L={np.argmax(signal_l)}, R={np.argmax(signal_r)}")
    
    # Generate multi-impulse
    signal = gen.generate_multi(positions=[1000, 2000, 3000], amplitudes=[1.0, 0.5, 0.25])
    print(f"Generated multi-impulse: peaks at={np.where(signal > 0)[0]}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(10, 4))
        plt.plot(signal[:5000])
        plt.title("Multi-Impulse Signal")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.show()
    except ImportError:
        print("Matplotlib not available, skipping plot")

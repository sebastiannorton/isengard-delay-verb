# Noise Signal Generator
# For frequency response analysis

"""
Noise signal generator for frequency response and spectral analysis.

Features:
- White noise (flat spectrum)
- Pink noise (1/f spectrum)
- Mono and stereo generation
- Configurable signal length
- Deterministic output with seed
- Sample-rate independent

Usage:
    from signals.noise import NoiseGenerator
    
    # Create generator
    gen = NoiseGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate white noise
    signal = gen.white()
    
    # Generate white noise with seed
    signal = gen.white(seed=42)
    
    # Generate pink noise
    signal = gen.pink()
    
    # Generate stereo noise
    signal_l, signal_r = gen.generate_stereo(noise_type='white', seed_l=42, seed_r=43)
"""

import numpy as np


class NoiseGenerator:
    """
    Generate noise signals for frequency response and spectral analysis.
    
    White noise has a flat frequency spectrum, making it ideal for
    measuring frequency responses. Pink noise has a 1/f spectrum,
    which is useful for testing systems with frequency-dependent behavior.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
        length_samples (int): Length of generated signals in samples (default: 44100)
    """
    
    def __init__(self, sample_rate=44100, length_samples=44100):
        """
        Initialize the noise generator.
        
        Args:
            sample_rate: Sample rate in Hz
            length_samples: Length of generated signals in samples
        """
        self.sample_rate = float(sample_rate)
        self.length_samples = int(length_samples)
    
    def white(self, seed=None):
        """
        Generate white noise (uniform distribution, flat spectrum).
        
        White noise has equal power at all frequencies, making it ideal
        for measuring the frequency response of audio systems.
        
        Args:
            seed: Random seed for reproducibility (default: None)
            
        Returns:
            numpy.ndarray: White noise signal of length length_samples
        """
        if seed is not None:
            np.random.seed(int(seed))
        
        # Generate uniform white noise in range [-1.0, 1.0]
        signal = np.random.uniform(-1.0, 1.0, self.length_samples).astype(np.float32)
        
        return signal
    
    def white_normal(self, seed=None):
        """
        Generate white noise (normal/Gaussian distribution, flat spectrum).
        
        Args:
            seed: Random seed for reproducibility (default: None)
            
        Returns:
            numpy.ndarray: Gaussian white noise signal of length length_samples
        """
        if seed is not None:
            np.random.seed(int(seed))
        
        # Generate normal white noise with std=0.5 (so most values are in [-1, 1])
        signal = np.random.normal(0.0, 0.5, self.length_samples).astype(np.float32)
        
        # Clip to [-1.0, 1.0] to prevent extreme values
        signal = np.clip(signal, -1.0, 1.0)
        
        return signal
    
    def pink(self, seed=None):
        """
        Generate pink noise (1/f spectrum).
        
        Pink noise has a spectrum where power is inversely proportional
        to frequency (1/f). This is useful for testing systems with
        frequency-dependent behavior, as it has more energy at low
        frequencies.
        
        This implementation uses the Voss-McCartney algorithm, which
        generates pink noise by summing white noise signals at different
        octaves.
        
        Args:
            seed: Random seed for reproducibility (default: None)
            
        Returns:
            numpy.ndarray: Pink noise signal of length length_samples
        """
        if seed is not None:
            np.random.seed(int(seed))
        
        # Voss-McCartney algorithm for pink noise
        # Number of octaves (more octaves = better quality but slower)
        num_octaves = 16
        
        # Initialize noise arrays for each octave
        noise = np.zeros((num_octaves, self.length_samples), dtype=np.float32)
        
        # Generate white noise for each octave
        for i in range(num_octaves):
            noise[i] = np.random.uniform(-1.0, 1.0, self.length_samples)
        
        # Sum noise from different octaves with appropriate scaling
        # Each octave is downsampled by 2^i and scaled by 2^(-i/2)
        pink = np.zeros(self.length_samples, dtype=np.float32)
        for i in range(num_octaves):
            # Downsample by 2^i
            step = 2 ** i
            if step >= self.length_samples:
                continue
            
            # Take every step-th sample
            downsampled = noise[i, ::step]
            
            # Pad to original length
            if len(downsampled) < self.length_samples:
                padding = self.length_samples - len(downsampled)
                downsampled = np.pad(downsampled, (0, padding), mode='edge')
            
            # Scale and add
            scale = (2 ** (-i / 2.0))
            pink += downsampled * scale
        
        # Normalize to [-1.0, 1.0] range
        max_val = np.max(np.abs(pink))
        if max_val > 0:
            pink = pink / max_val
        
        return pink
    
    def generate_stereo(self, noise_type='white', seed_l=None, seed_r=None, 
                       amplitude_l=1.0, amplitude_r=1.0):
        """
        Generate stereo noise signals.
        
        Args:
            noise_type: Type of noise ('white' or 'pink') (default: 'white')
            seed_l: Random seed for left channel (default: None)
            seed_r: Random seed for right channel (default: None)
            amplitude_l: Amplitude for left channel (default: 1.0)
            amplitude_r: Amplitude for right channel (default: 1.0)
            
        Returns:
            tuple: (left_signal, right_signal) - Two numpy arrays of length length_samples
        """
        if noise_type == 'white':
            signal_l = self.white(seed=seed_l) * amplitude_l
            signal_r = self.white(seed=seed_r) * amplitude_r
        elif noise_type == 'pink':
            signal_l = self.pink(seed=seed_l) * amplitude_l
            signal_r = self.pink(seed=seed_r) * amplitude_r
        else:
            raise ValueError(f"Unknown noise type: {noise_type}. Use 'white' or 'pink'.")
        
        return signal_l, signal_r
    
    def generate_correlated_stereo(self, noise_type='white', seed=None, 
                                   correlation=0.0, amplitude_l=1.0, amplitude_r=1.0):
        """
        Generate stereo noise with specified correlation between channels.
        
        Args:
            noise_type: Type of noise ('white' or 'pink') (default: 'white')
            seed: Random seed for reproducibility (default: None)
            correlation: Correlation coefficient between channels (-1.0 to 1.0) (default: 0.0)
            amplitude_l: Amplitude for left channel (default: 1.0)
            amplitude_r: Amplitude for right channel (default: 1.0)
            
        Returns:
            tuple: (left_signal, right_signal) - Two numpy arrays of length length_samples
        """
        if seed is not None:
            np.random.seed(int(seed))
        
        # Generate base noise
        if noise_type == 'white':
            base = np.random.uniform(-1.0, 1.0, self.length_samples).astype(np.float32)
        elif noise_type == 'pink':
            base = self.pink()
        else:
            raise ValueError(f"Unknown noise type: {noise_type}. Use 'white' or 'pink'.")
        
        # Generate uncorrelated noise for right channel
        uncorrelated = np.random.uniform(-1.0, 1.0, self.length_samples).astype(np.float32)
        
        # Mix base and uncorrelated to achieve desired correlation
        # signal_r = correlation * signal_l + sqrt(1 - correlation^2) * uncorrelated
        signal_l = base * amplitude_l
        signal_r = (correlation * base + 
                   np.sqrt(1.0 - correlation**2) * uncorrelated) * amplitude_r
        
        return signal_l, signal_r
    
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
    gen = NoiseGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate white noise
    white = gen.white(seed=42)
    print(f"Generated white noise: length={len(white)}, range=[{white.min():.3f}, {white.max():.3f}]")
    
    # Generate pink noise
    pink = gen.pink(seed=42)
    print(f"Generated pink noise: length={len(pink)}, range=[{pink.min():.3f}, {pink.max():.3f}]")
    
    # Generate stereo white noise
    white_l, white_r = gen.generate_stereo(noise_type='white', seed_l=42, seed_r=43)
    print(f"Generated stereo white noise: L range=[{white_l.min():.3f}, {white_l.max():.3f}], "
          f"R range=[{white_r.min():.3f}, {white_r.max():.3f}]")
    
    # Generate correlated stereo noise
    corr_l, corr_r = gen.generate_correlated_stereo(noise_type='white', seed=42, correlation=0.7)
    actual_corr = np.corrcoef(corr_l, corr_r)[0, 1]
    print(f"Generated correlated stereo: target={0.7:.3f}, actual={actual_corr:.3f}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 8))
        
        plt.subplot(4, 1, 1)
        plt.plot(white[:1000])
        plt.title("White Noise")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(4, 1, 2)
        plt.plot(pink[:1000])
        plt.title("Pink Noise")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(4, 1, 3)
        plt.plot(white_l[:1000], label='Left')
        plt.plot(white_r[:1000], label='Right', alpha=0.7)
        plt.title("Stereo White Noise")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(4, 1, 4)
        plt.plot(corr_l[:1000], label='Left')
        plt.plot(corr_r[:1000], label='Right', alpha=0.7)
        plt.title(f"Correlated Stereo Noise (r={actual_corr:.3f})")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("Matplotlib not available, skipping plots")

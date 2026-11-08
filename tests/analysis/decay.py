# Decay Curve Analyzer
# For reverb decay analysis

"""
Decay curve analysis tools for reverb characterization.

Features:
- Decay curve computation
- T60, T30, T20 measurement
- Spectral decay analysis
- Decay linearity measurement
- Modulation depth analysis

Usage:
    from analysis.decay import DecayAnalyzer
    
    # Create analyzer
    analyzer = DecayAnalyzer(sample_rate=44100)
    
    # Compute decay curve
    curve = analyzer.compute_decay_curve(signal)
    
    # Measure T60
    t60 = analyzer.measure_t60(signal)
    
    # Measure spectral decay
    spectral_decay = analyzer.measure_spectral_decay(signal)
"""

import numpy as np


class DecayAnalyzer:
    """
    Analyze decay curves for reverb characterization.
    
    Decay curves show how the energy of a signal decreases over time,
    which is essential for understanding reverb and delay behavior.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
    """
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the decay analyzer.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
    
    def compute_decay_curve(self, signal, window_size=1024, hop_size=None, 
                             attack_ms=10, release_ms=None):
        """
        Compute the decay curve from a signal.
        
        The decay curve is computed by dividing the signal into windows
        and calculating the RMS level of each window.
        
        Args:
            signal: Input signal (numpy array)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            release_ms: Duration of release to include in milliseconds (default: None, use full signal)
            
        Returns:
            tuple: (times, levels) - Time points and corresponding RMS levels
        """
        if hop_size is None:
            hop_size = window_size // 4
        
        # Convert times to samples
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        
        if release_ms is not None:
            release_samples = int(release_ms * self.sample_rate / 1000)
            signal = signal[:attack_samples + release_samples]
        else:
            # Skip attack
            signal = signal[attack_samples:]
        
        if len(signal) == 0:
            return np.array([]), np.array([])
        
        # Compute number of windows
        num_windows = 1 + (len(signal) - window_size) // hop_size
        
        # Initialize arrays
        times = np.zeros(num_windows)
        levels = np.zeros(num_windows)
        
        # Compute decay curve
        for i in range(num_windows):
            start = i * hop_size
            end = start + window_size
            
            if end > len(signal):
                # Zero-pad if necessary
                window = signal[start:]
                window = np.pad(window, (0, end - len(signal)), mode='constant')
            else:
                window = signal[start:end]
            
            # Compute RMS
            rms = np.sqrt(np.mean(window ** 2))
            
            # Store time and level
            times[i] = start / self.sample_rate
            levels[i] = rms
        
        return times, levels
    
    def compute_decay_curve_db(self, signal, window_size=1024, hop_size=None,
                                attack_ms=10, release_ms=None):
        """
        Compute the decay curve in dB from a signal.
        
        Args:
            signal: Input signal (numpy array)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            release_ms: Duration of release to include in milliseconds (default: None)
            
        Returns:
            tuple: (times, levels_db) - Time points and corresponding levels in dB
        """
        times, levels = self.compute_decay_curve(
            signal, window_size, hop_size, attack_ms, release_ms
        )
        
        # Convert to dB (relative to maximum level)
        epsilon = 1e-10
        max_level = np.max(levels) + epsilon
        levels_db = 20 * np.log10(levels / max_level)
        
        return times, levels_db
    
    def measure_decay_time(self, signal, threshold_db=-60, window_size=1024, 
                            hop_size=None, attack_ms=10):
        """
        Measure the decay time from a signal.
        
        Args:
            signal: Input signal (numpy array)
            threshold_db: Decay threshold in dB (default: -60)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            
        Returns:
            float: Decay time in seconds
        """
        times, levels_db = self.compute_decay_curve_db(
            signal, window_size, hop_size, attack_ms
        )
        
        if len(levels_db) == 0:
            return 0.0
        
        # Find initial level (first few points)
        initial_window = min(5, len(levels_db) // 4)
        initial_db = np.mean(levels_db[:initial_window])
        
        # Target level
        target_db = initial_db + threshold_db
        
        # Find where curve drops below target
        below_target = np.where(levels_db < target_db)[0]
        
        if len(below_target) > 0:
            idx = below_target[0]
            return times[idx]
        else:
            # If never drops below threshold, return last time
            return times[-1]
    
    def measure_t60(self, signal, window_size=1024, hop_size=None, attack_ms=10):
        """
        Measure T60 (time to decay by 60dB) from a signal.
        
        Args:
            signal: Input signal (numpy array)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            
        Returns:
            float: T60 in seconds
        """
        return self.measure_decay_time(
            signal, threshold_db=-60, window_size=window_size,
            hop_size=hop_size, attack_ms=attack_ms
        )
    
    def measure_t30(self, signal, window_size=1024, hop_size=None, attack_ms=10):
        """
        Measure T30 (time to decay by 30dB) from a signal.
        
        Args:
            signal: Input signal (numpy array)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            
        Returns:
            float: T30 in seconds
        """
        return self.measure_decay_time(
            signal, threshold_db=-30, window_size=window_size,
            hop_size=hop_size, attack_ms=attack_ms
        )
    
    def measure_t20(self, signal, window_size=1024, hop_size=None, attack_ms=10):
        """
        Measure T20 (time to decay by 20dB) from a signal.
        
        Args:
            signal: Input signal (numpy array)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            
        Returns:
            float: T20 in seconds
        """
        return self.measure_decay_time(
            signal, threshold_db=-20, window_size=window_size,
            hop_size=hop_size, attack_ms=attack_ms
        )
    
    def measure_spectral_decay(self, signal, num_bands=10, window_size=1024, 
                                hop_size=None, attack_ms=10):
        """
        Measure decay time per frequency band.
        
        This computes the decay time for each of several frequency bands,
        allowing analysis of frequency-dependent decay.
        
        Args:
            signal: Input signal (numpy array)
            num_bands: Number of frequency bands (default: 10)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            
        Returns:
            tuple: (band_frequencies, decay_times) - Center frequencies and decay times for each band
        """
        if hop_size is None:
            hop_size = window_size // 4
        
        # Convert attack to samples
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        signal = signal[attack_samples:]
        
        if len(signal) == 0:
            return np.array([]), np.array([])
        
        # Create filter bank (simple octave bands)
        band_frequencies = []
        band_filters = []
        
        nyquist = self.sample_rate / 2
        
        # Create bands with approximately equal spacing on log scale
        min_freq = 20.0
        max_freq = nyquist * 0.95
        
        # Logarithmic spacing
        band_edges = np.logspace(np.log10(min_freq), np.log10(max_freq), num_bands + 1)
        
        # Create bandpass filters for each band
        for i in range(num_bands):
            low = band_edges[i]
            high = band_edges[i + 1]
            
            # Simple bandpass: difference of two lowpass filters
            # In practice, you might use a proper bandpass filter
            band_frequencies.append(np.sqrt(low * high))  # Geometric mean
            
            # For simplicity, we'll use a simple approach: filter the signal
            # and then compute decay curve
            # (Actual filter implementation would be more sophisticated)
        
        # Compute decay times for each band
        decay_times = []
        
        for low, high in zip(band_edges[:-1], band_edges[1:]):
            # Bandpass filter the signal (simple implementation)
            # This is a placeholder - in practice, use a proper filter
            filtered = self._bandpass_filter(signal, low, high, self.sample_rate)
            
            # Compute decay time for this band
            decay_time = self.measure_t60(
                filtered, window_size=window_size, hop_size=hop_size, attack_ms=0
            )
            decay_times.append(decay_time)
        
        return np.array(band_frequencies), np.array(decay_times)
    
    def measure_decay_linearity(self, signal, window_size=1024, hop_size=None, 
                                attack_ms=10):
        """
        Measure how linear the decay is.
        
        A perfectly linear decay (on a dB scale) indicates a simple exponential
        decay, while non-linear decay indicates more complex behavior.
        
        Args:
            signal: Input signal (numpy array)
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            attack_ms: Duration of attack to skip in milliseconds (default: 10)
            
        Returns:
            float: Decay linearity (0.0 = non-linear, 1.0 = perfectly linear)
        """
        times, levels_db = self.compute_decay_curve_db(
            signal, window_size, hop_size, attack_ms
        )
        
        if len(levels_db) < 10:
            return 0.0
        
        # Use first 80% of the decay for linearity measurement
        end_idx = int(0.8 * len(levels_db))
        times = times[:end_idx]
        levels_db = levels_db[:end_idx]
        
        # Fit a line to the decay curve
        # Line: y = mx + b
        A = np.vstack([times, np.ones(len(times))]).T
        m, b = np.linalg.lstsq(A, levels_db, rcond=None)[0]
        
        # Compute fitted line
        fitted = m * times + b
        
        # Compute correlation between actual and fitted
        corr = np.corrcoef(levels_db, fitted)[0, 1]
        
        # Linearity is the absolute value of correlation
        # (negative correlation is still linear)
        linearity = np.abs(corr)
        
        return linearity
    
    def measure_modulation_depth(self, signal, modulation_freq_hz, window_size=1024, 
                                  hop_size=None):
        """
        Measure the depth of amplitude modulation at a specific frequency.
        
        Args:
            signal: Input signal (numpy array)
            modulation_freq_hz: Modulation frequency to analyze in Hz
            window_size: Size of the analysis window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            
        Returns:
            float: Modulation depth (0.0 to 1.0)
        """
        # Compute decay curve (envelope)
        times, levels = self.compute_decay_curve(
            signal, window_size, hop_size, attack_ms=0
        )
        
        if len(levels) < 10:
            return 0.0
        
        # Compute FFT of the envelope to find modulation components
        fft_result = np.fft.rfft(levels)
        frequencies = np.fft.rfftfreq(len(levels), times[1] - times[0])
        magnitude = np.abs(fft_result)
        
        # Find the modulation frequency bin
        mod_bin = np.argmin(np.abs(frequencies - modulation_freq_hz))
        
        if mod_bin < len(magnitude):
            # Modulation depth is the magnitude at modulation frequency
            # relative to DC component
            dc_magnitude = magnitude[0] if len(magnitude) > 0 else 1.0
            mod_magnitude = magnitude[mod_bin]
            
            # Avoid division by zero
            epsilon = 1e-10
            depth = mod_magnitude / (dc_magnitude + epsilon)
            
            # Clamp to [0, 1]
            return min(1.0, max(0.0, depth))
        else:
            return 0.0
    
    def _bandpass_filter(self, signal, low, high, sample_rate):
        """
        Simple bandpass filter (placeholder implementation).
        
        In practice, you would use a proper filter design (e.g., Butterworth).
        This is a simplified version for demonstration.
        
        Args:
            signal: Input signal
            low: Low cutoff frequency in Hz
            high: High cutoff frequency in Hz
            sample_rate: Sample rate in Hz
            
        Returns:
            numpy.ndarray: Filtered signal
        """
        # Simple implementation: use FFT-based filtering
        n = len(signal)
        fft_signal = np.fft.rfft(signal)
        frequencies = np.fft.rfftfreq(n, 1.0 / sample_rate)
        
        # Create filter mask
        mask = np.zeros_like(frequencies)
        mask[(frequencies >= low) & (frequencies <= high)] = 1.0
        
        # Apply filter
        filtered_fft = fft_signal * mask
        
        # Inverse FFT
        filtered = np.fft.irfft(filtered_fft, n=n)
        
        return filtered
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from signals.sine import SineGenerator
    from signals.burst import BurstGenerator
    
    # Create analyzers and generators
    decay_analyzer = DecayAnalyzer(sample_rate=44100)
    sine_gen = SineGenerator(sample_rate=44100, length_samples=44100)
    burst_gen = BurstGenerator(sample_rate=44100, length_samples=44100)
    
    print("Decay Curve Analyzer Example")
    print("=" * 50)
    
    # Generate a test signal with decay (simulated reverb)
    # Create a burst with exponential decay
    burst = burst_gen.generate(frequency=1000.0, duration_ms=100.0, envelope='exponential')
    
    # Add some decay by convolving with an exponential decay
    # (In practice, this would be the actual impulse response)
    decay_length = 44100
    t = np.arange(decay_length, dtype=np.float32) / 44100
    decay_envelope = np.exp(-5.0 * t)  # Exponential decay
    
    # Convolve burst with decay envelope
    test_signal = np.convolve(burst, decay_envelope)[:decay_length]
    
    # Analyze the signal
    print("\nAnalyzing test signal with decay:")
    
    # Compute decay curve
    times, levels = decay_analyzer.compute_decay_curve(test_signal, window_size=1024, hop_size=256)
    print(f"  Decay curve: {len(times)} points, {times[-1]:.2f} seconds")
    
    # Compute decay curve in dB
    times_db, levels_db = decay_analyzer.compute_decay_curve_db(test_signal, window_size=1024, hop_size=256)
    print(f"  Decay curve (dB): starts at {levels_db[0]:.2f} dB, ends at {levels_db[-1]:.2f} dB")
    
    # Measure decay times
    t60 = decay_analyzer.measure_t60(test_signal, window_size=1024, hop_size=256)
    t30 = decay_analyzer.measure_t30(test_signal, window_size=1024, hop_size=256)
    t20 = decay_analyzer.measure_t20(test_signal, window_size=1024, hop_size=256)
    print(f"  T60: {t60:.3f} seconds")
    print(f"  T30: {t30:.3f} seconds")
    print(f"  T20: {t20:.3f} seconds")
    
    # Measure decay linearity
    linearity = decay_analyzer.measure_decay_linearity(test_signal, window_size=1024, hop_size=256)
    print(f"  Decay linearity: {linearity:.3f}")
    
    # Measure spectral decay
    band_freqs, band_decays = decay_analyzer.measure_spectral_decay(
        test_signal, num_bands=5, window_size=1024, hop_size=256
    )
    print(f"  Spectral decay (5 bands):")
    for freq, decay in zip(band_freqs, band_decays):
        print(f"    {freq:.1f} Hz: {decay:.3f} s")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 8))
        
        plt.subplot(3, 1, 1)
        plt.plot(test_signal[:5000])
        plt.title("Test Signal with Decay")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(3, 1, 2)
        plt.plot(times, levels)
        plt.title("Decay Curve (Linear)")
        plt.xlabel("Time (s)")
        plt.ylabel("RMS Level")
        plt.grid(True)
        
        plt.subplot(3, 1, 3)
        plt.plot(times_db, levels_db)
        plt.title("Decay Curve (dB)")
        plt.xlabel("Time (s)")
        plt.ylabel("Level (dB)")
        plt.axhline(y=-60, color='r', linestyle='--', label='-60dB')
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

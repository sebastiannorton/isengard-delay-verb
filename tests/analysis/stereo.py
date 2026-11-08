# Stereo Correlation Analyzer
# For stereo width, correlation, and phase analysis

"""
Stereo correlation and width analysis tools.

Features:
- Stereo correlation computation
- Cross-correlation with lag
- Stereo width measurement
- Phase difference analysis
- Channel balance measurement
- Coherence analysis

Usage:
    from analysis.stereo import StereoAnalyzer
    
    # Create analyzer
    analyzer = StereoAnalyzer()
    
    # Compute correlation
    correlation = analyzer.correlation(left_signal, right_signal)
    
    # Compute stereo width
    width = analyzer.width(left_signal, right_signal)
    
    # Compute cross-correlation
    lag, corr = analyzer.cross_correlation(left_signal, right_signal)
"""

import numpy as np


class StereoAnalyzer:
    """
    Analyze stereo characteristics of audio signals.
    
    This class provides methods for analyzing the stereo properties of
    audio signals, including correlation, width, phase differences, and
    channel balance.
    """
    
    def __init__(self):
        """Initialize the stereo analyzer."""
        pass
    
    def correlation(self, left, right):
        """
        Compute the Pearson correlation coefficient between left and right channels.
        
        The correlation coefficient ranges from -1 (perfectly anti-correlated)
        to +1 (perfectly correlated). A value of 0 indicates no correlation.
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            
        Returns:
            float: Correlation coefficient (-1.0 to 1.0)
        """
        # Ensure signals are the same length
        min_len = min(len(left), len(right))
        left = left[:min_len]
        right = right[:min_len]
        
        # Remove DC offset
        left = left - np.mean(left)
        right = right - np.mean(right)
        
        # Compute correlation
        # corr = cov(L, R) / (std(L) * std(R))
        cov = np.mean(left * right)
        std_l = np.std(left)
        std_r = np.std(right)
        
        # Avoid division by zero
        epsilon = 1e-10
        corr = cov / (std_l * std_r + epsilon)
        
        # Clamp to [-1, 1] due to numerical errors
        return np.clip(corr, -1.0, 1.0)
    
    def cross_correlation(self, left, right, max_lag=None):
        """
        Compute the cross-correlation between left and right channels.
        
        Cross-correlation measures the similarity between two signals as a
        function of the displacement (lag) of one relative to the other.
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            max_lag: Maximum lag to consider in samples (default: min(len(left), len(right)) // 4)
            
        Returns:
            tuple: (lag, correlation) - Lag in samples and corresponding correlation
        """
        # Ensure signals are the same length
        min_len = min(len(left), len(right))
        left = left[:min_len]
        right = right[:min_len]
        
        if max_lag is None:
            max_lag = min_len // 4
        
        # Remove DC offset
        left = left - np.mean(left)
        right = right - np.mean(right)
        
        # Compute cross-correlation using FFT
        # corr = IFFT(FFT(L) * conj(FFT(R)))
        fft_left = np.fft.fft(left, n=2 * min_len)
        fft_right = np.fft.fft(right, n=2 * min_len)
        
        # Cross-spectrum
        cross_spectrum = fft_left * np.conj(fft_right)
        
        # Inverse FFT
        corr = np.fft.ifft(cross_spectrum).real
        
        # Take the relevant part
        corr = corr[:max_lag + 1]
        lags = np.arange(-max_lag, max_lag + 1)
        
        # Find peak correlation and lag
        peak_idx = np.argmax(corr)
        peak_lag = lags[peak_idx]
        peak_corr = corr[peak_idx]
        
        return peak_lag, peak_corr
    
    def width(self, left, right):
        """
        Compute the stereo width.
        
        Stereo width is a measure of how wide the stereo image is.
        - Width = 0: Mono (left and right are identical)
        - Width = 1: Perfectly uncorrelated (left and right are independent)
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            
        Returns:
            float: Stereo width (0.0 to 1.0)
        """
        # Compute correlation
        corr = self.correlation(left, right)
        
        # Width = sqrt(1 - corr^2)
        width = np.sqrt(1.0 - corr ** 2)
        
        return width
    
    def phase_difference(self, left, right, frequency=None):
        """
        Compute the average phase difference between left and right channels.
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            frequency: Frequency to analyze in Hz (default: None, analyze all frequencies)
            
        Returns:
            float: Average phase difference in radians (-pi to pi)
        """
        # Ensure signals are the same length
        min_len = min(len(left), len(right))
        left = left[:min_len]
        right = right[:min_len]
        
        # Compute FFT
        n = min_len
        fft_left = np.fft.rfft(left, n=n)
        fft_right = np.fft.rfft(right, n=n)
        
        # Compute phase difference
        phase_left = np.angle(fft_left)
        phase_right = np.angle(fft_right)
        phase_diff = phase_left - phase_right
        
        # Unwrap phase difference
        phase_diff = np.unwrap(phase_diff)
        
        # If frequency is specified, find the corresponding bin
        if frequency is not None:
            # Assume sample rate is known (not stored in this class)
            # This is a limitation - in practice, you'd need to pass sample_rate
            freq_bins = np.fft.rfftfreq(n, 1.0)  # Assuming sample_rate=1 for now
            bin_idx = np.argmin(np.abs(freq_bins - frequency))
            return phase_diff[bin_idx]
        
        # Otherwise, compute weighted average
        magnitude_left = np.abs(fft_left)
        magnitude_right = np.abs(fft_right)
        weights = (magnitude_left + magnitude_right) / 2
        
        # Weighted average
        weighted_phase_diff = np.sum(phase_diff * weights) / np.sum(weights)
        
        return weighted_phase_diff
    
    def channel_balance(self, left, right):
        """
        Compute the channel balance (relative level difference).
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            
        Returns:
            float: Channel balance in dB (positive = left louder, negative = right louder)
        """
        # Compute RMS of each channel
        rms_left = np.sqrt(np.mean(left ** 2))
        rms_right = np.sqrt(np.mean(right ** 2))
        
        # Avoid division by zero
        epsilon = 1e-10
        
        # Compute balance in dB
        balance_db = 20 * np.log10((rms_left + epsilon) / (rms_right + epsilon))
        
        return balance_db
    
    def coherence(self, left, right, nfft=None):
        """
        Compute the magnitude-squared coherence between left and right channels.
        
        Coherence is a frequency-domain measure of linear relationship between
        two signals. It ranges from 0 (no relationship) to 1 (perfect relationship).
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            nfft: Number of FFT points (default: min(len(left), len(right)))
            
        Returns:
            tuple: (frequencies, coherence) - Frequency bins and corresponding coherence values
        """
        # Ensure signals are the same length
        min_len = min(len(left), len(right))
        left = left[:min_len]
        right = right[:min_len]
        
        if nfft is None:
            nfft = min_len
        
        # Remove DC offset
        left = left - np.mean(left)
        right = right - np.mean(right)
        
        # Compute FFT
        fft_left = np.fft.rfft(left, n=nfft)
        fft_right = np.fft.rfft(right, n=nfft)
        
        # Compute cross-spectrum and power spectra
        cross_spectrum = fft_left * np.conj(fft_right)
        power_left = np.abs(fft_left) ** 2
        power_right = np.abs(fft_right) ** 2
        
        # Compute coherence
        epsilon = 1e-10
        coherence = np.abs(cross_spectrum) ** 2 / (power_left * power_right + epsilon)
        
        # Compute frequency bins
        frequencies = np.fft.rfftfreq(nfft, 1.0)  # Assuming sample_rate=1
        
        return frequencies, coherence
    
    def stereo_to_mid_side(self, left, right):
        """
        Convert stereo signal to mid/side representation.
        
        Mid = (Left + Right) / 2
        Side = (Right - Left) / 2
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            
        Returns:
            tuple: (mid, side) - Mid and side signals
        """
        # Ensure signals are the same length
        min_len = min(len(left), len(right))
        left = left[:min_len]
        right = right[:min_len]
        
        mid = (left + right) / 2
        side = (right - left) / 2
        
        return mid, side
    
    def mid_side_to_stereo(self, mid, side):
        """
        Convert mid/side signal to stereo representation.
        
        Left = Mid - Side
        Right = Mid + Side
        
        Args:
            mid: Mid channel signal (numpy array)
            side: Side channel signal (numpy array)
            
        Returns:
            tuple: (left, right) - Left and right signals
        """
        # Ensure signals are the same length
        min_len = min(len(mid), len(side))
        mid = mid[:min_len]
        side = side[:min_len]
        
        left = mid - side
        right = mid + side
        
        return left, right
    
    def measure_stereo_image(self, left, right):
        """
        Measure various properties of the stereo image.
        
        Args:
            left: Left channel signal (numpy array)
            right: Right channel signal (numpy array)
            
        Returns:
            dict: Dictionary containing various stereo image properties
        """
        # Compute all properties
        correlation = self.correlation(left, right)
        width = self.width(left, right)
        lag, cross_corr = self.cross_correlation(left, right)
        phase_diff = self.phase_difference(left, right)
        balance_db = self.channel_balance(left, right)
        mid, side = self.stereo_to_mid_side(left, right)
        
        # Compute mid/side ratio
        rms_mid = np.sqrt(np.mean(mid ** 2))
        rms_side = np.sqrt(np.mean(side ** 2))
        epsilon = 1e-10
        mid_side_ratio = 20 * np.log10((rms_mid + epsilon) / (rms_side + epsilon))
        
        return {
            'correlation': correlation,
            'width': width,
            'cross_correlation_lag': lag,
            'cross_correlation': cross_corr,
            'phase_difference': phase_diff,
            'channel_balance_db': balance_db,
            'mid_side_ratio_db': mid_side_ratio,
            'mid_rms': rms_mid,
            'side_rms': rms_side
        }


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from signals.sine import SineGenerator
    from signals.noise import NoiseGenerator
    
    # Create analyzer and generators
    stereo_analyzer = StereoAnalyzer()
    sine_gen = SineGenerator(sample_rate=44100, length_samples=44100)
    noise_gen = NoiseGenerator(sample_rate=44100, length_samples=44100)
    
    print("Stereo Analyzer Example")
    print("=" * 50)
    
    # Generate test signals
    # Mono signal (identical left and right)
    mono_l, mono_r = sine_gen.generate_stereo(frequency=440.0, amplitude_l=0.5, amplitude_r=0.5)
    
    # Stereo signal with phase difference
    stereo_phase_l, stereo_phase_r = sine_gen.generate_stereo(
        frequency=440.0, amplitude_l=0.5, amplitude_r=0.5, phase_l=0.0, phase_r=np.pi/2
    )
    
    # Stereo signal with different frequencies
    stereo_freq_l = sine_gen.generate(frequency=400.0, amplitude=0.5)
    stereo_freq_r = sine_gen.generate(frequency=500.0, amplitude=0.5)
    
    # Uncorrelated noise
    noise_l, noise_r = noise_gen.generate_stereo(noise_type='white', seed_l=42, seed_r=43)
    
    # Correlated noise
    corr_l, corr_r = noise_gen.generate_correlated_stereo(noise_type='white', seed=42, correlation=0.7)
    
    # Analyze mono signal
    print("\nAnalyzing mono signal:")
    mono_corr = stereo_analyzer.correlation(mono_l, mono_r)
    mono_width = stereo_analyzer.width(mono_l, mono_r)
    mono_balance = stereo_analyzer.channel_balance(mono_l, mono_r)
    print(f"  Correlation: {mono_corr:.4f} (expected: ~1.0)")
    print(f"  Width: {mono_width:.4f} (expected: ~0.0)")
    print(f"  Balance: {mono_balance:.2f} dB (expected: ~0.0)")
    
    # Analyze stereo signal with phase difference
    print("\nAnalyzing stereo signal with phase difference:")
    phase_corr = stereo_analyzer.correlation(stereo_phase_l, stereo_phase_r)
    phase_width = stereo_analyzer.width(stereo_phase_l, stereo_phase_r)
    phase_lag, phase_cross_corr = stereo_analyzer.cross_correlation(stereo_phase_l, stereo_phase_r)
    print(f"  Correlation: {phase_corr:.4f}")
    print(f"  Width: {phase_width:.4f}")
    print(f"  Cross-correlation lag: {phase_lag} samples")
    print(f"  Cross-correlation: {phase_cross_corr:.4f}")
    
    # Analyze stereo signal with different frequencies
    print("\nAnalyzing stereo signal with different frequencies:")
    freq_corr = stereo_analyzer.correlation(stereo_freq_l, stereo_freq_r)
    freq_width = stereo_analyzer.width(stereo_freq_l, stereo_freq_r)
    print(f"  Correlation: {freq_corr:.4f}")
    print(f"  Width: {freq_width:.4f}")
    
    # Analyze uncorrelated noise
    print("\nAnalyzing uncorrelated noise:")
    noise_corr = stereo_analyzer.correlation(noise_l, noise_r)
    noise_width = stereo_analyzer.width(noise_l, noise_r)
    print(f"  Correlation: {noise_corr:.4f} (expected: ~0.0)")
    print(f"  Width: {noise_width:.4f} (expected: ~1.0)")
    
    # Analyze correlated noise
    print("\nAnalyzing correlated noise (r=0.7):")
    corr_noise_corr = stereo_analyzer.correlation(corr_l, corr_r)
    corr_noise_width = stereo_analyzer.width(corr_l, corr_r)
    print(f"  Correlation: {corr_noise_corr:.4f} (expected: ~0.7)")
    print(f"  Width: {corr_noise_width:.4f}")
    
    # Measure stereo image
    print("\nMeasuring stereo image of phase-different signal:")
    image = stereo_analyzer.measure_stereo_image(stereo_phase_l, stereo_phase_r)
    for key, value in image.items():
        print(f"  {key}: {value}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 10))
        
        plt.subplot(5, 1, 1)
        plt.plot(mono_l[:500], label='Left')
        plt.plot(mono_r[:500], label='Right', alpha=0.7)
        plt.title("Mono Signal (Identical Channels)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(5, 1, 2)
        plt.plot(stereo_phase_l[:500], label='Left (0 rad)')
        plt.plot(stereo_phase_r[:500], label='Right (π/2 rad)', alpha=0.7)
        plt.title("Stereo Signal with Phase Difference")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(5, 1, 3)
        plt.plot(stereo_freq_l[:500], label='Left (400Hz)')
        plt.plot(stereo_freq_r[:500], label='Right (500Hz)', alpha=0.7)
        plt.title("Stereo Signal with Different Frequencies")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(5, 1, 4)
        plt.plot(noise_l[:500], label='Left')
        plt.plot(noise_r[:500], label='Right', alpha=0.7)
        plt.title("Uncorrelated Noise")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(5, 1, 5)
        plt.plot(corr_l[:500], label='Left')
        plt.plot(corr_r[:500], label='Right', alpha=0.7)
        plt.title("Correlated Noise (r=0.7)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

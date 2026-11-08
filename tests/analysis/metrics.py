# Comparison Metrics
# For comparing implementation against reference

"""
Comparison metrics for validating implementation against reference.

Features:
- Sample-level difference
- RMS difference
- Correlation
- Spectral difference
- Spectral correlation
- Phase difference
- Time-frequency difference

Usage:
    from analysis.metrics import ComparisonMetrics
    
    # Create analyzer
    metrics = ComparisonMetrics()
    
    # Compute sample difference
    diff = metrics.sample_difference(ref, impl)
    
    # Compute RMS difference
    rms_diff = metrics.rms_difference(ref, impl)
    
    # Compute correlation
    corr = metrics.correlation(ref, impl)
"""

import numpy as np


class ComparisonMetrics:
    """
    Compute various metrics for comparing two audio signals.
    
    These metrics are useful for validating that an implementation
    matches a reference, or for comparing two different implementations.
    """
    
    def __init__(self):
        """Initialize the comparison metrics."""
        pass
    
    def sample_difference(self, reference, implementation):
        """
        Compute the sample-level difference between two signals.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            
        Returns:
            numpy.ndarray: Sample-level difference (reference - implementation)
        """
        # Ensure signals are the same length
        min_len = min(len(reference), len(implementation))
        reference = reference[:min_len]
        implementation = implementation[:min_len]
        
        return reference - implementation
    
    def rms_difference(self, reference, implementation):
        """
        Compute the RMS of the difference between two signals.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            
        Returns:
            float: RMS difference
        """
        diff = self.sample_difference(reference, implementation)
        return float(np.sqrt(np.mean(diff ** 2)))
    
    def max_difference(self, reference, implementation):
        """
        Compute the maximum absolute difference between two signals.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            
        Returns:
            float: Maximum absolute difference
        """
        diff = self.sample_difference(reference, implementation)
        return float(np.max(np.abs(diff)))
    
    def correlation(self, reference, implementation):
        """
        Compute the Pearson correlation coefficient between two signals.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            
        Returns:
            float: Correlation coefficient (-1.0 to 1.0)
        """
        # Ensure signals are the same length
        min_len = min(len(reference), len(implementation))
        reference = reference[:min_len]
        implementation = implementation[:min_len]
        
        # Remove DC offset
        reference = reference - np.mean(reference)
        implementation = implementation - np.mean(implementation)
        
        # Compute correlation
        cov = np.mean(reference * implementation)
        std_ref = np.std(reference)
        std_impl = np.std(implementation)
        
        # Avoid division by zero
        epsilon = 1e-10
        corr = cov / (std_ref * std_impl + epsilon)
        
        # Clamp to [-1, 1] due to numerical errors
        return float(np.clip(corr, -1.0, 1.0))
    
    def spectral_difference(self, reference, implementation, nfft=None, sample_rate=44100):
        """
        Compute the spectral difference between two signals.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            nfft: Number of FFT points (default: min(len(reference), len(implementation)))
            sample_rate: Sample rate in Hz (default: 44100)
            
        Returns:
            tuple: (frequencies, difference_db) - Frequency bins and difference in dB
        """
        # Ensure signals are the same length
        min_len = min(len(reference), len(implementation))
        reference = reference[:min_len]
        implementation = implementation[:min_len]
        
        if nfft is None:
            nfft = min_len
        
        # Compute FFT
        fft_ref = np.fft.rfft(reference, n=nfft)
        fft_impl = np.fft.rfft(implementation, n=nfft)
        
        # Compute magnitude spectra
        mag_ref = np.abs(fft_ref)
        mag_impl = np.abs(fft_impl)
        
        # Convert to dB
        epsilon = 1e-10
        db_ref = 20 * np.log10(mag_ref + epsilon)
        db_impl = 20 * np.log10(mag_impl + epsilon)
        
        # Compute difference
        difference_db = db_ref - db_impl
        
        # Compute frequency bins
        frequencies = np.fft.rfftfreq(nfft, 1.0 / sample_rate)
        
        return frequencies, difference_db
    
    def spectral_correlation(self, reference, implementation, nfft=None):
        """
        Compute the spectral correlation between two signals.
        
        Spectral correlation measures how similar the frequency content
        of two signals is.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            nfft: Number of FFT points (default: min(len(reference), len(implementation)))
            
        Returns:
            float: Spectral correlation coefficient
        """
        # Ensure signals are the same length
        min_len = min(len(reference), len(implementation))
        reference = reference[:min_len]
        implementation = implementation[:min_len]
        
        if nfft is None:
            nfft = min_len
        
        # Compute FFT
        fft_ref = np.fft.rfft(reference, n=nfft)
        fft_impl = np.fft.rfft(implementation, n=nfft)
        
        # Compute magnitude spectra
        mag_ref = np.abs(fft_ref)
        mag_impl = np.abs(fft_impl)
        
        # Compute correlation
        corr = np.corrcoef(mag_ref, mag_impl)[0, 1]
        
        return float(corr)
    
    def phase_difference(self, reference, implementation, nfft=None, unwrap=True):
        """
        Compute the phase difference between two signals.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            nfft: Number of FFT points (default: min(len(reference), len(implementation)))
            unwrap: Whether to unwrap the phase difference (default: True)
            
        Returns:
            tuple: (frequencies, phase_diff) - Frequency bins and phase difference in radians
        """
        # Ensure signals are the same length
        min_len = min(len(reference), len(implementation))
        reference = reference[:min_len]
        implementation = implementation[:min_len]
        
        if nfft is None:
            nfft = min_len
        
        # Compute FFT
        fft_ref = np.fft.rfft(reference, n=nfft)
        fft_impl = np.fft.rfft(implementation, n=nfft)
        
        # Compute phase
        phase_ref = np.angle(fft_ref)
        phase_impl = np.angle(fft_impl)
        
        # Compute phase difference
        phase_diff = phase_ref - phase_impl
        
        # Unwrap if requested
        if unwrap:
            phase_diff = np.unwrap(phase_diff)
        
        # Compute frequency bins (assuming sample_rate=1 for now)
        frequencies = np.fft.rfftfreq(nfft, 1.0)
        
        return frequencies, phase_diff
    
    def time_frequency_difference(self, reference, implementation, window_size=1024, 
                                    hop_size=None, nfft=None, sample_rate=44100):
        """
        Compute the time-frequency difference between two signals.
        
        This computes the difference in the spectrogram representation,
        which shows how the frequency content changes over time.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            window_size: Size of the FFT window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            nfft: Number of FFT points (default: window_size)
            sample_rate: Sample rate in Hz (default: 44100)
            
        Returns:
            tuple: (time_bins, freq_bins, difference) - Time bins, frequency bins, and difference
        """
        if hop_size is None:
            hop_size = window_size // 4
        
        if nfft is None:
            nfft = window_size
        
        # Ensure signals are the same length
        min_len = min(len(reference), len(implementation))
        reference = reference[:min_len]
        implementation = implementation[:min_len]
        
        # Compute number of frames
        num_frames = 1 + (min_len - window_size) // hop_size
        
        # Compute spectrograms
        spectrogram_ref = self._compute_spectrogram(reference, window_size, hop_size, nfft)
        spectrogram_impl = self._compute_spectrogram(implementation, window_size, hop_size, nfft)
        
        # Compute difference in dB
        epsilon = 1e-10
        difference_db = 20 * np.log10((spectrogram_ref + epsilon) / (spectrogram_impl + epsilon))
        
        # Compute time and frequency bins
        time_bins = np.arange(num_frames) * hop_size / sample_rate
        freq_bins = np.fft.rfftfreq(nfft, 1.0 / sample_rate)
        
        return time_bins, freq_bins, difference_db
    
    def _compute_spectrogram(self, signal, window_size, hop_size, nfft):
        """
        Compute the spectrogram of a signal.
        
        Args:
            signal: Input signal
            window_size: Size of the FFT window
            hop_size: Number of samples between successive windows
            nfft: Number of FFT points
            
        Returns:
            numpy.ndarray: Spectrogram matrix
        """
        # Create window
        window = np.hanning(window_size)
        
        # Compute number of frames
        num_frames = 1 + (len(signal) - window_size) // hop_size
        
        # Initialize spectrogram
        spectrogram = np.zeros((nfft // 2 + 1, num_frames), dtype=np.float32)
        
        # Compute STFT
        for i in range(num_frames):
            start = i * hop_size
            end = start + window_size
            
            if end > len(signal):
                # Zero-pad if necessary
                frame = signal[start:]
                frame = np.pad(frame, (0, end - len(signal)), mode='constant')
            else:
                frame = signal[start:end]
            
            # Apply window
            windowed_frame = frame * window
            
            # Compute FFT
            fft_result = np.fft.rfft(windowed_frame, n=nfft)
            
            # Store magnitude
            spectrogram[:, i] = np.abs(fft_result)
        
        return spectrogram
    
    def error_metrics(self, reference, implementation, sample_rate=44100):
        """
        Compute a comprehensive set of error metrics.
        
        Args:
            reference: Reference signal (numpy array)
            implementation: Implementation signal (numpy array)
            sample_rate: Sample rate in Hz (default: 44100)
            
        Returns:
            dict: Dictionary containing various error metrics
        """
        # Ensure signals are the same length
        min_len = min(len(reference), len(implementation))
        reference = reference[:min_len]
        implementation = implementation[:min_len]
        
        # Compute metrics
        sample_diff = self.sample_difference(reference, implementation)
        rms_diff = self.rms_difference(reference, implementation)
        max_diff = self.max_difference(reference, implementation)
        corr = self.correlation(reference, implementation)
        
        # Spectral metrics
        freqs, spec_diff_db = self.spectral_difference(reference, implementation, sample_rate=sample_rate)
        spec_corr = self.spectral_correlation(reference, implementation)
        
        # Average spectral difference
        avg_spec_diff = float(np.mean(np.abs(spec_diff_db)))
        max_spec_diff = float(np.max(np.abs(spec_diff_db)))
        
        # Time-frequency metrics
        time_bins, freq_bins, tf_diff = self.time_frequency_difference(
            reference, implementation, sample_rate=sample_rate
        )
        avg_tf_diff = float(np.mean(np.abs(tf_diff)))
        
        return {
            'sample_metrics': {
                'rms_difference': rms_diff,
                'max_difference': max_diff,
            },
            'correlation': corr,
            'spectral_metrics': {
                'average_difference_db': avg_spec_diff,
                'max_difference_db': max_spec_diff,
                'correlation': spec_corr,
            },
            'time_frequency_metrics': {
                'average_difference_db': avg_tf_diff,
            }
        }
    
    def compare_impulse_responses(self, ref_ir, impl_ir, sample_rate=44100):
        """
        Compare two impulse responses using specialized metrics.
        
        Args:
            ref_ir: Reference impulse response
            impl_ir: Implementation impulse response
            sample_rate: Sample rate in Hz (default: 44100)
            
        Returns:
            dict: Dictionary containing impulse response comparison metrics
        """
        # Compute basic metrics
        basic_metrics = self.error_metrics(ref_ir, impl_ir, sample_rate)
        
        # Compute spectral difference
        freqs, spec_diff = self.spectral_difference(ref_ir, impl_ir, sample_rate=sample_rate)
        
        # Compute phase difference
        freqs_phase, phase_diff = self.phase_difference(ref_ir, impl_ir, sample_rate=sample_rate)
        
        # Average phase difference (weighted by magnitude)
        fft_ref = np.fft.rfft(ref_ir)
        mag_ref = np.abs(fft_ref)
        weights = mag_ref / (np.sum(mag_ref) + 1e-10)
        avg_phase_diff = float(np.sum(np.abs(phase_diff) * weights))
        
        return {
            **basic_metrics,
            'phase_metrics': {
                'average_phase_difference_rad': avg_phase_diff,
            }
        }


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from signals.sine import SineGenerator
    from signals.noise import NoiseGenerator
    
    # Create metrics and generators
    metrics = ComparisonMetrics()
    sine_gen = SineGenerator(sample_rate=44100, length_samples=44100)
    noise_gen = NoiseGenerator(sample_rate=44100, length_samples=44100)
    
    print("Comparison Metrics Example")
    print("=" * 50)
    
    # Generate test signals
    # Identical signals
    signal1 = sine_gen.generate(frequency=440.0, amplitude=0.5)
    signal2 = sine_gen.generate(frequency=440.0, amplitude=0.5)
    
    # Similar signals (slightly different frequency)
    signal3 = sine_gen.generate(frequency=440.0, amplitude=0.5)
    signal4 = sine_gen.generate(frequency=441.0, amplitude=0.5)
    
    # Different signals
    signal5 = sine_gen.generate(frequency=440.0, amplitude=0.5)
    signal6 = sine_gen.generate(frequency=880.0, amplitude=0.5)
    
    # Uncorrelated signals
    noise1 = noise_gen.white(seed=42)
    noise2 = noise_gen.white(seed=43)
    
    # Compare identical signals
    print("\nComparing identical signals:")
    rms_diff = metrics.rms_difference(signal1, signal2)
    max_diff = metrics.max_difference(signal1, signal2)
    corr = metrics.correlation(signal1, signal2)
    print(f"  RMS difference: {rms_diff:.10f}")
    print(f"  Max difference: {max_diff:.10f}")
    print(f"  Correlation: {corr:.10f}")
    
    # Compare similar signals
    print("\nComparing similar signals (440Hz vs 441Hz):")
    rms_diff = metrics.rms_difference(signal3, signal4)
    corr = metrics.correlation(signal3, signal4)
    freqs, spec_diff = metrics.spectral_difference(signal3, signal4, sample_rate=44100)
    spec_corr = metrics.spectral_correlation(signal3, signal4)
    print(f"  RMS difference: {rms_diff:.6f}")
    print(f"  Correlation: {corr:.6f}")
    print(f"  Spectral correlation: {spec_corr:.6f}")
    
    # Compare different signals
    print("\nComparing different signals (440Hz vs 880Hz):")
    rms_diff = metrics.rms_difference(signal5, signal6)
    corr = metrics.correlation(signal5, signal6)
    spec_corr = metrics.spectral_correlation(signal5, signal6)
    print(f"  RMS difference: {rms_diff:.6f}")
    print(f"  Correlation: {corr:.6f}")
    print(f"  Spectral correlation: {spec_corr:.6f}")
    
    # Compare uncorrelated signals
    print("\nComparing uncorrelated signals (different noise seeds):")
    rms_diff = metrics.rms_difference(noise1, noise2)
    corr = metrics.correlation(noise1, noise2)
    spec_corr = metrics.spectral_correlation(noise1, noise2)
    print(f"  RMS difference: {rms_diff:.6f}")
    print(f"  Correlation: {corr:.6f}")
    print(f"  Spectral correlation: {spec_corr:.6f}")
    
    # Compute comprehensive error metrics
    print("\nComprehensive error metrics (440Hz vs 441Hz):")
    error_metrics = metrics.error_metrics(signal3, signal4, sample_rate=44100)
    for key, value in error_metrics.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 8))
        
        plt.subplot(4, 1, 1)
        plt.plot(signal1[:500], label='Signal 1')
        plt.plot(signal2[:500], label='Signal 2', alpha=0.7)
        plt.title("Identical Signals")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(4, 1, 2)
        plt.plot(signal3[:500], label='440Hz')
        plt.plot(signal4[:500], label='441Hz', alpha=0.7)
        plt.title("Similar Signals (440Hz vs 441Hz)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(4, 1, 3)
        plt.plot(signal5[:500], label='440Hz')
        plt.plot(signal6[:500], label='880Hz', alpha=0.7)
        plt.title("Different Signals (440Hz vs 880Hz)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(4, 1, 4)
        plt.plot(noise1[:500], label='Noise 1')
        plt.plot(noise2[:500], label='Noise 2', alpha=0.7)
        plt.title("Uncorrelated Signals (Different Noise)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

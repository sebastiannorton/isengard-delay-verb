# FFT and Spectral Analysis
# For frequency response and spectral analysis

"""
FFT and spectral analysis tools for audio signal analysis.

Features:
- Magnitude and phase spectrum computation
- Power spectral density estimation
- Spectrogram generation
- Frequency response analysis
- Spectral centroid and flatness
- Windowing functions

Usage:
    from analysis.fft import FFTAnalyzer
    
    # Create analyzer
    analyzer = FFTAnalyzer(sample_rate=44100)
    
    # Compute magnitude spectrum
    frequencies, magnitude = analyzer.magnitude_spectrum(signal)
    
    # Compute phase spectrum
    frequencies, phase = analyzer.phase_spectrum(signal)
    
    # Compute power spectral density
    frequencies, psd = analyzer.power_spectral_density(signal)
    
    # Compute spectrogram
    spectrogram, freq_bins, time_bins = analyzer.spectrogram(signal)
    
    # Analyze frequency response
    freq_response = analyzer.frequency_response(input_signal, output_signal)
"""

import numpy as np


class FFTAnalyzer:
    """
    FFT and spectral analysis for audio signals.
    
    This class provides methods for computing various spectral representations
    of audio signals, including magnitude spectrum, phase spectrum, power spectral
    density, and spectrograms.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
    """
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the FFT analyzer.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
    
    def magnitude_spectrum(self, signal, nfft=None, window=None):
        """
        Compute the magnitude spectrum of a signal.
        
        The magnitude spectrum shows the amplitude of each frequency component
        in the signal.
        
        Args:
            signal: Input signal (numpy array)
            nfft: Number of FFT points (default: length of signal)
            window: Window function to apply (default: None, no windowing)
            
        Returns:
            tuple: (frequencies, magnitude) - Frequency bins and corresponding magnitudes
        """
        if nfft is None:
            nfft = len(signal)
        
        # Apply window if specified
        if window is not None:
            signal = signal * window
        
        # Compute FFT
        fft_result = np.fft.rfft(signal, n=nfft)
        
        # Compute magnitude
        magnitude = np.abs(fft_result)
        
        # Compute frequency bins
        frequencies = np.fft.rfftfreq(nfft, 1.0 / self.sample_rate)
        
        return frequencies, magnitude
    
    def phase_spectrum(self, signal, nfft=None, window=None, unwrap=True):
        """
        Compute the phase spectrum of a signal.
        
        The phase spectrum shows the phase of each frequency component in the signal.
        
        Args:
            signal: Input signal (numpy array)
            nfft: Number of FFT points (default: length of signal)
            window: Window function to apply (default: None, no windowing)
            unwrap: Whether to unwrap the phase (default: True)
            
        Returns:
            tuple: (frequencies, phase) - Frequency bins and corresponding phases
        """
        if nfft is None:
            nfft = len(signal)
        
        # Apply window if specified
        if window is not None:
            signal = signal * window
        
        # Compute FFT
        fft_result = np.fft.rfft(signal, n=nfft)
        
        # Compute phase
        phase = np.angle(fft_result)
        
        # Unwrap phase if requested
        if unwrap:
            phase = np.unwrap(phase)
        
        # Compute frequency bins
        frequencies = np.fft.rfftfreq(nfft, 1.0 / self.sample_rate)
        
        return frequencies, phase
    
    def power_spectral_density(self, signal, nfft=None, window=None):
        """
        Compute the power spectral density (PSD) of a signal.
        
        PSD shows how power is distributed across frequencies.
        
        Args:
            signal: Input signal (numpy array)
            nfft: Number of FFT points (default: length of signal)
            window: Window function to apply (default: None, no windowing)
            
        Returns:
            tuple: (frequencies, psd) - Frequency bins and corresponding PSD values
        """
        if nfft is None:
            nfft = len(signal)
        
        # Apply window if specified
        if window is not None:
            signal = signal * window
        
        # Compute FFT
        fft_result = np.fft.rfft(signal, n=nfft)
        
        # Compute PSD: magnitude squared, normalized by N and sample rate
        psd = (np.abs(fft_result) ** 2) / (len(signal) * self.sample_rate)
        
        # Compute frequency bins
        frequencies = np.fft.rfftfreq(nfft, 1.0 / self.sample_rate)
        
        return frequencies, psd
    
    def spectrogram(self, signal, window_size=1024, hop_size=None, window_type='hanning'):
        """
        Compute the spectrogram of a signal.
        
        A spectrogram shows how the frequency content of a signal changes over time.
        
        Args:
            signal: Input signal (numpy array)
            window_size: Size of the FFT window in samples (default: 1024)
            hop_size: Number of samples between successive windows (default: window_size // 4)
            window_type: Type of window function ('hanning', 'hamming', 'rectangular', etc.) (default: 'hanning')
            
        Returns:
            tuple: (spectrogram, freq_bins, time_bins) - Spectrogram matrix and bin centers
        """
        if hop_size is None:
            hop_size = window_size // 4
        
        # Get window function
        window = self._get_window(window_type, window_size)
        
        # Compute number of frames
        num_frames = 1 + (len(signal) - window_size) // hop_size
        
        # Initialize spectrogram
        spectrogram = np.zeros((window_size // 2 + 1, num_frames), dtype=np.float32)
        
        # Compute frequency bins
        freq_bins = np.fft.rfftfreq(window_size, 1.0 / self.sample_rate)
        
        # Compute time bins (center of each window)
        time_bins = np.arange(num_frames) * hop_size / self.sample_rate
        
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
            fft_result = np.fft.rfft(windowed_frame, n=window_size)
            
            # Store magnitude
            spectrogram[:, i] = np.abs(fft_result)
        
        return spectrogram, freq_bins, time_bins
    
    def frequency_response(self, input_signal, output_signal, nfft=None):
        """
        Compute the frequency response from input and output signals.
        
        The frequency response shows how the system responds to different frequencies.
        
        Args:
            input_signal: Input signal (numpy array)
            output_signal: Output signal (numpy array)
            nfft: Number of FFT points (default: max length of input and output)
            
        Returns:
            tuple: (frequencies, magnitude_response, phase_response) - Frequency response
        """
        if nfft is None:
            nfft = max(len(input_signal), len(output_signal))
        
        # Ensure signals are the same length
        min_len = min(len(input_signal), len(output_signal))
        input_signal = input_signal[:min_len]
        output_signal = output_signal[:min_len]
        
        # Compute FFT of input and output
        fft_input = np.fft.rfft(input_signal, n=nfft)
        fft_output = np.fft.rfft(output_signal, n=nfft)
        
        # Compute frequency response: H(f) = Y(f) / X(f)
        # Add small epsilon to avoid division by zero
        epsilon = 1e-10
        magnitude_response = np.abs(fft_output) / (np.abs(fft_input) + epsilon)
        phase_response = np.angle(fft_output) - np.angle(fft_input)
        
        # Compute frequency bins
        frequencies = np.fft.rfftfreq(nfft, 1.0 / self.sample_rate)
        
        return frequencies, magnitude_response, phase_response
    
    def spectral_centroid(self, signal, nfft=None, window=None):
        """
        Compute the spectral centroid of a signal.
        
        The spectral centroid is the "center of mass" of the spectrum, indicating
        where the energy is concentrated.
        
        Args:
            signal: Input signal (numpy array)
            nfft: Number of FFT points (default: length of signal)
            window: Window function to apply (default: None, no windowing)
            
        Returns:
            float: Spectral centroid in Hz
        """
        frequencies, magnitude = self.magnitude_spectrum(signal, nfft, window)
        
        # Compute spectral centroid
        # centroid = sum(f_i * mag_i) / sum(mag_i)
        if np.sum(magnitude) > 0:
            centroid = np.sum(frequencies * magnitude) / np.sum(magnitude)
        else:
            centroid = 0.0
        
        return centroid
    
    def spectral_flatness(self, signal, nfft=None, window=None):
        """
        Compute the spectral flatness of a signal.
        
        Spectral flatness measures how "flat" or "peaky" the spectrum is.
        - Flatness = 1: Perfectly flat spectrum (like white noise)
        - Flatness = 0: Very peaky spectrum (like a sine wave)
        
        Args:
            signal: Input signal (numpy array)
            nfft: Number of FFT points (default: length of signal)
            window: Window function to apply (default: None, no windowing)
            
        Returns:
            float: Spectral flatness (0 to 1)
        """
        frequencies, magnitude = self.magnitude_spectrum(signal, nfft, window)
        
        # Compute geometric mean and arithmetic mean of magnitude
        # Skip DC component (index 0) as it's usually very large
        magnitude = magnitude[1:]
        
        if len(magnitude) == 0 or np.sum(magnitude) == 0:
            return 0.0
        
        # Arithmetic mean
        am = np.mean(magnitude)
        
        # Geometric mean (add epsilon to avoid log(0))
        epsilon = 1e-10
        gm = np.exp(np.mean(np.log(magnitude + epsilon)))
        
        # Spectral flatness = gm / am
        flatness = gm / (am + epsilon)
        
        return flatness
    
    def spectral_rolloff(self, signal, percentile=0.85, nfft=None, window=None):
        """
        Compute the spectral rolloff frequency.
        
        The spectral rolloff is the frequency below which a specified percentage
        of the total spectral energy is contained.
        
        Args:
            signal: Input signal (numpy array)
            percentile: Percentage of energy to include (default: 0.85)
            nfft: Number of FFT points (default: length of signal)
            window: Window function to apply (default: None, no windowing)
            
        Returns:
            float: Rolloff frequency in Hz
        """
        frequencies, magnitude = self.magnitude_spectrum(signal, nfft, window)
        
        # Compute cumulative sum of magnitude squared (energy)
        energy = magnitude ** 2
        cumulative_energy = np.cumsum(energy)
        total_energy = cumulative_energy[-1]
        
        # Find frequency where cumulative energy reaches percentile
        target_energy = percentile * total_energy
        
        # Find first index where cumulative energy >= target
        idx = np.searchsorted(cumulative_energy, target_energy)
        
        if idx < len(frequencies):
            return frequencies[idx]
        else:
            return frequencies[-1]
    
    def _get_window(self, window_type, length):
        """
        Get a window function of the specified type and length.
        
        Args:
            window_type: Type of window ('hanning', 'hamming', 'rectangular', etc.)
            length: Length of the window in samples
            
        Returns:
            numpy.ndarray: Window function
        """
        if window_type == 'hanning':
            return np.hanning(length).astype(np.float32)
        elif window_type == 'hamming':
            return np.hamming(length).astype(np.float32)
        elif window_type == 'rectangular':
            return np.ones(length, dtype=np.float32)
        elif window_type == 'bartlett':
            return np.bartlett(length).astype(np.float32)
        elif window_type == 'blackman':
            return np.blackman(length).astype(np.float32)
        elif window_type == 'parzen':
            return np.parzen(length).astype(np.float32)
        else:
            raise ValueError(f"Unknown window type: {window_type}")
    
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
    from signals.noise import NoiseGenerator
    
    # Create analyzers and generators
    fft_analyzer = FFTAnalyzer(sample_rate=44100)
    sine_gen = SineGenerator(sample_rate=44100, length_samples=44100)
    noise_gen = NoiseGenerator(sample_rate=44100, length_samples=44100)
    
    print("FFT Analyzer Example")
    print("=" * 50)
    
    # Generate test signals
    sine_440 = sine_gen.generate(frequency=440.0, amplitude=0.5)
    sine_1000 = sine_gen.generate(frequency=1000.0, amplitude=0.5)
    white_noise = noise_gen.white(seed=42)
    multi_tone = sine_gen.generate_multi(
        frequencies=[100.0, 200.0, 400.0, 800.0],
        amplitudes=[0.25, 0.25, 0.25, 0.25]
    )
    
    # Analyze sine wave
    print("\nAnalyzing 440Hz sine wave:")
    freqs, mag = fft_analyzer.magnitude_spectrum(sine_440, nfft=8192)
    peak_freq = freqs[np.argmax(mag)]
    print(f"  Peak frequency: {peak_freq:.1f} Hz (expected: 440.0 Hz)")
    
    # Analyze white noise
    print("\nAnalyzing white noise:")
    freqs, mag = fft_analyzer.magnitude_spectrum(white_noise, nfft=8192)
    centroid = fft_analyzer.spectral_centroid(white_noise, nfft=8192)
    flatness = fft_analyzer.spectral_flatness(white_noise, nfft=8192)
    rolloff = fft_analyzer.spectral_rolloff(white_noise, percentile=0.85, nfft=8192)
    print(f"  Spectral centroid: {centroid:.1f} Hz")
    print(f"  Spectral flatness: {flatness:.3f}")
    print(f"  85% rolloff frequency: {rolloff:.1f} Hz")
    
    # Analyze multi-tone
    print("\nAnalyzing multi-tone signal:")
    freqs, mag = fft_analyzer.magnitude_spectrum(multi_tone, nfft=8192)
    peaks = np.where(mag > 0.1 * np.max(mag))[0]
    peak_freqs = freqs[peaks]
    print(f"  Detected peaks: {peak_freqs[:4]}")
    
    # Compute spectrogram
    print("\nComputing spectrogram of multi-tone signal:")
    spectrogram, freq_bins, time_bins = fft_analyzer.spectrogram(
        multi_tone, window_size=1024, hop_size=256
    )
    print(f"  Spectrogram shape: {spectrogram.shape}")
    print(f"  Frequency bins: {len(freq_bins)} ({freq_bins[0]:.1f} - {freq_bins[-1]:.1f} Hz)")
    print(f"  Time bins: {len(time_bins)} ({time_bins[0]:.3f} - {time_bins[-1]:.3f} s)")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 10))
        
        plt.subplot(4, 1, 1)
        plt.plot(freqs[:1000], mag[:1000])
        plt.title("440Hz Sine Wave - Magnitude Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.xlim(0, 1000)
        plt.grid(True)
        
        plt.subplot(4, 1, 2)
        plt.plot(freqs[:5000], mag[:5000])
        plt.title("White Noise - Magnitude Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.xlim(0, 5000)
        plt.grid(True)
        
        plt.subplot(4, 1, 3)
        plt.plot(freqs[:1000], mag[:1000])
        plt.title("Multi-Tone - Magnitude Spectrum")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.xlim(0, 1000)
        plt.grid(True)
        
        plt.subplot(4, 1, 4)
        plt.imshow(spectrogram[:100, :50], aspect='auto', origin='lower',
                   extent=[time_bins[0], time_bins[49], freq_bins[0], freq_bins[99]])
        plt.title("Multi-Tone - Spectrogram")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.colorbar(label='Magnitude')
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

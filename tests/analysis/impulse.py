# Impulse Response Analyzer
# For delay time, echo density, and system identification

"""
Impulse response analysis tools for audio system characterization.

Features:
- Delay time measurement
- Echo density analysis
- Early reflection detection
- Late reverb characterization
- System identification

Usage:
    from analysis.impulse import ImpulseAnalyzer
    
    # Create analyzer
    analyzer = ImpulseAnalyzer(sample_rate=44100)
    
    # Measure delay time
    delay_ms = analyzer.measure_delay(impulse_response)
    
    # Measure echo density
    density = analyzer.measure_echo_density(impulse_response)
    
    # Detect early reflections
    reflections = analyzer.detect_early_reflections(impulse_response)
    
    # Analyze decay
    decay_time = analyzer.measure_decay(impulse_response, threshold_db=-60)
"""

import numpy as np


class ImpulseAnalyzer:
    """
    Analyze impulse responses to characterize audio systems.
    
    An impulse response is the output of a system when the input is an impulse.
    It contains complete information about the system's behavior.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
    """
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the impulse analyzer.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
    
    def measure_delay(self, impulse_response, threshold=0.01):
        """
        Measure the delay time from an impulse response.
        
        This finds the first significant peak in the impulse response,
        which corresponds to the delay time of the system.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            threshold: Threshold for detecting the first peak (0.0 to 1.0) (default: 0.01)
            
        Returns:
            float: Delay time in milliseconds
        """
        # Normalize the impulse response
        max_val = np.max(np.abs(impulse_response))
        if max_val == 0:
            return 0.0
        
        normalized = np.abs(impulse_response) / max_val
        
        # Find first sample above threshold
        above_threshold = np.where(normalized > threshold)[0]
        
        if len(above_threshold) > 0:
            first_sample = above_threshold[0]
            delay_ms = first_sample / self.sample_rate * 1000
            return delay_ms
        else:
            return 0.0
    
    def measure_delay_peak(self, impulse_response, min_peak_height=0.1):
        """
        Measure the delay time by finding the first peak in the impulse response.
        
        This is more robust than threshold-based detection as it looks for
        actual peaks rather than just values above a threshold.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            min_peak_height: Minimum height for a peak to be considered (0.0 to 1.0) (default: 0.1)
            
        Returns:
            float: Delay time in milliseconds
        """
        # Normalize the impulse response
        max_val = np.max(np.abs(impulse_response))
        if max_val == 0:
            return 0.0
        
        normalized = np.abs(impulse_response) / max_val
        
        # Find peaks (local maxima)
        peaks = self._find_peaks(normalized, min_height=min_peak_height)
        
        if len(peaks) > 0:
            first_peak = peaks[0]
            delay_ms = first_peak / self.sample_rate * 1000
            return delay_ms
        else:
            return 0.0
    
    def measure_echo_density(self, impulse_response, window_ms=100, threshold=0.01):
        """
        Measure the echo density (echoes per second) from an impulse response.
        
        Echo density is a measure of how "dense" the echo pattern is, which
        relates to the diffusion and modulation in the system.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            window_ms: Size of the analysis window in milliseconds (default: 100)
            threshold: Threshold for detecting echoes (0.0 to 1.0) (default: 0.01)
            
        Returns:
            float: Average echo density in echoes per second
        """
        # Normalize the impulse response
        max_val = np.max(np.abs(impulse_response))
        if max_val == 0:
            return 0.0
        
        normalized = np.abs(impulse_response) / max_val
        
        # Convert window size to samples
        window_samples = int(window_ms * self.sample_rate / 1000)
        
        # Process in windows
        densities = []
        for i in range(0, len(normalized), window_samples):
            window = normalized[i:i + window_samples]
            
            if len(window) == 0:
                continue
            
            # Count peaks above threshold
            peaks = self._find_peaks(window, min_height=threshold)
            densities.append(len(peaks) / (window_ms / 1000))
        
        if len(densities) > 0:
            return np.mean(densities)
        else:
            return 0.0
    
    def detect_early_reflections(self, impulse_response, max_delay_ms=100, 
                                  min_peak_height=0.01, min_peak_distance_ms=1.0):
        """
        Detect early reflections in an impulse response.
        
        Early reflections are distinct echoes that arrive shortly after the
        direct sound. They are important for spatial perception and room acoustics.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            max_delay_ms: Maximum delay for early reflections in milliseconds (default: 100)
            min_peak_height: Minimum height for a peak to be considered (0.0 to 1.0) (default: 0.01)
            min_peak_distance_ms: Minimum distance between peaks in milliseconds (default: 1.0)
            
        Returns:
            list: List of tuples (delay_ms, amplitude) for each early reflection
        """
        # Normalize the impulse response
        max_val = np.max(np.abs(impulse_response))
        if max_val == 0:
            return []
        
        normalized = np.abs(impulse_response) / max_val
        
        # Convert time limits to samples
        max_delay_samples = int(max_delay_ms * self.sample_rate / 1000)
        min_peak_distance_samples = int(min_peak_distance_ms * self.sample_rate / 1000)
        
        # Only consider the first part of the response
        early_part = normalized[:max_delay_samples]
        
        # Find peaks
        peaks = self._find_peaks(early_part, min_height=min_peak_height, 
                                min_distance=min_peak_distance_samples)
        
        # Convert to milliseconds and amplitudes
        reflections = []
        for peak in peaks:
            delay_ms = peak / self.sample_rate * 1000
            amplitude = early_part[peak]
            reflections.append((delay_ms, amplitude))
        
        return reflections
    
    def measure_decay(self, impulse_response, threshold_db=-60):
        """
        Measure the decay time from an impulse response.
        
        The decay time is the time it takes for the signal to decay by a
        specified number of decibels (e.g., T60 for 60dB decay).
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            threshold_db: Decay threshold in dB (default: -60)
            
        Returns:
            float: Decay time in milliseconds
        """
        # Convert to dB
        epsilon = 1e-10
        db_response = 20 * np.log10(np.abs(impulse_response) + epsilon)
        
        # Find initial level (first 10% of response)
        initial_window = int(0.1 * len(db_response))
        if initial_window > 0:
            initial_db = np.mean(db_response[:initial_window])
        else:
            initial_db = np.max(db_response)
        
        # Target level
        target_db = initial_db + threshold_db
        
        # Find where response drops below target
        below_target = np.where(db_response < target_db)[0]
        
        if len(below_target) > 0:
            decay_samples = below_target[0]
            decay_ms = decay_samples / self.sample_rate * 1000
            return decay_ms
        else:
            # If never drops below threshold, return full length
            return len(impulse_response) / self.sample_rate * 1000
    
    def measure_t60(self, impulse_response):
        """
        Measure T60 (time to decay by 60dB) from an impulse response.
        
        T60 is a standard measure of reverb time in room acoustics.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            
        Returns:
            float: T60 in milliseconds
        """
        return self.measure_decay(impulse_response, threshold_db=-60)
    
    def measure_t30(self, impulse_response):
        """
        Measure T30 (time to decay by 30dB) from an impulse response.
        
        T30 is often more reliable than T60 for noisy measurements.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            
        Returns:
            float: T30 in milliseconds
        """
        return self.measure_decay(impulse_response, threshold_db=-30)
    
    def measure_t20(self, impulse_response):
        """
        Measure T20 (time to decay by 20dB) from an impulse response.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            
        Returns:
            float: T20 in milliseconds
        """
        return self.measure_decay(impulse_response, threshold_db=-20)
    
    def measure_early_decay_time(self, impulse_response, end_time_ms=100):
        """
        Measure Early Decay Time (EDT) from an impulse response.
        
        EDT is the time it takes for the energy to decay by 10dB in the
        first part of the response. It's a measure of the early decay rate.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            end_time_ms: Time to consider for early decay in milliseconds (default: 100)
            
        Returns:
            float: EDT in milliseconds
        """
        # Convert to dB
        epsilon = 1e-10
        db_response = 20 * np.log10(np.abs(impulse_response) + epsilon)
        
        # Only consider the first part
        end_samples = int(end_time_ms * self.sample_rate / 1000)
        early_db = db_response[:end_samples]
        
        if len(early_db) == 0:
            return 0.0
        
        # Find initial level
        initial_db = early_db[0]
        target_db = initial_db - 10  # 10dB decay
        
        # Find where response drops below target
        below_target = np.where(early_db < target_db)[0]
        
        if len(below_target) > 0:
            decay_samples = below_target[0]
            decay_ms = decay_samples / self.sample_rate * 1000
            return decay_ms * 6  # Scale to equivalent T60
        else:
            return 0.0
    
    def measure_clarity(self, impulse_response, time_ms=50):
        """
        Measure clarity (C50 or C80) from an impulse response.
        
        Clarity is the ratio of early energy to late energy, measured in dB.
        C50 is commonly used in room acoustics.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            time_ms: Time boundary between early and late energy in milliseconds (default: 50)
            
        Returns:
            float: Clarity in dB
        """
        # Convert to energy (squared)
        energy = impulse_response ** 2
        
        # Split into early and late parts
        boundary_samples = int(time_ms * self.sample_rate / 1000)
        early_energy = np.sum(energy[:boundary_samples])
        late_energy = np.sum(energy[boundary_samples:])
        
        # Avoid division by zero
        epsilon = 1e-10
        
        # Clarity in dB
        clarity_db = 10 * np.log10((early_energy + epsilon) / (late_energy + epsilon))
        
        return clarity_db
    
    def measure_definition(self, impulse_response, time_ms=50):
        """
        Measure definition (D50) from an impulse response.
        
        Definition is the ratio of early energy to total energy.
        
        Args:
            impulse_response: Impulse response signal (numpy array)
            time_ms: Time boundary for early energy in milliseconds (default: 50)
            
        Returns:
            float: Definition (0.0 to 1.0)
        """
        # Convert to energy (squared)
        energy = impulse_response ** 2
        
        # Split into early and total parts
        boundary_samples = int(time_ms * self.sample_rate / 1000)
        early_energy = np.sum(energy[:boundary_samples])
        total_energy = np.sum(energy)
        
        # Avoid division by zero
        epsilon = 1e-10
        
        # Definition
        definition = early_energy / (total_energy + epsilon)
        
        return definition
    
    def _find_peaks(self, signal, min_height=0.0, min_distance=1):
        """
        Find local maxima (peaks) in a signal.
        
        Args:
            signal: Input signal (numpy array)
            min_height: Minimum height for a peak to be considered
            min_distance: Minimum distance between peaks in samples
            
        Returns:
            numpy.ndarray: Indices of peaks
        """
        # Find all local maxima
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
                if signal[i] >= min_height:
                    # Check distance from previous peak
                    if len(peaks) == 0 or i - peaks[-1] >= min_distance:
                        peaks.append(i)
        
        return np.array(peaks, dtype=int)
    
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
    from signals.impulse import ImpulseGenerator
    from signals.noise import NoiseGenerator
    import scipy.signal
    
    # Create analyzers and generators
    impulse_analyzer = ImpulseAnalyzer(sample_rate=44100)
    impulse_gen = ImpulseGenerator(sample_rate=44100, length_samples=44100)
    
    print("Impulse Response Analyzer Example")
    print("=" * 50)
    
    # Generate a test impulse response (simulated delay + reverb)
    # Create a simple impulse response with a delay and some echoes
    ir_length = 44100
    impulse_response = np.zeros(ir_length, dtype=np.float32)
    
    # Direct sound at 0ms
    impulse_response[0] = 1.0
    
    # Add some echoes
    echo_delays_ms = [50, 100, 150, 200, 250]
    echo_amplitudes = [0.5, 0.3, 0.2, 0.1, 0.05]
    
    for delay_ms, amp in zip(echo_delays_ms, echo_amplitudes):
        delay_samples = int(delay_ms * 44100 / 1000)
        if delay_samples < ir_length:
            impulse_response[delay_samples] = amp
    
    # Add some noise to make it more realistic
    noise = NoiseGenerator(sample_rate=44100, length_samples=ir_length).white(seed=42) * 0.01
    impulse_response += noise
    
    # Analyze the impulse response
    print("\nAnalyzing simulated impulse response:")
    
    # Measure delay
    delay_ms = impulse_analyzer.measure_delay(impulse_response)
    print(f"  Delay (threshold): {delay_ms:.2f} ms")
    
    delay_peak_ms = impulse_analyzer.measure_delay_peak(impulse_response)
    print(f"  Delay (peak): {delay_peak_ms:.2f} ms")
    
    # Measure echo density
    density = impulse_analyzer.measure_echo_density(impulse_response, window_ms=50)
    print(f"  Echo density: {density:.2f} echoes/second")
    
    # Detect early reflections
    reflections = impulse_analyzer.detect_early_reflections(impulse_response, max_delay_ms=300)
    print(f"  Early reflections: {len(reflections)}")
    for delay, amp in reflections[:5]:  # Show first 5
        print(f"    - {delay:.1f}ms: {amp:.3f}")
    
    # Measure decay times
    t60 = impulse_analyzer.measure_t60(impulse_response)
    t30 = impulse_analyzer.measure_t30(impulse_response)
    t20 = impulse_analyzer.measure_t20(impulse_response)
    print(f"  T60: {t60:.2f} ms")
    print(f"  T30: {t30:.2f} ms")
    print(f"  T20: {t20:.2f} ms")
    
    # Measure clarity and definition
    c50 = impulse_analyzer.measure_clarity(impulse_response, time_ms=50)
    d50 = impulse_analyzer.measure_definition(impulse_response, time_ms=50)
    print(f"  C50: {c50:.2f} dB")
    print(f"  D50: {d50:.3f}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 8))
        
        plt.subplot(3, 1, 1)
        plt.plot(impulse_response[:1000])
        plt.title("Simulated Impulse Response (First 1000 Samples)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(3, 1, 2)
        # Plot in dB
        db_response = 20 * np.log10(np.abs(impulse_response[:10000]) + 1e-10)
        plt.plot(db_response)
        plt.title("Impulse Response (dB)")
        plt.xlabel("Sample")
        plt.ylabel("Level (dB)")
        plt.axhline(y=-60, color='r', linestyle='--', label='-60dB')
        plt.grid(True)
        plt.legend()
        
        plt.subplot(3, 1, 3)
        # Plot early part with reflections
        plt.stem(np.arange(len(impulse_response[:3000])) / 44100 * 1000, impulse_response[:3000], use_line_collection=True)
        plt.title("Early Part with Reflections (First 3000 Samples)")
        plt.xlabel("Time (ms)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

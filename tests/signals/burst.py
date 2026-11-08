# Tone Burst Signal Generator
# For transient response analysis

"""
Tone burst signal generator for transient response analysis.

Features:
- Short tone bursts with configurable duration
- Multiple envelope types (rectangular, hanning, hamming, triangular, exponential)
- Mono and stereo generation
- Configurable frequency and amplitude
- Configurable signal length
- Deterministic output
- Sample-rate independent

Usage:
    from signals.burst import BurstGenerator
    
    # Create generator
    gen = BurstGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate tone burst at 1000Hz, 100ms duration
    signal = gen.generate(frequency=1000.0, duration_ms=100.0)
    
    # Generate tone burst with Hanning envelope
    signal = gen.generate(frequency=1000.0, duration_ms=100.0, envelope='hanning')
    
    # Generate tone burst at specific position
    signal = gen.generate(frequency=1000.0, duration_ms=100.0, position_ms=500.0)
    
    # Generate stereo tone burst
    signal_l, signal_r = gen.generate_stereo(frequency=1000.0, duration_ms=100.0)
"""

import numpy as np


class BurstGenerator:
    """
    Generate tone burst signals for transient response analysis.
    
    A tone burst is a short sine wave with an envelope, used for testing
    transient responses, attack/release times, and stability of audio systems.
    The envelope shapes the beginning and end of the burst to avoid clicks.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
        length_samples (int): Length of generated signals in samples (default: 44100)
    """
    
    def __init__(self, sample_rate=44100, length_samples=44100):
        """
        Initialize the burst generator.
        
        Args:
            sample_rate: Sample rate in Hz
            length_samples: Length of generated signals in samples
        """
        self.sample_rate = float(sample_rate)
        self.length_samples = int(length_samples)
    
    def generate(self, frequency, duration_ms, amplitude=0.5, phase=0.0,
                 position_ms=0.0, envelope='hanning'):
        """
        Generate a mono tone burst signal.
        
        Args:
            frequency: Frequency of the tone in Hz
            duration_ms: Duration of the burst in milliseconds
            amplitude: Amplitude of the tone (default: 0.5)
            phase: Phase offset in radians (default: 0.0)
            position_ms: Position of the burst in milliseconds (default: 0.0)
            envelope: Envelope type ('rectangular', 'hanning', 'hamming', 
                     'triangular', 'exponential', 'cosine') (default: 'hanning')
            
        Returns:
            numpy.ndarray: Mono tone burst signal of length length_samples
        """
        # Validate frequency
        if frequency <= 0:
            raise ValueError(f"Frequency must be positive, got {frequency}")
        
        if frequency > self.sample_rate / 2:
            raise ValueError(f"Frequency {frequency} Hz exceeds Nyquist frequency ({self.sample_rate/2} Hz)")
        
        # Convert milliseconds to samples
        duration_samples = int(duration_ms * self.sample_rate / 1000)
        position_samples = int(position_ms * self.sample_rate / 1000)
        
        # Validate duration
        if duration_samples <= 0:
            raise ValueError(f"Duration must be positive, got {duration_ms}ms")
        
        if duration_samples > self.length_samples:
            raise ValueError(f"Duration {duration_samples} samples exceeds signal length {self.length_samples}")
        
        # Validate position
        if position_samples < 0:
            raise ValueError(f"Position must be non-negative, got {position_ms}ms")
        
        if position_samples + duration_samples > self.length_samples:
            raise ValueError(f"Burst at position {position_samples} with duration {duration_samples} "
                           f"exceeds signal length {self.length_samples}")
        
        # Generate signal
        signal = np.zeros(self.length_samples, dtype=np.float32)
        
        # Generate time array for burst
        t = np.arange(duration_samples, dtype=np.float32) / self.sample_rate
        
        # Generate sine wave for burst
        tone = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        
        # Apply envelope
        envelope_window = self._get_envelope_window(envelope, duration_samples)
        burst = tone * envelope_window
        
        # Place burst at specified position
        signal[position_samples:position_samples + duration_samples] = burst
        
        return signal
    
    def generate_stereo(self, frequency, duration_ms, amplitude_l=0.5, amplitude_r=0.5,
                        phase_l=0.0, phase_r=0.0, position_ms=0.0, envelope='hanning'):
        """
        Generate a stereo tone burst signal.
        
        Args:
            frequency: Frequency of the tone in Hz
            duration_ms: Duration of the burst in milliseconds
            amplitude_l: Amplitude for left channel (default: 0.5)
            amplitude_r: Amplitude for right channel (default: 0.5)
            phase_l: Phase offset for left channel in radians (default: 0.0)
            phase_r: Phase offset for right channel in radians (default: 0.0)
            position_ms: Position of the burst in milliseconds (default: 0.0)
            envelope: Envelope type (default: 'hanning')
            
        Returns:
            tuple: (left_signal, right_signal) - Two numpy arrays of length length_samples
        """
        # Generate left channel
        signal_l = self.generate(
            frequency=frequency,
            duration_ms=duration_ms,
            amplitude=amplitude_l,
            phase=phase_l,
            position_ms=position_ms,
            envelope=envelope
        )
        
        # Generate right channel
        signal_r = self.generate(
            frequency=frequency,
            duration_ms=duration_ms,
            amplitude=amplitude_r,
            phase=phase_r,
            position_ms=position_ms,
            envelope=envelope
        )
        
        return signal_l, signal_r
    
    def generate_multi(self, frequencies, duration_ms, amplitudes=None, phases=None,
                       position_ms=0.0, envelope='hanning'):
        """
        Generate a signal with multiple tone bursts at the same position.
        
        Args:
            frequencies: List of frequencies in Hz
            duration_ms: Duration of each burst in milliseconds
            amplitudes: List of amplitudes (default: all 0.5 / len(frequencies))
            phases: List of phase offsets in radians (default: all 0.0)
            position_ms: Position of the bursts in milliseconds (default: 0.0)
            envelope: Envelope type (default: 'hanning')
            
        Returns:
            numpy.ndarray: Mono signal with multiple tone bursts
        """
        if amplitudes is None:
            amplitudes = [0.5 / len(frequencies)] * len(frequencies)
        
        if phases is None:
            phases = [0.0] * len(frequencies)
        
        if len(frequencies) != len(amplitudes) or len(frequencies) != len(phases):
            raise ValueError("Frequencies, amplitudes, and phases must have the same length")
        
        # Generate signal
        signal = np.zeros(self.length_samples, dtype=np.float32)
        
        # Convert milliseconds to samples
        duration_samples = int(duration_ms * self.sample_rate / 1000)
        position_samples = int(position_ms * self.sample_rate / 1000)
        
        # Validate
        if position_samples + duration_samples > self.length_samples:
            raise ValueError(f"Bursts exceed signal length")
        
        # Generate time array for burst
        t = np.arange(duration_samples, dtype=np.float32) / self.sample_rate
        
        # Generate envelope window
        envelope_window = self._get_envelope_window(envelope, duration_samples)
        
        # Sum all tone bursts
        for freq, amp, phase in zip(frequencies, amplitudes, phases):
            if freq > 0 and freq <= self.sample_rate / 2:
                tone = amp * np.sin(2 * np.pi * freq * t + phase)
                signal[position_samples:position_samples + duration_samples] += tone * envelope_window
        
        return signal
    
    def generate_sequence(self, bursts, envelope='hanning'):
        """
        Generate a sequence of tone bursts at different positions.
        
        Args:
            bursts: List of burst specifications, each as a dict with:
                    - frequency: Frequency in Hz
                    - duration_ms: Duration in milliseconds
                    - amplitude: Amplitude (default: 0.5)
                    - phase: Phase offset in radians (default: 0.0)
                    - position_ms: Position in milliseconds
            envelope: Envelope type (default: 'hanning')
            
        Returns:
            numpy.ndarray: Mono signal with sequence of tone bursts
        """
        signal = np.zeros(self.length_samples, dtype=np.float32)
        
        for burst in bursts:
            freq = burst.get('frequency')
            duration_ms = burst.get('duration_ms')
            amplitude = burst.get('amplitude', 0.5)
            phase = burst.get('phase', 0.0)
            position_ms = burst.get('position_ms', 0.0)
            
            burst_signal = self.generate(
                frequency=freq,
                duration_ms=duration_ms,
                amplitude=amplitude,
                phase=phase,
                position_ms=position_ms,
                envelope=envelope
            )
            
            signal += burst_signal
        
        # Clip to prevent overflow
        signal = np.clip(signal, -1.0, 1.0)
        
        return signal
    
    def _get_envelope_window(self, envelope, length):
        """
        Get the envelope window for the specified type and length.
        
        Args:
            envelope: Envelope type
            length: Length of the window in samples
            
        Returns:
            numpy.ndarray: Envelope window of specified length
        """
        if envelope == 'rectangular':
            return np.ones(length, dtype=np.float32)
        
        elif envelope == 'hanning':
            return np.hanning(length).astype(np.float32)
        
        elif envelope == 'hamming':
            return np.hamming(length).astype(np.float32)
        
        elif envelope == 'triangular':
            # Triangular window: linear rise and fall
            half = length // 2
            window = np.zeros(length, dtype=np.float32)
            window[:half] = np.linspace(0.0, 1.0, half)
            window[half:] = np.linspace(1.0, 0.0, length - half)
            return window
        
        elif envelope == 'exponential':
            # Exponential rise and fall
            t = np.linspace(0.0, 1.0, length)
            # Rise: 1 - exp(-10 * t)
            # Fall: exp(-10 * (1 - t))
            rise = 1.0 - np.exp(-10.0 * t)
            fall = np.exp(-10.0 * (1.0 - t))
            window = rise * fall
            return window.astype(np.float32)
        
        elif envelope == 'cosine':
            # Cosine window: sin(pi * t)^2
            t = np.linspace(0.0, 1.0, length)
            window = np.sin(np.pi * t) ** 2
            return window.astype(np.float32)
        
        else:
            raise ValueError(f"Unknown envelope type: {envelope}. Use 'rectangular', 'hanning', "
                           f"'hamming', 'triangular', 'exponential', or 'cosine'.")
    
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
    gen = BurstGenerator(sample_rate=44100, length_samples=44100)
    
    print(f"Sample rate: {gen.sample_rate} Hz")
    print(f"Length: {gen.length_samples} samples ({gen.duration_seconds:.2f} seconds)")
    print(f"Nyquist frequency: {gen.nyquist_frequency:.1f} Hz")
    
    # Generate tone burst at 1000Hz, 100ms duration
    burst_1000 = gen.generate(frequency=1000.0, duration_ms=100.0)
    print(f"\nGenerated 1000Hz burst (100ms): max={burst_1000.max():.3f}, min={burst_1000.min():.3f}")
    
    # Generate tone burst with Hanning envelope
    burst_hanning = gen.generate(frequency=1000.0, duration_ms=100.0, envelope='hanning')
    print(f"Generated burst with Hanning: max={burst_hanning.max():.3f}, min={burst_hanning.min():.3f}")
    
    # Generate tone burst at specific position
    burst_positioned = gen.generate(frequency=1000.0, duration_ms=100.0, position_ms=500.0)
    burst_start = np.where(burst_positioned != 0)[0][0] if np.any(burst_positioned != 0) else 0
    print(f"Generated positioned burst: starts at sample {burst_start} (expected ~22050)")
    
    # Generate stereo tone burst
    burst_l, burst_r = gen.generate_stereo(frequency=1000.0, duration_ms=100.0)
    print(f"Generated stereo burst: L max={burst_l.max():.3f}, R max={burst_r.max():.3f}")
    
    # Generate multi-frequency burst
    burst_multi = gen.generate_multi(
        frequencies=[100.0, 200.0, 400.0],
        duration_ms=100.0,
        amplitudes=[0.3, 0.2, 0.1]
    )
    print(f"Generated multi-frequency burst: max={burst_multi.max():.3f}, min={burst_multi.min():.3f}")
    
    # Generate sequence of bursts
    bursts = [
        {'frequency': 100.0, 'duration_ms': 50.0, 'position_ms': 0.0},
        {'frequency': 500.0, 'duration_ms': 50.0, 'position_ms': 200.0},
        {'frequency': 1000.0, 'duration_ms': 50.0, 'position_ms': 400.0}
    ]
    burst_sequence = gen.generate_sequence(bursts)
    print(f"Generated burst sequence: max={burst_sequence.max():.3f}, min={burst_sequence.min():.3f}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 10))
        
        plt.subplot(5, 1, 1)
        plt.plot(burst_1000[:1000])
        plt.title("1000Hz Tone Burst (100ms, Rectangular)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(5, 1, 2)
        plt.plot(burst_hanning[:1000])
        plt.title("1000Hz Tone Burst (100ms, Hanning)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(5, 1, 3)
        plt.plot(burst_positioned[20000:23000])
        plt.title("1000Hz Tone Burst at Position 500ms")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.subplot(5, 1, 4)
        plt.plot(burst_l[:1000], label='Left')
        plt.plot(burst_r[:1000], label='Right', alpha=0.7)
        plt.title("Stereo Tone Burst")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid(True)
        
        plt.subplot(5, 1, 5)
        plt.plot(burst_sequence[:5000])
        plt.title("Burst Sequence (100Hz, 500Hz, 1000Hz)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

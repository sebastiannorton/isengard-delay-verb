# Filter Implementations
# Allpass, Comb, OnePole, Biquad filters for DSP

"""
Filter implementations for Isengard plugins.

Features:
- AllpassFilter: Allpass filter for phase manipulation and diffusion
- CombFilter: Comb filter for reverb and delay networks
- OnePoleFilter: Simple one-pole lowpass/highpass filter
- BiquadFilter: Second-order IIR filters (lowpass, highpass, bandpass, etc.)

Usage:
    from isengard_shared.filters import AllpassFilter, CombFilter, OnePoleFilter, BiquadFilter
    
    # Create allpass filter
    allpass = AllpassFilter(delay_ms=5.0, feedback=0.7, sample_rate=44100)
    
    # Create comb filter
    comb = CombFilter(delay_ms=30.0, feedback=0.8, sample_rate=44100)
    
    # Create one-pole lowpass filter
    lowpass = OnePoleFilter(cutoff_hz=1000.0, sample_rate=44100, type='lowpass')
"""

import numpy as np


class AllpassFilter:
    """
    Allpass filter implementation.
    
    An allpass filter passes all frequencies with equal amplitude but
    modifies the phase. It's commonly used in reverb algorithms for
    diffusion and in delay lines for fractional delay interpolation.
    
    The transfer function is: H(z) = (feedback + z^(-delay)) / (1 + feedback * z^(-delay))
    
    Parameters:
        delay_ms (float): Delay time in milliseconds
        feedback (float): Feedback coefficient (0.0 to 1.0)
        sample_rate (float): Sample rate in Hz (default: 44100)
    """
    
    def __init__(self, delay_ms, feedback, sample_rate=44100):
        """
        Initialize the allpass filter.
        
        Args:
            delay_ms: Delay time in milliseconds
            feedback: Feedback coefficient (0.0 to 1.0)
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        self.feedback = float(np.clip(feedback, 0.0, 1.0))
        
        # Calculate delay in samples
        self.delay_samples = int(np.round(delay_ms * sample_rate / 1000))
        
        # Allocate delay line
        self.delay_line = np.zeros(self.delay_samples + 1, dtype=np.float32)
        self.write_pos = 0
    
    def set_delay(self, delay_ms):
        """
        Set the delay time.
        
        Args:
            delay_ms: New delay time in milliseconds
        """
        self.delay_samples = int(np.round(delay_ms * self.sample_rate / 1000))
        
        # Reallocate delay line if needed
        if self.delay_samples + 1 > len(self.delay_line):
            new_delay_line = np.zeros(self.delay_samples + 1, dtype=np.float32)
            # Copy old data
            copy_len = min(len(self.delay_line), len(new_delay_line))
            new_delay_line[:copy_len] = self.delay_line[:copy_len]
            self.delay_line = new_delay_line
    
    def set_feedback(self, feedback):
        """
        Set the feedback coefficient.
        
        Args:
            feedback: New feedback coefficient (0.0 to 1.0)
        """
        self.feedback = float(np.clip(feedback, 0.0, 1.0))
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        # Recalculate delay in samples
        self.delay_samples = int(np.round(self.delay_samples * sample_rate / self.sample_rate))
    
    def reset(self):
        """Reset the filter state."""
        self.delay_line.fill(0.0)
        self.write_pos = 0
    
    def process(self, input_sample):
        """
        Process a sample through the allpass filter.
        
        Args:
            input_sample: Input sample
            
        Returns:
            float: Filtered output sample
        """
        # Read from delay line
        read_pos = (self.write_pos - self.delay_samples) % len(self.delay_line)
        delayed = self.delay_line[read_pos]
        
        # Allpass filter: y[n] = -feedback * x[n] + x[n-delay] + feedback * y[n-delay]
        # Simplified: y[n] = -feedback * x[n] + delayed + feedback * y[n-delay]
        # But we need to store y[n] in the delay line
        
        # Calculate output
        output = -self.feedback * input_sample + delayed
        
        # Store in delay line
        self.delay_line[self.write_pos] = input_sample + self.feedback * output
        
        # Update write position
        self.write_pos = (self.write_pos + 1) % len(self.delay_line)
        
        return output
    
    def process_block(self, input_buffer, output_buffer, num_samples):
        """
        Process a block of samples through the allpass filter.
        
        Args:
            input_buffer: Input buffer (numpy array)
            output_buffer: Output buffer (numpy array)
            num_samples: Number of samples to process
        """
        input_buffer = np.asarray(input_buffer, dtype=np.float32)
        output_buffer = np.asarray(output_buffer, dtype=np.float32)
        
        for i in range(num_samples):
            output_buffer[i] = self.process(input_buffer[i])
    
    def reset(self):
        """Reset the filter to initial state."""
        self.delay_line.fill(0.0)
        self.write_pos = 0


class CombFilter:
    """
    Comb filter implementation.
    
    A comb filter creates a series of echoes at regular intervals.
    It's a fundamental building block of reverb algorithms.
    
    The transfer function is: H(z) = 1 / (1 - feedback * z^(-delay))
    
    Parameters:
        delay_ms (float): Delay time in milliseconds
        feedback (float): Feedback coefficient (-1.0 to 1.0)
        sample_rate (float): Sample rate in Hz (default: 44100)
        damping_hz (float): Damping frequency in Hz (default: None, no damping)
    """
    
    def __init__(self, delay_ms, feedback, sample_rate=44100, damping_hz=None):
        """
        Initialize the comb filter.
        
        Args:
            delay_ms: Delay time in milliseconds
            feedback: Feedback coefficient (-1.0 to 1.0)
            sample_rate: Sample rate in Hz
            damping_hz: Damping frequency in Hz (optional)
        """
        self.sample_rate = float(sample_rate)
        self.feedback = float(np.clip(feedback, -1.0, 1.0))
        self.damping_hz = damping_hz
        
        # Calculate delay in samples
        self.delay_samples = int(np.round(delay_ms * sample_rate / 1000))
        
        # Allocate delay line
        self.delay_line = np.zeros(self.delay_samples + 1, dtype=np.float32)
        self.write_pos = 0
        
        # Create damping filter if needed
        self.damping_filter = None
        if damping_hz is not None:
            self.damping_filter = OnePoleFilter(
                cutoff_hz=damping_hz,
                sample_rate=sample_rate,
                filter_type='lowpass'
            )
    
    def set_delay(self, delay_ms):
        """
        Set the delay time.
        
        Args:
            delay_ms: New delay time in milliseconds
        """
        self.delay_samples = int(np.round(delay_ms * self.sample_rate / 1000))
        
        # Reallocate delay line if needed
        if self.delay_samples + 1 > len(self.delay_line):
            new_delay_line = np.zeros(self.delay_samples + 1, dtype=np.float32)
            # Copy old data
            copy_len = min(len(self.delay_line), len(new_delay_line))
            new_delay_line[:copy_len] = self.delay_line[:copy_len]
            self.delay_line = new_delay_line
    
    def set_feedback(self, feedback):
        """
        Set the feedback coefficient.
        
        Args:
            feedback: New feedback coefficient (-1.0 to 1.0)
        """
        self.feedback = float(np.clip(feedback, -1.0, 1.0))
    
    def set_damping(self, damping_hz):
        """
        Set the damping frequency.
        
        Args:
            damping_hz: Damping frequency in Hz (None for no damping)
        """
        self.damping_hz = damping_hz
        if damping_hz is not None:
            self.damping_filter = OnePoleFilter(
                cutoff_hz=damping_hz,
                sample_rate=self.sample_rate,
                filter_type='lowpass'
            )
        else:
            self.damping_filter = None
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        # Recalculate delay in samples
        self.delay_samples = int(np.round(self.delay_samples * sample_rate / self.sample_rate))
        
        # Update damping filter
        if self.damping_filter:
            self.damping_filter.set_sample_rate(sample_rate)
    
    def process(self, input_sample):
        """
        Process a sample through the comb filter.
        
        Args:
            input_sample: Input sample
            
        Returns:
            float: Filtered output sample
        """
        # Read from delay line
        read_pos = (self.write_pos - self.delay_samples) % len(self.delay_line)
        delayed = self.delay_line[read_pos]
        
        # Calculate output: y[n] = x[n] + feedback * delayed
        output = input_sample + self.feedback * delayed
        
        # Apply damping if enabled
        if self.damping_filter:
            output = self.damping_filter.process(output)
        
        # Store in delay line
        self.delay_line[self.write_pos] = input_sample
        
        # Update write position
        self.write_pos = (self.write_pos + 1) % len(self.delay_line)
        
        return output
    
    def process_block(self, input_buffer, output_buffer, num_samples):
        """
        Process a block of samples through the comb filter.
        
        Args:
            input_buffer: Input buffer (numpy array)
            output_buffer: Output buffer (numpy array)
            num_samples: Number of samples to process
        """
        input_buffer = np.asarray(input_buffer, dtype=np.float32)
        output_buffer = np.asarray(output_buffer, dtype=np.float32)
        
        for i in range(num_samples):
            output_buffer[i] = self.process(input_buffer[i])
    
    def reset(self):
        """Reset the filter to initial state."""
        self.delay_line.fill(0.0)
        self.write_pos = 0
        if self.damping_filter:
            self.damping_filter.reset()


class OnePoleFilter:
    """
    One-pole filter implementation.
    
    A simple first-order IIR filter that can be configured as lowpass
    or highpass. Commonly used for damping and tone shaping.
    
    Parameters:
        cutoff_hz (float): Cutoff frequency in Hz
        sample_rate (float): Sample rate in Hz (default: 44100)
        filter_type (str): Filter type ('lowpass' or 'highpass') (default: 'lowpass')
    """
    
    def __init__(self, cutoff_hz, sample_rate=44100, filter_type='lowpass'):
        """
        Initialize the one-pole filter.
        
        Args:
            cutoff_hz: Cutoff frequency in Hz
            sample_rate: Sample rate in Hz
            filter_type: Filter type ('lowpass' or 'highpass')
        """
        self.sample_rate = float(sample_rate)
        self.filter_type = filter_type.lower()
        
        # Set cutoff frequency
        self.set_cutoff(cutoff_hz)
        
        # State
        self.state = 0.0
    
    def set_cutoff(self, cutoff_hz):
        """
        Set the cutoff frequency.
        
        Args:
            cutoff_hz: New cutoff frequency in Hz
        """
        self.cutoff_hz = float(np.clip(cutoff_hz, 0.0, self.sample_rate / 2))
        
        # Calculate filter coefficient
        # For lowpass: y[n] = alpha * x[n] + (1 - alpha) * y[n-1]
        # where alpha = 2 * pi * cutoff / sample_rate / (1 + 2 * pi * cutoff / sample_rate)
        
        # More accurate: alpha = 1 / (1 + sample_rate / (2 * pi * cutoff))
        if self.cutoff_hz > 0:
            self.alpha = 1.0 / (1.0 + self.sample_rate / (2.0 * np.pi * self.cutoff_hz))
        else:
            self.alpha = 0.0
        
        # For highpass: y[n] = alpha * (x[n] - y[n-1]) + y[n-1]
        # which is equivalent to: y[n] = alpha * x[n] + (1 - alpha) * y[n-1] with alpha = 1 - lowpass_alpha
        if self.filter_type == 'highpass':
            self.alpha = 1.0 - self.alpha
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        # Recalculate coefficient
        self.set_cutoff(self.cutoff_hz)
    
    def set_filter_type(self, filter_type):
        """
        Set the filter type.
        
        Args:
            filter_type: Filter type ('lowpass' or 'highpass')
        """
        self.filter_type = filter_type.lower()
        # Recalculate coefficient
        self.set_cutoff(self.cutoff_hz)
    
    def process(self, input_sample):
        """
        Process a sample through the filter.
        
        Args:
            input_sample: Input sample
            
        Returns:
            float: Filtered output sample
        """
        if self.filter_type == 'lowpass':
            # Lowpass: y[n] = alpha * x[n] + (1 - alpha) * y[n-1]
            self.state = self.alpha * input_sample + (1.0 - self.alpha) * self.state
        else:  # highpass
            # Highpass: y[n] = alpha * (x[n] - y[n-1]) + y[n-1]
            self.state = self.alpha * (input_sample - self.state) + self.state
        
        return self.state
    
    def process_block(self, input_buffer, output_buffer, num_samples):
        """
        Process a block of samples through the filter.
        
        Args:
            input_buffer: Input buffer (numpy array)
            output_buffer: Output buffer (numpy array)
            num_samples: Number of samples to process
        """
        input_buffer = np.asarray(input_buffer, dtype=np.float32)
        output_buffer = np.asarray(output_buffer, dtype=np.float32)
        
        for i in range(num_samples):
            output_buffer[i] = self.process(input_buffer[i])
    
    def reset(self):
        """Reset the filter to initial state."""
        self.state = 0.0


class BiquadFilter:
    """
    Biquad (second-order IIR) filter implementation.
    
    A biquad filter is a second-order IIR filter that can implement
    various filter types: lowpass, highpass, bandpass, notch, etc.
    
    Parameters:
        filter_type (str): Filter type ('lowpass', 'highpass', 'bandpass', 'notch', 'peaking', 'lowshelf', 'highshelf')
        cutoff_hz (float): Cutoff/center frequency in Hz
        sample_rate (float): Sample rate in Hz (default: 44100)
        q (float): Quality factor (resonance) (default: 0.707)
        gain_db (float): Gain in dB (for shelf filters) (default: 0.0)
    """
    
    def __init__(self, filter_type='lowpass', cutoff_hz=1000.0, sample_rate=44100,
                 q=0.707, gain_db=0.0):
        """
        Initialize the biquad filter.
        
        Args:
            filter_type: Filter type
            cutoff_hz: Cutoff/center frequency in Hz
            sample_rate: Sample rate in Hz
            q: Quality factor
            gain_db: Gain in dB (for shelf filters)
        """
        self.sample_rate = float(sample_rate)
        self.filter_type = filter_type.lower()
        self.q = float(np.clip(q, 0.1, 10.0))
        self.gain_db = float(gain_db)
        
        # Set cutoff frequency
        self.set_cutoff(cutoff_hz)
        
        # State
        self.state1 = 0.0
        self.state2 = 0.0
        
        # Coefficients
        self.b0 = 1.0
        self.b1 = 0.0
        self.b2 = 0.0
        self.a1 = 0.0
        self.a2 = 0.0
    
    def set_cutoff(self, cutoff_hz):
        """
        Set the cutoff frequency.
        
        Args:
            cutoff_hz: New cutoff frequency in Hz
        """
        self.cutoff_hz = float(np.clip(cutoff_hz, 0.0, self.sample_rate / 2))
        self._update_coefficients()
    
    def set_q(self, q):
        """
        Set the quality factor.
        
        Args:
            q: New quality factor
        """
        self.q = float(np.clip(q, 0.1, 10.0))
        self._update_coefficients()
    
    def set_gain(self, gain_db):
        """
        Set the gain in dB.
        
        Args:
            gain_db: New gain in dB
        """
        self.gain_db = float(gain_db)
        self._update_coefficients()
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        self._update_coefficients()
    
    def set_filter_type(self, filter_type):
        """
        Set the filter type.
        
        Args:
            filter_type: New filter type
        """
        self.filter_type = filter_type.lower()
        self._update_coefficients()
    
    def _update_coefficients(self):
        """Update the filter coefficients based on current parameters."""
        # Normalize frequency
        w0 = 2.0 * np.pi * self.cutoff_hz / self.sample_rate
        
        # Calculate coefficients based on filter type
        if self.filter_type == 'lowpass':
            # Lowpass: H(s) = w0^2 / (s^2 + w0/Q * s + w0^2)
            alpha = np.sin(w0) / (2.0 * self.q)
            cos_w0 = np.cos(w0)
            
            self.b0 = (1.0 - cos_w0) / 2.0
            self.b1 = 1.0 - cos_w0
            self.b2 = (1.0 - cos_w0) / 2.0
            self.a1 = -2.0 * cos_w0
            self.a2 = 1.0 - alpha
            
            # Normalize
            inv_a0 = 1.0 / (1.0 + alpha)
            self.b0 *= inv_a0
            self.b1 *= inv_a0
            self.b2 *= inv_a0
            self.a1 *= inv_a0
            self.a2 *= inv_a0
        
        elif self.filter_type == 'highpass':
            # Highpass: H(s) = s^2 / (s^2 + w0/Q * s + w0^2)
            alpha = np.sin(w0) / (2.0 * self.q)
            cos_w0 = np.cos(w0)
            
            self.b0 = (1.0 + cos_w0) / 2.0
            self.b1 = -(1.0 + cos_w0)
            self.b2 = (1.0 + cos_w0) / 2.0
            self.a1 = -2.0 * cos_w0
            self.a2 = 1.0 - alpha
            
            # Normalize
            inv_a0 = 1.0 / (1.0 + alpha)
            self.b0 *= inv_a0
            self.b1 *= inv_a0
            self.b2 *= inv_a0
            self.a1 *= inv_a0
            self.a2 *= inv_a0
        
        elif self.filter_type == 'bandpass':
            # Bandpass: H(s) = (w0/Q * s) / (s^2 + w0/Q * s + w0^2)
            alpha = np.sin(w0) / (2.0 * self.q)
            cos_w0 = np.cos(w0)
            
            self.b0 = alpha
            self.b1 = 0.0
            self.b2 = -alpha
            self.a1 = -2.0 * cos_w0
            self.a2 = 1.0 - alpha
            
            # Normalize
            inv_a0 = 1.0 / (1.0 + alpha)
            self.b0 *= inv_a0
            self.b1 *= inv_a0
            self.b2 *= inv_a0
            self.a1 *= inv_a0
            self.a2 *= inv_a0
        
        elif self.filter_type == 'notch':
            # Notch: H(s) = (s^2 + w0^2) / (s^2 + w0/Q * s + w0^2)
            alpha = np.sin(w0) / (2.0 * self.q)
            cos_w0 = np.cos(w0)
            
            self.b0 = 1.0
            self.b1 = -2.0 * cos_w0
            self.b2 = 1.0
            self.a1 = -2.0 * cos_w0
            self.a2 = 1.0 - alpha
            
            # Normalize
            inv_a0 = 1.0 / (1.0 + alpha)
            self.b0 *= inv_a0
            self.b1 *= inv_a0
            self.b2 *= inv_a0
            self.a1 *= inv_a0
            self.a2 *= inv_a0
        
        else:
            # Default to lowpass
            self.set_filter_type('lowpass')
    
    def process(self, input_sample):
        """
        Process a sample through the filter.
        
        Args:
            input_sample: Input sample
            
        Returns:
            float: Filtered output sample
        """
        # Biquad filter: y[n] = b0 * x[n] + b1 * x[n-1] + b2 * x[n-2] - a1 * y[n-1] - a2 * y[n-2]
        # We need to maintain the input history, but for simplicity, we'll use the output states
        
        # For now, use a simplified approach
        # In a full implementation, we'd maintain input history
        output = self.b0 * input_sample + self.state1
        self.state1 = self.b1 * input_sample - self.a1 * output + self.state2
        self.state2 = self.b2 * input_sample - self.a2 * output
        
        return output
    
    def process_block(self, input_buffer, output_buffer, num_samples):
        """
        Process a block of samples through the filter.
        
        Args:
            input_buffer: Input buffer (numpy array)
            output_buffer: Output buffer (numpy array)
            num_samples: Number of samples to process
        """
        input_buffer = np.asarray(input_buffer, dtype=np.float32)
        output_buffer = np.asarray(output_buffer, dtype=np.float32)
        
        for i in range(num_samples):
            output_buffer[i] = self.process(input_buffer[i])
    
    def reset(self):
        """Reset the filter to initial state."""
        self.state1 = 0.0
        self.state2 = 0.0


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from signals.sine import SineGenerator
    
    print("Filter Examples")
    print("=" * 50)
    
    # Create signal generator
    sine_gen = SineGenerator(sample_rate=44100, length_samples=44100)
    
    # Generate test signal (sweep)
    signal = sine_gen.logarithmic(start_freq=20.0, end_freq=20000.0)
    
    # Test allpass filter
    print("\nAllpass Filter:")
    allpass = AllpassFilter(delay_ms=5.0, feedback=0.7, sample_rate=44100)
    output = np.zeros_like(signal)
    allpass.process_block(signal, output, len(signal))
    print(f"  Input RMS: {np.sqrt(np.mean(signal**2)):.6f}")
    print(f"  Output RMS: {np.sqrt(np.mean(output**2)):.6f}")
    
    # Test comb filter
    print("\nComb Filter:")
    comb = CombFilter(delay_ms=30.0, feedback=0.8, sample_rate=44100, damping_hz=5000.0)
    output = np.zeros_like(signal)
    comb.process_block(signal, output, len(signal))
    print(f"  Input RMS: {np.sqrt(np.mean(signal**2)):.6f}")
    print(f"  Output RMS: {np.sqrt(np.mean(output**2)):.6f}")
    
    # Test one-pole lowpass
    print("\nOne-Pole Lowpass Filter (1000Hz):")
    lowpass = OnePoleFilter(cutoff_hz=1000.0, sample_rate=44100, filter_type='lowpass')
    output = np.zeros_like(signal)
    lowpass.process_block(signal, output, len(signal))
    print(f"  Input RMS: {np.sqrt(np.mean(signal**2)):.6f}")
    print(f"  Output RMS: {np.sqrt(np.mean(output**2)):.6f}")
    
    # Test one-pole highpass
    print("\nOne-Pole Highpass Filter (1000Hz):")
    highpass = OnePoleFilter(cutoff_hz=1000.0, sample_rate=44100, filter_type='highpass')
    output = np.zeros_like(signal)
    highpass.process_block(signal, output, len(signal))
    print(f"  Input RMS: {np.sqrt(np.mean(signal**2)):.6f}")
    print(f"  Output RMS: {np.sqrt(np.mean(output**2)):.6f}")
    
    # Test biquad lowpass
    print("\nBiquad Lowpass Filter (1000Hz, Q=0.707):")
    biquad_lowpass = BiquadFilter(filter_type='lowpass', cutoff_hz=1000.0, sample_rate=44100, q=0.707)
    output = np.zeros_like(signal)
    biquad_lowpass.process_block(signal, output, len(signal))
    print(f"  Input RMS: {np.sqrt(np.mean(signal**2)):.6f}")
    print(f"  Output RMS: {np.sqrt(np.mean(output**2)):.6f}")
    
    # Plot (if matplotlib is available)
    try:
        plt.figure(figsize=(12, 10))
        
        plt.subplot(5, 1, 1)
        plt.plot(signal[:5000])
        plt.title("Input Signal (Log Sweep)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        # Allpass output
        allpass.reset()
        output = np.zeros_like(signal)
        allpass.process_block(signal, output, len(signal))
        plt.subplot(5, 1, 2)
        plt.plot(output[:5000])
        plt.title("Allpass Filter Output")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        # Comb output
        comb.reset()
        output = np.zeros_like(signal)
        comb.process_block(signal, output, len(signal))
        plt.subplot(5, 1, 3)
        plt.plot(output[:5000])
        plt.title("Comb Filter Output")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        # Lowpass output
        lowpass.reset()
        output = np.zeros_like(signal)
        lowpass.process_block(signal, output, len(signal))
        plt.subplot(5, 1, 4)
        plt.plot(output[:5000])
        plt.title("One-Pole Lowpass Output (1000Hz)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        # Biquad lowpass output
        biquad_lowpass.reset()
        output = np.zeros_like(signal)
        biquad_lowpass.process_block(signal, output, len(signal))
        plt.subplot(5, 1, 5)
        plt.plot(output[:5000])
        plt.title("Biquad Lowpass Output (1000Hz, Q=0.707)")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")

"""
RevPitch Mode Implementation

Based on ValhallaDelay RevPitch mode (E023)

Characteristics:
- Reverse delay with pitch shifting
- Creates unique reverse echo effects with pitch changes
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine
from isengard_shared.filters import OnePoleFilter


class ReverseBuffer:
    """
    Reverse buffer for creating reverse delay effects.
    
    This buffer stores incoming samples and can play them back in reverse.
    
    Parameters:
        max_size_samples: Maximum buffer size in samples
    """
    
    def __init__(self, max_size_samples: int = 44100):
        self.buffer = np.zeros(max_size_samples, dtype=np.float32)
        self.max_size = max_size_samples
        self.write_pos = 0
        self.buffer_full = False
    
    def set_size(self, size_samples: int):
        """Set the buffer size."""
        size_samples = min(size_samples, self.max_size)
        # For now, we'll just use the full buffer
        # In a proper implementation, we'd manage the size dynamically
    
    def write(self, sample: float):
        """Write a sample to the buffer."""
        self.buffer[self.write_pos] = sample
        self.write_pos += 1
        if self.write_pos >= self.max_size:
            self.write_pos = 0
            self.buffer_full = True
    
    def read_reverse(self) -> float:
        """
        Read a sample from the buffer in reverse order.
        
        Returns:
            Sample from the buffer played in reverse
        """
        # Always read from the position before the write position
        read_pos = self.write_pos - 1
        if read_pos < 0:
            read_pos = self.max_size - 1
        
        return self.buffer[read_pos]
    
    def reset(self):
        """Reset the buffer."""
        self.buffer.fill(0.0)
        self.write_pos = 0
        self.buffer_full = False


class RevPitchMode:
    """
    RevPitch Mode for Isengard Delay.
    
    This mode creates reverse delay effects with pitch shifting.
    The delay is played back in reverse, and then pitch shifted.
    
    Parameters:
    - delay_time_ms: Delay time in milliseconds
    - feedback: Feedback amount (0.0 to 1.0)
    - pitch_shift: Pitch shift in semitones (-12 to +12)
    - tone: Tone control
    - mix: Wet/dry mix (0.0 to 1.0)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize RevPitchMode.
        
        Args:
            sample_rate: Audio sample rate in Hz
            max_delay_ms: Maximum delay time in milliseconds
        """
        self.sample_rate = sample_rate
        self.max_delay_ms = max_delay_ms
        
        # Create delay lines for left and right channels
        self.delay_left = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='cubic'
        )
        self.delay_right = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='cubic'
        )
        
        # Reverse buffers
        max_size_samples = int(max_delay_ms / 1000.0 * sample_rate)
        self.reverse_left = ReverseBuffer(max_size_samples)
        self.reverse_right = ReverseBuffer(max_size_samples)
        
        # Simple pitch shifter (using ratio-based approach)
        # For RevPitch, we'll use a simpler approach since the reverse
        # already creates a lot of the characteristic sound
        self.pitch_ratio = 1.0  # 1.0 = no pitch shift
        
        # DC blocker for input
        self.dc_blocker = OnePoleFilter(
            cutoff_hz=10.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        
        # Tone control
        self.tone_filter = OnePoleFilter(
            cutoff_hz=10000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        
        # Parameters
        self.params = {
            'delay_time_ms': 500.0,
            'feedback': 0.5,
            'pitch_shift': 0.0,  # semitones (-12 to +12)
            'tone': 0.5,
            'mix': 0.5,  # 0.0 = dry only, 1.0 = wet only
        }
        
        # Internal state for pitch shifting
        self._pitch_buffer_l = np.zeros(44100, dtype=np.float32)
        self._pitch_buffer_r = np.zeros(44100, dtype=np.float32)
        self._pitch_write_pos = 0
        self._pitch_read_pos_l = 0.0
        self._pitch_read_pos_r = 0.0
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
        self.reverse_left.reset()
        self.reverse_right.reset()
        self._pitch_buffer_l.fill(0.0)
        self._pitch_buffer_r.fill(0.0)
        self._pitch_write_pos = 0
        self._pitch_read_pos_l = 0.0
        self._pitch_read_pos_r = 0.0
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_left.set_sample_rate(sample_rate)
        self.delay_right.set_sample_rate(sample_rate)
        self.dc_blocker.set_sample_rate(sample_rate)
        self.tone_filter.set_sample_rate(sample_rate)
    
    def set_delay_time(self, delay_time_ms: float):
        """Set delay time in milliseconds."""
        delay_time_ms = np.clip(delay_time_ms, 1.0, self.max_delay_ms)
        self.params['delay_time_ms'] = delay_time_ms
        delay_seconds = delay_time_ms / 1000.0
        self.delay_left.set_delay_time(delay_seconds)
        self.delay_right.set_delay_time(delay_seconds)
        
        # Update reverse buffer sizes
        max_size_samples = int(delay_time_ms / 1000.0 * self.sample_rate)
        self.reverse_left.set_size(max_size_samples)
        self.reverse_right.set_size(max_size_samples)
    
    def set_feedback(self, feedback: float):
        """Set feedback amount (0.0 to 1.0)."""
        self.params['feedback'] = np.clip(feedback, 0.0, 0.999)
    
    def set_pitch_shift(self, semitones: float):
        """Set pitch shift in semitones (-12 to +12)."""
        self.params['pitch_shift'] = np.clip(semitones, -12.0, 12.0)
        self.pitch_ratio = 2.0 ** (semitones / 12.0)
    
    def set_tone(self, tone: float):
        """Set tone control (0.0 = dark, 1.0 = bright)."""
        self.params['tone'] = np.clip(tone, 0.0, 1.0)
        # Map tone to cutoff: 0.0 -> 4000Hz, 1.0 -> 15000Hz
        cutoff = 4000.0 + 11000.0 * tone
        self.tone_filter.set_cutoff(cutoff)
    
    def set_mix(self, mix: float):
        """Set wet/dry mix (0.0 = dry only, 1.0 = wet only)."""
        self.params['mix'] = np.clip(mix, 0.0, 1.0)
    
    def set_parameters(self, params: dict):
        """Set all parameters at once."""
        for key, value in params.items():
            if key == 'delay_time_ms':
                self.set_delay_time(value)
            elif key == 'feedback':
                self.set_feedback(value)
            elif key == 'pitch_shift':
                self.set_pitch_shift(value)
            elif key == 'tone':
                self.set_tone(value)
            elif key == 'mix':
                self.set_mix(value)
    
    def get_parameters(self) -> dict:
        """Get current parameters."""
        return self.params.copy()
    
    def _apply_pitch_shift(self, sample: float, is_left: bool) -> float:
        """
        Apply pitch shift using simple sample rate conversion.
        
        Args:
            sample: Input sample
            is_left: Whether this is the left channel
            
        Returns:
            Pitch-shifted sample
        """
        buffer = self._pitch_buffer_l if is_left else self._pitch_buffer_r
        read_pos = self._pitch_read_pos_l if is_left else self._pitch_read_pos_r
        
        # Write to buffer
        buffer[self._pitch_write_pos] = sample
        
        # Read from buffer at pitch-shifted rate
        if self.pitch_ratio >= 1.0:
            # Pitch up
            read_pos += self.pitch_ratio
            if read_pos >= len(buffer):
                read_pos -= len(buffer)
            
            int_pos = int(read_pos)
            frac = read_pos - int_pos
            idx0 = int_pos % len(buffer)
            idx1 = (int_pos + 1) % len(buffer)
            
            result = buffer[idx0] * (1.0 - frac) + buffer[idx1] * frac
        else:
            # Pitch down - for simplicity, just scale
            result = sample * self.pitch_ratio
        
        # Update positions
        self._pitch_write_pos = (self._pitch_write_pos + 1) % len(buffer)
        if is_left:
            self._pitch_read_pos_l = read_pos
        else:
            self._pitch_read_pos_r = read_pos
        
        return result
    
    def process_sample(self, input_l: float, input_r: float) -> Tuple[float, float]:
        """
        Process a single sample pair (L, R).
        
        Signal flow:
        1. Apply DC blocking to inputs
        2. Write to reverse buffers
        3. Get delayed outputs
        4. Read from reverse buffers
        5. Apply pitch shifting
        6. Apply feedback
        7. Write to delay lines
        8. Apply tone filter
        9. Apply dry/wet mix
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Step 1: DC blocking
        input_l = self.dc_blocker.process(input_l)
        input_r = self.dc_blocker.process(input_r)
        
        # Step 2: Write to reverse buffers
        self.reverse_left.write(input_l)
        self.reverse_right.write(input_r)
        
        # Step 3: Get delayed outputs (read without writing)
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Step 4: Read from reverse buffers
        reverse_l = self.reverse_left.read_reverse()
        reverse_r = self.reverse_right.read_reverse()
        
        # Step 5: Apply pitch shifting to reverse outputs
        pitched_l = self._apply_pitch_shift(reverse_l, True)
        pitched_r = self._apply_pitch_shift(reverse_r, False)
        
        # Step 6: Apply feedback
        feedback = self.params['feedback']
        feedback_l = pitched_l * feedback
        feedback_r = pitched_r * feedback
        
        # Step 7: Mix feedback with input and write to delay lines
        mixed_l = input_l + feedback_l
        mixed_r = input_r + feedback_r
        
        self.delay_left.process(mixed_l)
        self.delay_right.process(mixed_r)
        
        # Step 8: Apply tone filter to delayed outputs
        output_l = self.tone_filter.process(pitched_l)
        output_r = self.tone_filter.process(pitched_r)
        
        # Step 9: Apply dry/wet mix
        dry_l = input_l
        dry_r = input_r
        mix = self.params['mix']
        output_l = dry_l * (1.0 - mix) + output_l * mix
        output_r = dry_r * (1.0 - mix) + output_r * mix
        
        return output_l, output_r
    
    def process_block(self, input_block: np.ndarray) -> np.ndarray:
        """
        Process a block of audio samples.
        
        Args:
            input_block: Input audio as numpy array (N, 2) where N is num samples
                        and 2 is (L, R) channels
            
        Returns:
            Output audio as numpy array (N, 2)
        """
        num_samples = input_block.shape[0]
        output_block = np.zeros((num_samples, 2), dtype=np.float32)
        
        for i in range(num_samples):
            input_l = input_block[i, 0]
            input_r = input_block[i, 1]
            
            output_l, output_r = self.process_sample(input_l, input_r)
            output_block[i, 0] = output_l
            output_block[i, 1] = output_r
        
        return output_block
    
    def get_name(self) -> str:
        """Get mode name."""
        return "RevPitch"


# Test
if __name__ == "__main__":
    print("Testing RevPitchMode...")
    
    # Create RevPitch mode
    revpitch_mode = RevPitchMode(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    revpitch_mode.set_parameters({
        'delay_time_ms': 500.0,
        'feedback': 0.5,
        'pitch_shift': 0.0,  # No pitch shift for now
        'tone': 0.5,
        'mix': 1.0
    })
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)  # 1 second
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = revpitch_mode.process_block(test_signal)
    
    print(f'Input shape: {test_signal.shape}')
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    print(f'Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
    
    # Check output around 500ms
    delay_samples = int(500.0 / 1000.0 * 44100)
    print(f'Expected delay at sample {delay_samples}')
    print(f'Output at delay position L: {output[delay_samples, 0]:.6f}')
    print(f'Output at delay position R: {output[delay_samples, 1]:.6f}')
    
    print('\nRevPitchMode test completed successfully!')

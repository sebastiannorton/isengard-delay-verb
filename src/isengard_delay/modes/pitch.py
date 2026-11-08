"""
Pitch Mode Implementation

Based on ValhallaDelay Pitch mode (E022)

Characteristics:
- Pitch shifting in feedback path
- Independent pitch shift and detune controls
- Creates harmonized delay effects
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine
from isengard_shared.filters import OnePoleFilter


class PitchShifter:
    """
    Simple pitch shifter using phase vocoder-like approach.
    
    This is a simplified pitch shifter that uses sample rate conversion
    via linear interpolation. For a production-quality pitch shifter,
    you would use a proper phase vocoder or time-domain approach.
    
    Parameters:
        shift_semitones: Pitch shift in semitones
        sample_rate: Audio sample rate
    """
    
    def __init__(self, shift_semitones: float = 0.0, sample_rate: int = 44100):
        self.shift_semitones = shift_semitones
        self.sample_rate = sample_rate
        
        # Calculate pitch shift ratio
        # ratio = 2^(semitones / 12)
        self.ratio = 2.0 ** (shift_semitones / 12.0)
        
        # Internal buffer for pitch shifting
        self.buffer = np.zeros(44100, dtype=np.float32)  # 1 second buffer
        self.buffer_size = len(self.buffer)
        self.write_pos = 0
        self.read_pos = 0.0
    
    def set_shift(self, semitones: float):
        """Set pitch shift in semitones."""
        self.shift_semitones = semitones
        self.ratio = 2.0 ** (semitones / 12.0)
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
    
    def process(self, x: float) -> float:
        """
        Process a sample through the pitch shifter.
        
        Uses simple sample rate conversion via linear interpolation.
        
        Args:
            x: Input sample
            
        Returns:
            Pitch-shifted sample
        """
        # Write to buffer
        self.buffer[self.write_pos] = x
        self.write_pos = (self.write_pos + 1) % self.buffer_size
        
        # Read from buffer at different rate
        # For pitch up (ratio > 1), we read faster
        # For pitch down (ratio < 1), we read slower
        
        # Calculate output
        if self.ratio >= 1.0:
            # Pitch up: read faster, may need to interpolate
            self.read_pos += self.ratio
            if self.read_pos >= self.buffer_size:
                self.read_pos -= self.buffer_size
            
            # Linear interpolation
            int_pos = int(self.read_pos)
            frac = self.read_pos - int_pos
            
            idx0 = int_pos % self.buffer_size
            idx1 = (int_pos + 1) % self.buffer_size
            
            return self.buffer[idx0] * (1.0 - frac) + self.buffer[idx1] * frac
        else:
            # Pitch down: read slower, may need to duplicate
            # For simplicity, just return the input (this is a placeholder)
            # A proper implementation would use a different approach
            return x * self.ratio
    
    def reset(self):
        """Reset the pitch shifter."""
        self.buffer.fill(0.0)
        self.write_pos = 0
        self.read_pos = 0.0


class PitchMode:
    """
    Pitch Mode for Isengard Delay.
    
    This mode applies pitch shifting to the feedback path, creating
    harmonized delay effects.
    
    Parameters:
    - delay_time_ms: Delay time in milliseconds
    - feedback: Feedback amount (0.0 to 1.0)
    - pitch_shift: Pitch shift in semitones (-12 to +12)
    - pitch_detune: Pitch detune in cents (-100 to +100)
    - tone: Tone control
    - mix: Wet/dry mix (0.0 to 1.0)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize PitchMode.
        
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
        
        # Pitch shifter for feedback path
        self.pitch_shifter_l = PitchShifter(
            shift_semitones=0.0,
            sample_rate=sample_rate
        )
        self.pitch_shifter_r = PitchShifter(
            shift_semitones=0.0,
            sample_rate=sample_rate
        )
        
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
            'pitch_detune': 0.0,  # cents (-100 to +100)
            'tone': 0.5,
            'mix': 0.5,  # 0.0 = dry only, 1.0 = wet only
        }
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
        self.pitch_shifter_l.reset()
        self.pitch_shifter_r.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_left.set_sample_rate(sample_rate)
        self.delay_right.set_sample_rate(sample_rate)
        self.pitch_shifter_l.set_sample_rate(sample_rate)
        self.pitch_shifter_r.set_sample_rate(sample_rate)
        self.dc_blocker.set_sample_rate(sample_rate)
        self.tone_filter.set_sample_rate(sample_rate)
    
    def set_delay_time(self, delay_time_ms: float):
        """Set delay time in milliseconds."""
        delay_time_ms = np.clip(delay_time_ms, 1.0, self.max_delay_ms)
        self.params['delay_time_ms'] = delay_time_ms
        delay_seconds = delay_time_ms / 1000.0
        self.delay_left.set_delay_time(delay_seconds)
        self.delay_right.set_delay_time(delay_seconds)
    
    def set_feedback(self, feedback: float):
        """Set feedback amount (0.0 to 1.0)."""
        self.params['feedback'] = np.clip(feedback, 0.0, 0.999)
    
    def set_pitch_shift(self, semitones: float):
        """Set pitch shift in semitones (-12 to +12)."""
        self.params['pitch_shift'] = np.clip(semitones, -12.0, 12.0)
        
        # Apply to both pitch shifters
        # Left channel: pitch shift
        self.pitch_shifter_l.set_shift(semitones)
        
        # Right channel: pitch shift + detune
        detune_semitones = self.params.get('pitch_detune', 0.0) / 100.0
        self.pitch_shifter_r.set_shift(semitones + detune_semitones)
    
    def set_pitch_detune(self, cents: float):
        """Set pitch detune in cents (-100 to +100)."""
        self.params['pitch_detune'] = np.clip(cents, -100.0, 100.0)
        
        # Update right channel pitch shifter
        shift_semitones = self.params.get('pitch_shift', 0.0)
        detune_semitones = cents / 100.0
        self.pitch_shifter_r.set_shift(shift_semitones + detune_semitones)
    
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
            elif key == 'pitch_detune':
                self.set_pitch_detune(value)
            elif key == 'tone':
                self.set_tone(value)
            elif key == 'mix':
                self.set_mix(value)
    
    def get_parameters(self) -> dict:
        """Get current parameters."""
        return self.params.copy()
    
    def process_sample(self, input_l: float, input_r: float) -> Tuple[float, float]:
        """
        Process a single sample pair (L, R).
        
        Signal flow:
        1. Apply DC blocking to inputs
        2. Get delayed outputs
        3. Apply pitch shifting to feedback path
        4. Apply feedback
        5. Write to delay lines
        6. Apply tone filter
        7. Apply dry/wet mix
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Step 1: DC blocking
        input_l = self.dc_blocker.process(input_l)
        input_r = self.dc_blocker.process(input_r)
        
        # Step 2: Get delayed outputs (read without writing)
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Step 3: Apply pitch shifting to feedback path
        shifted_l = self.pitch_shifter_l.process(delayed_l)
        shifted_r = self.pitch_shifter_r.process(delayed_r)
        
        # Step 4: Apply feedback
        feedback = self.params['feedback']
        feedback_l = shifted_l * feedback
        feedback_r = shifted_r * feedback
        
        # Step 5: Mix feedback with input and write to delay lines
        mixed_l = input_l + feedback_l
        mixed_r = input_r + feedback_r
        
        self.delay_left.process(mixed_l)
        self.delay_right.process(mixed_r)
        
        # Step 6: Apply tone filter to delayed outputs
        output_l = self.tone_filter.process(delayed_l)
        output_r = self.tone_filter.process(delayed_r)
        
        # Step 7: Apply dry/wet mix
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
        return "Pitch"


# Test
if __name__ == "__main__":
    print("Testing PitchMode...")
    
    # Create Pitch mode
    pitch_mode = PitchMode(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    pitch_mode.set_parameters({
        'delay_time_ms': 500.0,
        'feedback': 0.5,
        'pitch_shift': 7.0,  # +7 semitones (perfect fifth)
        'pitch_detune': 0.0,
        'tone': 0.5,
        'mix': 1.0
    })
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)  # 1 second
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = pitch_mode.process_block(test_signal)
    
    print(f'Input shape: {test_signal.shape}')
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    print(f'Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
    
    # Check that delay appears at ~500ms
    delay_samples = int(500.0 / 1000.0 * 44100)
    print(f'Expected delay at sample {delay_samples}')
    print(f'Output at delay position L: {output[delay_samples, 0]:.6f}')
    print(f'Output at delay position R: {output[delay_samples, 1]:.6f}')
    
    print('\nPitchMode test completed successfully!')

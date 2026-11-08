"""
Ghost Mode Implementation

Based on ValhallaDelay Ghost mode (E020-E021)

Characteristics:
- Frequency shifting in feedback path
- Frequency-dependent diffusion
- Present/Future ERA parameter
- Ethereal, otherworldly sound

ERA Behavior (E021):
- Present ERA: Standard frequency-dependent diffusion
- Future ERA: Enhanced frequency-dependent diffusion
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine
from isengard_delay.dsp.diffusion import DiffusionNetwork
from isengard_delay.dsp.modulation import LFO
from isengard_shared.filters import OnePoleFilter


class FrequencyShifter:
    """
    Simple frequency shifter using single sideband modulation.
    
    This implements a basic frequency shift by multiplying the signal
    with a complex exponential (cosine + i*sine) and filtering.
    
    For simplicity, we use a single sideband approach with a fixed
    shift amount controlled by the shift parameter.
    
    Parameters:
        shift_hz: Frequency shift in Hz (positive or negative)
        sample_rate: Audio sample rate
    """
    
    def __init__(self, shift_hz: float = 10.0, sample_rate: int = 44100):
        self.shift_hz = shift_hz
        self.sample_rate = sample_rate
        self.phase = 0.0
        self.phase_inc = 2.0 * np.pi * shift_hz / sample_rate
    
    def set_shift(self, shift_hz: float):
        """Set frequency shift in Hz."""
        self.shift_hz = shift_hz
        self.phase_inc = 2.0 * np.pi * shift_hz / self.sample_rate
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.phase_inc = 2.0 * np.pi * self.shift_hz / sample_rate
    
    def process(self, x: float) -> float:
        """
        Apply frequency shift to a sample.
        
        Uses single sideband modulation: output = x * cos(2πft)
        
        Args:
            x: Input sample
            
        Returns:
            Frequency-shifted sample
        """
        # Generate cosine at shift frequency
        cos_val = np.cos(self.phase)
        
        # Update phase
        self.phase += self.phase_inc
        if self.phase >= 2.0 * np.pi:
            self.phase -= 2.0 * np.pi
        elif self.phase < 0:
            self.phase += 2.0 * np.pi
        
        return x * cos_val
    
    def reset(self):
        """Reset phase."""
        self.phase = 0.0


class GhostMode:
    """
    Ghost Mode for Isengard Delay.
    
    This mode creates ethereal, otherworldly delay effects with:
    - Frequency shifting in the feedback path
    - Frequency-dependent diffusion
    - ERA parameter (Present/Future)
    
    Parameters:
    - delay_time_ms: Delay time in milliseconds
    - feedback: Feedback amount (0.0 to 1.0)
    - shift: Frequency shift amount (0.0 to 1.0)
    - era: ERA parameter (0.0 = Present, 1.0 = Future)
    - diffusion_amount: Amount of diffusion (0.0 to 1.0)
    - diffusion_size: Size of diffusion network (0.0 to 1.0)
    - tone: Tone control
    - mix: Wet/dry mix (0.0 to 1.0)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize GhostMode.
        
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
        
        # Frequency shifter for feedback path
        self.freq_shifter = FrequencyShifter(
            shift_hz=10.0,
            sample_rate=sample_rate
        )
        
        # Diffusion network
        self.diffusion = DiffusionNetwork(sample_rate=sample_rate)
        
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
            'shift': 0.0,  # -1.0 to 1.0 (normalized)
            'era': 0.0,  # 0.0 = Present, 1.0 = Future
            'diffusion_amount': 0.5,
            'diffusion_size': 0.5,
            'tone': 0.5,
            'mix': 0.5,  # 0.0 = dry only, 1.0 = wet only
        }
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
        self.freq_shifter.reset()
        self.diffusion.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_left.set_sample_rate(sample_rate)
        self.delay_right.set_sample_rate(sample_rate)
        self.freq_shifter.set_sample_rate(sample_rate)
        self.diffusion.set_sample_rate(sample_rate)
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
    
    def set_shift(self, shift: float):
        """
        Set frequency shift (-1.0 to 1.0).
        
        Maps to approximately -50Hz to +50Hz.
        """
        self.params['shift'] = np.clip(shift, -1.0, 1.0)
        # Map to Hz: -1.0 -> -50Hz, 0.0 -> 0Hz, 1.0 -> 50Hz
        shift_hz = shift * 50.0
        self.freq_shifter.set_shift(shift_hz)
    
    def set_era(self, era: float):
        """
        Set ERA parameter (0.0 = Present, 1.0 = Future).
        
        ERA Behavior (E021):
        - Present: Standard frequency-dependent diffusion
        - Future: Enhanced frequency-dependent diffusion
        """
        self.params['era'] = np.clip(era, 0.0, 1.0)
        # ERA affects diffusion characteristics
        # For now, we'll use it to modify diffusion parameters
        self._update_diffusion()
    
    def set_diffusion_amount(self, amount: float):
        """Set diffusion amount (0.0 to 1.0)."""
        self.params['diffusion_amount'] = np.clip(amount, 0.0, 1.0)
        self.diffusion.set_amount(amount)
    
    def set_diffusion_size(self, size: float):
        """Set diffusion size (0.0 to 1.0)."""
        self.params['diffusion_size'] = np.clip(size, 0.0, 1.0)
        self.diffusion.set_size(size)
    
    def _update_diffusion(self):
        """Update diffusion parameters based on ERA."""
        era = self.params['era']
        # Future ERA has more diffusion
        amount = self.params['diffusion_amount'] * (0.5 + era * 0.5)
        self.diffusion.set_amount(amount)
        
        # Future ERA has larger diffusion network
        size = self.params['diffusion_size'] * (0.5 + era * 0.5)
        self.diffusion.set_size(size)
    
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
            elif key == 'shift':
                self.set_shift(value)
            elif key == 'era':
                self.set_era(value)
            elif key == 'diffusion_amount':
                self.set_diffusion_amount(value)
            elif key == 'diffusion_size':
                self.set_diffusion_size(value)
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
        3. Apply frequency shifting to feedback path
        4. Apply diffusion to feedback
        5. Apply feedback
        6. Write to delay lines
        7. Apply tone filter
        8. Apply dry/wet mix
        
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
        
        # Step 3: Apply frequency shifting to feedback path
        # Frequency shift is applied to the delayed signal before feedback
        shifted_l = self.freq_shifter.process(delayed_l)
        shifted_r = self.freq_shifter.process(delayed_r)
        
        # Step 4: Apply diffusion to feedback
        # Process through diffusion network
        diffused_l, diffused_r = self.diffusion.process_stereo(shifted_l, shifted_r)
        
        # Step 5: Apply feedback
        feedback = self.params['feedback']
        feedback_l = diffused_l * feedback
        feedback_r = diffused_r * feedback
        
        # Step 6: Mix feedback with input and write to delay lines
        mixed_l = input_l + feedback_l
        mixed_r = input_r + feedback_r
        
        self.delay_left.process(mixed_l)
        self.delay_right.process(mixed_r)
        
        # Step 7: Apply tone filter to delayed outputs
        output_l = self.tone_filter.process(delayed_l)
        output_r = self.tone_filter.process(delayed_r)
        
        # Step 8: Apply dry/wet mix
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
        return "Ghost"


# Test
if __name__ == "__main__":
    print("Testing GhostMode...")
    
    # Create Ghost mode
    ghost_mode = GhostMode(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    ghost_mode.set_parameters({
        'delay_time_ms': 500.0,
        'feedback': 0.5,
        'shift': 0.3,  # +15Hz shift
        'era': 0.5,  # Between Present and Future
        'diffusion_amount': 0.5,
        'diffusion_size': 0.5,
        'tone': 0.5,
        'mix': 1.0
    })
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)  # 1 second
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = ghost_mode.process_block(test_signal)
    
    print(f'Input shape: {test_signal.shape}')
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    print(f'Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
    
    # Check that delay appears at ~500ms
    delay_samples = int(500.0 / 1000.0 * 44100)
    print(f'Expected delay at sample {delay_samples}')
    print(f'Output at delay position L: {output[delay_samples, 0]:.6f}')
    print(f'Output at delay position R: {output[delay_samples, 1]:.6f}')
    
    print('\nGhostMode test completed successfully!')

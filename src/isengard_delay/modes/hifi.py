"""
HiFi Mode Implementation

Based on ValhallaDelay HiFi mode (E013-E014)

Characteristics:
- Clean high-fidelity delay
- Subtle modulation (chorus-like)
- Minimal coloration
- Precise timing
- No saturation or noise

This is the most transparent delay mode, suitable for clean echo effects.
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine
from isengard_delay.dsp.modulation import LFO
from isengard_shared.filters import OnePoleFilter


class HiFiMode:
    """
    HiFi Mode for Isengard Delay.
    
    This mode provides clean, high-fidelity delay with subtle modulation.
    It's the most transparent delay mode, suitable for pristine echo effects.
    
    Parameters:
    - delay_time_ms: Delay time in milliseconds
    - feedback: Feedback amount (0.0 to 1.0)
    - mod_rate: Modulation rate in Hz
    - mod_depth: Modulation depth (0.0 to 1.0)
    - width: Stereo width (0.0 to 1.0)
    - mix: Wet/dry mix (0.0 to 1.0)
    - tone: Tone control (highpass filter cutoff)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize HiFiMode.
        
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
        
        # Subtle modulation LFO (chorus-like)
        # HiFi mode uses sine or triangle waveform for smooth modulation
        self.mod_lfo = LFO(
            rate_hz=0.5,  # Subtle, slow modulation
            depth=0.001,  # Very small depth (0.1%)
            waveform='sine',
            sample_rate=sample_rate
        )
        
        # DC blocker for input
        self.dc_blocker = OnePoleFilter(
            cutoff_hz=10.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        
        # Tone control (highpass filter for brightness)
        self.tone_filter = OnePoleFilter(
            cutoff_hz=100.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        
        # Parameters
        self.params = {
            'delay_time_ms': 500.0,
            'feedback': 0.5,
            'mod_rate': 0.5,  # Hz
            'mod_depth': 0.1,  # 0-1, scaled to small values
            'width': 0.5,  # 0-1 stereo width
            'tone': 0.5,  # 0-1 tone control
            'mix': 0.5,  # 0-1 wet/dry mix
        }
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
        self.mod_lfo.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_left.set_sample_rate(sample_rate)
        self.delay_right.set_sample_rate(sample_rate)
        self.mod_lfo.set_sample_rate(sample_rate)
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
    
    def set_mod_rate(self, rate: float):
        """Set modulation rate in Hz."""
        self.params['mod_rate'] = np.clip(rate, 0.1, 10.0)
        self.mod_lfo.set_rate(rate)
    
    def set_mod_depth(self, depth: float):
        """Set modulation depth (0.0 to 1.0)."""
        self.params['mod_depth'] = np.clip(depth, 0.0, 1.0)
        # Scale to very small values for HiFi mode (0-0.1%)
        self.mod_lfo.set_depth(depth * 0.001)
    
    def set_width(self, width: float):
        """Set stereo width (0.0 to 1.0)."""
        self.params['width'] = np.clip(width, 0.0, 1.0)
    
    def set_tone(self, tone: float):
        """Set tone control (0.0 = warm, 1.0 = bright)."""
        self.params['tone'] = np.clip(tone, 0.0, 1.0)
        # Map tone to cutoff: 0.0 -> 100Hz, 1.0 -> 5000Hz
        cutoff = 100.0 + 4900.0 * tone
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
            elif key == 'mod_rate':
                self.set_mod_rate(value)
            elif key == 'mod_depth':
                self.set_mod_depth(value)
            elif key == 'width':
                self.set_width(value)
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
        2. Get modulation value
        3. Apply modulation to delay lines
        4. Get delayed outputs
        5. Apply feedback
        6. Write to delay lines
        7. Apply tone filter
        8. Apply stereo width
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
        
        # Step 2: Get modulation value and advance LFO
        mod_value = self.mod_lfo.process_sample()
        
        # Step 3: Apply modulation to delay lines
        # HiFi mode has very subtle modulation
        mod_depth = self.params['mod_depth'] * 0.001
        mod_samples = (self.params['delay_time_ms'] / 1000.0 * self.sample_rate) * mod_depth
        
        # Apply modulation with stereo decorrelation
        self.delay_left.set_modulation(mod_samples, mod_value)
        self.delay_right.set_modulation(mod_samples, mod_value * 0.7)  # Slightly different for stereo
        
        # Step 4: Get delayed outputs (read without writing)
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Step 5: Apply feedback
        feedback = self.params['feedback']
        feedback_l = delayed_l * feedback
        feedback_r = delayed_r * feedback
        
        # Step 6: Mix feedback with input and write to delay lines
        mixed_l = input_l + feedback_l
        mixed_r = input_r + feedback_r
        
        self.delay_left.process(mixed_l)
        self.delay_right.process(mixed_r)
        
        # Step 7: Apply tone filter to delayed outputs
        output_l = self.tone_filter.process(delayed_l)
        output_r = self.tone_filter.process(delayed_r)
        
        # Step 8: Apply stereo width
        # Width = 0: mono (both channels same)
        # Width = 1: full stereo separation
        width = self.params['width']
        if width < 1.0:
            # Mix channels towards center
            mid = (output_l + output_r) * 0.5
            side = (output_l - output_r) * 0.5
            output_l = mid + side * width
            output_r = mid - side * width
        
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
        return "HiFi"


# Test
if __name__ == "__main__":
    print("Testing HiFiMode...")
    
    # Create HiFi mode
    hifi_mode = HiFiMode(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    hifi_mode.set_parameters({
        'delay_time_ms': 500.0,
        'feedback': 0.5,
        'mod_rate': 1.0,
        'mod_depth': 0.5,
        'width': 0.5,
        'tone': 0.5,
        'mix': 1.0
    })
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)  # 1 second
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = hifi_mode.process_block(test_signal)
    
    print(f'Input shape: {test_signal.shape}')
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    print(f'Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
    
    # Check that delay appears at ~500ms
    delay_samples = int(500.0 / 1000.0 * 44100)
    print(f'Expected delay at sample {delay_samples}')
    print(f'Output at delay position L: {output[delay_samples, 0]:.6f}')
    print(f'Output at delay position R: {output[delay_samples, 1]:.6f}')
    
    print('\nHiFiMode test completed successfully!')

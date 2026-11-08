"""
Tape Mode Implementation

Based on ValhallaDelay Tape mode (E008-E012)

Characteristics:
- Analog tape emulation
- Wow/Flutter modulation (rates are functions of delay time)
- Tape saturation (tanh-based soft clipping)
- Mechanical noise
- Feedback path with tape characteristics

Modulation Scaling (E012):
- Wow rate: 1000ms / delayTimeMs (clamped to 0.1-2Hz)
- Flutter rate: Wow rate * 10 (clamped to 2-20Hz)
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine
from isengard_delay.dsp.modulation import WowFlutterLFO
from isengard_shared.filters import OnePoleFilter


class TapeSaturation:
    """
    Tape saturation using tanh-based soft clipping.
    
    Drive parameter controls the amount of saturation:
    - 0.0: No saturation (linear)
    - 1.0: Maximum saturation
    """
    
    def __init__(self):
        self.drive = 0.0
        self.input_gain = 1.0
        self.output_gain = 1.0
    
    def set_drive(self, drive: float):
        """Set drive amount (0.0 to 1.0)."""
        self.drive = np.clip(drive, 0.0, 1.0)
        # Map drive to input gain: 0 -> 1x, 1 -> 4x
        self.input_gain = 1.0 + 3.0 * self.drive
        # Compensate output to maintain similar level
        self.output_gain = 1.0 / (1.0 + 0.5 * self.drive)
    
    def process(self, x: float) -> float:
        """Process single sample through tape saturation."""
        # Apply input gain
        x = x * self.input_gain
        
        # Soft clipping using tanh
        x = np.tanh(x)
        
        # Apply output gain
        return x * self.output_gain
    
    def process_block(self, x: np.ndarray) -> np.ndarray:
        """Process block of samples."""
        x = x * self.input_gain
        x = np.tanh(x)
        return x * self.output_gain


class TapeHissGenerator:
    """
    Generate mechanical tape hiss noise.
    
    The noise level should be consistent and subtle, representing
    the inherent noise floor of analog tape.
    """
    
    def __init__(self, sample_rate: int = 44100, seed: int = 42):
        self.sample_rate = sample_rate
        self.seed = seed
        self.noise_level = 0.001  # Default hiss level (-60dB)
        self._rng_state = np.random.RandomState(seed)
    
    def set_noise_level(self, level: float):
        """Set noise level (0.0 to 1.0)."""
        self.noise_level = np.clip(level, 0.0, 1.0) * 0.005  # Scale to -46dB max
    
    def generate(self, num_samples: int) -> np.ndarray:
        """Generate white noise."""
        return self._rng_state.uniform(-1.0, 1.0, num_samples) * self.noise_level
    
    def generate_sample(self) -> float:
        """Generate single noise sample."""
        return (self._rng_state.random() * 2.0 - 1.0) * self.noise_level


class TapeMode:
    """
    Tape Mode for Isengard Delay.
    
    This mode emulates analog tape delay characteristics:
    - Wow and flutter modulation (pitch variation)
    - Tape saturation (nonlinear distortion)
    - Mechanical hiss noise
    - Smooth frequency response
    
    Parameters:
    - delay_time_ms: Delay time in milliseconds
    - feedback: Feedback amount (0.0 to 1.0)
    - mod_rate: Modulation rate (affects wow/flutter base rates)
    - mod_depth: Modulation depth (0.0 to 1.0)
    - drive: Tape saturation drive (0.0 to 1.0)
    - wow_depth: Wow modulation depth (0.0 to 1.0)
    - flutter_depth: Flutter modulation depth (0.0 to 1.0)
    - tone: Tone control (lowpass filter cutoff)
    - mix: Wet/dry mix (0.0 = dry only, 1.0 = wet only)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize TapeMode.
        
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
        
        # Wow and flutter LFOs
        self.wow_flutter_lfo = WowFlutterLFO(
            sample_rate=sample_rate,
            delay_time_ms=500.0  # Initial value
        )
        
        # Tape saturation
        self.saturation = TapeSaturation()
        
        # Tape hiss generator
        self.hiss_gen = TapeHissGenerator(sample_rate=sample_rate)
        
        # Lowpass filter for tone control (emulating tape's limited bandwidth)
        self.tone_filter = OnePoleFilter(
            cutoff_hz=10000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        
        # DC blocker
        self.dc_blocker = OnePoleFilter(
            cutoff_hz=10.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        
        # Parameters
        self.params = {
            'delay_time_ms': 500.0,
            'feedback': 0.5,
            'mod_rate': 1.0,
            'mod_depth': 0.3,
            'drive': 0.0,
            'wow_depth': 0.3,
            'flutter_depth': 0.2,
            'tone': 1.0,  # 0.0 = dark, 1.0 = bright
            'mix': 0.5,  # 0.0 = dry only, 1.0 = wet only
        }
        
        # Internal state
        self._feedback_buffer = np.zeros(2)  # [L, R] feedback samples
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
        self.wow_flutter_lfo.reset()
        self._feedback_buffer = np.zeros(2)
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_left.set_sample_rate(sample_rate)
        self.delay_right.set_sample_rate(sample_rate)
        self.wow_flutter_lfo.set_sample_rate(sample_rate)
        self.tone_filter.set_sample_rate(sample_rate)
        self.dc_blocker.set_sample_rate(sample_rate)
        self.hiss_gen = TapeHissGenerator(sample_rate=sample_rate)
    
    def set_delay_time(self, delay_time_ms: float):
        """Set delay time in milliseconds."""
        delay_time_ms = np.clip(delay_time_ms, 1.0, self.max_delay_ms)
        self.params['delay_time_ms'] = delay_time_ms
        delay_seconds = delay_time_ms / 1000.0
        self.delay_left.set_delay_time(delay_seconds)
        self.delay_right.set_delay_time(delay_seconds)
        
        # Update wow/flutter rates based on delay time (E012)
        self.wow_flutter_lfo.set_delay_time(delay_time_ms)
    
    def set_feedback(self, feedback: float):
        """Set feedback amount (0.0 to 1.0)."""
        self.params['feedback'] = np.clip(feedback, 0.0, 0.999)
    
    def set_mod_rate(self, rate: float):
        """Set modulation rate multiplier."""
        self.params['mod_rate'] = np.clip(rate, 0.0, 2.0)
        # Note: WowFlutterLFO doesn't have rate multiplier, rates are determined by delay time
    
    def set_mod_depth(self, depth: float):
        """Set modulation depth."""
        self.params['mod_depth'] = np.clip(depth, 0.0, 1.0)
        # Note: WowFlutterLFO doesn't have depth multiplier, depths are set separately for wow/flutter
    
    def set_drive(self, drive: float):
        """Set tape saturation drive."""
        self.params['drive'] = np.clip(drive, 0.0, 1.0)
        self.saturation.set_drive(drive)
    
    def set_wow_depth(self, depth: float):
        """Set wow modulation depth."""
        self.params['wow_depth'] = np.clip(depth, 0.0, 1.0)
        self.wow_flutter_lfo.set_wow_depth(depth)
    
    def set_flutter_depth(self, depth: float):
        """Set flutter modulation depth."""
        self.params['flutter_depth'] = np.clip(depth, 0.0, 1.0)
        self.wow_flutter_lfo.set_flutter_depth(depth)
    
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
            elif key == 'mod_rate':
                self.set_mod_rate(value)
            elif key == 'mod_depth':
                self.set_mod_depth(value)
            elif key == 'drive':
                self.set_drive(value)
            elif key == 'wow_depth':
                self.set_wow_depth(value)
            elif key == 'flutter_depth':
                self.set_flutter_depth(value)
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
        2. Get wow/flutter modulation values
        3. Apply modulation to delay lines (via set_modulation)
        4. Get delayed outputs from delay lines
        5. Apply tape saturation to feedback path
        6. Mix feedback with input
        7. Write mixed signal to delay lines
        8. Apply tone filter to delayed outputs
        9. Add tape hiss
        10. Apply dry/wet mix
        
        Note: The DelayLine.process() method writes input and returns delayed output.
        We need to separate the read and write operations for feedback.
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Step 1: DC blocking
        input_l = self.dc_blocker.process(input_l)
        input_r = self.dc_blocker.process(input_r)
        
        # Step 2: Get modulation values
        wow_mod, flutter_mod = self.wow_flutter_lfo.get_values()
        
        # Step 3: Apply modulation to delay lines
        # Modulation depth from parameters
        mod_depth = self.params['mod_depth']
        wow_depth = self.params['wow_depth']
        flutter_depth = self.params['flutter_depth']
        
        # Calculate modulation amount
        mod_amount = (wow_depth * wow_mod + flutter_depth * flutter_mod) * mod_depth
        
        # Apply modulation in samples
        base_delay_samples = self.params['delay_time_ms'] / 1000.0 * self.sample_rate
        mod_samples = base_delay_samples * mod_amount * 0.005  # +/- 0.5% max
        
        self.delay_left.set_modulation(mod_samples, wow_mod + flutter_mod * 0.3)
        self.delay_right.set_modulation(mod_samples * 0.9, wow_mod + flutter_mod * 0.3)
        
        # Step 4: Get delayed outputs (read without writing)
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Step 5: Process feedback path
        feedback_l = delayed_l * self.params['feedback']
        feedback_r = delayed_r * self.params['feedback']
        
        # Apply tape saturation to feedback
        feedback_l = self.saturation.process(feedback_l)
        feedback_r = self.saturation.process(feedback_r)
        
        # Step 6: Mix feedback with input
        mixed_l = input_l + feedback_l
        mixed_r = input_r + feedback_r
        
        # Step 7: Write mixed signal to delay lines
        self.delay_left.process(mixed_l)
        self.delay_right.process(mixed_r)
        
        # Step 8: Apply tone filter to delayed outputs (from step 4)
        output_l = self.tone_filter.process(delayed_l)
        output_r = self.tone_filter.process(delayed_r)
        
        # Step 9: Add tape hiss
        hiss_l = self.hiss_gen.generate_sample()
        hiss_r = self.hiss_gen.generate_sample()
        output_l += hiss_l
        output_r += hiss_r
        
        # Step 10: Apply dry/wet mix
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
        return "Tape"


# Test
if __name__ == "__main__":
    print("Testing TapeMode...")
    
    # Create tape mode
    tape_mode = TapeMode(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    tape_mode.set_parameters({
        'delay_time_ms': 500.0,
        'feedback': 0.5,
        'mod_rate': 1.0,
        'mod_depth': 0.3,
        'drive': 0.5,
        'wow_depth': 0.3,
        'flutter_depth': 0.2,
        'tone': 0.7,
        'mix': 1.0
    })
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)  # 1 second
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = tape_mode.process_block(test_signal)
    
    print(f'Input shape: {test_signal.shape}')
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    print(f'Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
    
    # Check that delay appears at ~500ms
    delay_samples = int(500.0 / 1000.0 * 44100)
    print(f'Expected delay at sample {delay_samples}')
    print(f'Output at delay position L: {output[delay_samples, 0]:.6f}')
    print(f'Output at delay position R: {output[delay_samples, 1]:.6f}')
    
    print('\nTapeMode test completed successfully!')

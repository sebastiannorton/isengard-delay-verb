"""
BBD Mode Implementation

Based on ValhallaDelay BBD mode (E015-E017)

Characteristics:
- Bucket Brigade Device emulation
- Noise tracks signal level via compander (E017)
- Clock jitter modulation
- Limited bandwidth (lowpass filter)
- Added noise that follows signal level

Noise Tracking (E017):
- noiseScale = max(0.01, 1.0 - signalLevel * 0.9)
- noiseLevel = noiseScale * noiseAmount
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine
from isengard_delay.dsp.modulation import LFO
from isengard_shared.filters import OnePoleFilter


class BBDCompander:
    """
    BBD-style compander for noise tracking.
    
    The noise level tracks the signal level, reducing noise when the
    signal is present and increasing it when the signal is quiet.
    
    This emulates the behavior of analog BBD circuits where the noise
    floor is more audible when there's no signal.
    
    Noise Tracking (E017):
    - noiseScale = max(0.01, 1.0 - signalLevel * 0.9)
    - noiseLevel = noiseScale * noiseAmount
    """
    
    def __init__(self, noise_amount: float = 0.01, sample_rate: int = 44100):
        self.noise_amount = np.clip(noise_amount, 0.0, 0.1)
        self.sample_rate = sample_rate
        
        # Signal level tracking (with smoothing)
        self.signal_level = 0.0
        self.smoothing_alpha = 0.01  # Smoothing factor
        
        # Noise generator state
        self._rng_state = np.random.RandomState()
        
        # Lowpass filter for BBD characteristic
        self.lowpass = OnePoleFilter(
            cutoff_hz=5000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
    
    def set_noise_amount(self, amount: float):
        """Set noise amount (0.0 to 0.1)."""
        self.noise_amount = np.clip(amount, 0.0, 0.1)
    
    def set_cutoff(self, cutoff_hz: float):
        """Set lowpass cutoff frequency."""
        self.lowpass.set_cutoff(cutoff_hz)
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.lowpass.set_sample_rate(sample_rate)
    
    def process(self, x: float) -> float:
        """
        Process a single sample through BBD compander.
        
        Args:
            x: Input sample
            
        Returns:
            Output sample with noise and filtering
        """
        # Update signal level (absolute value for envelope tracking)
        signal_abs = abs(x)
        self.signal_level = (1.0 - self.smoothing_alpha) * self.signal_level + \
                           self.smoothing_alpha * signal_abs
        
        # Calculate noise scale based on signal level (E017)
        noise_scale = max(0.01, 1.0 - self.signal_level * 0.9)
        noise_level = noise_scale * self.noise_amount
        
        # Generate noise
        noise = (self._rng_state.random() * 2.0 - 1.0) * noise_level
        
        # Apply lowpass filter (BBD characteristic)
        filtered = self.lowpass.process(x)
        
        # Add noise
        return filtered + noise
    
    def process_block(self, x: np.ndarray) -> np.ndarray:
        """Process a block of samples."""
        result = np.zeros_like(x)
        for i in range(x.shape[0]):
            result[i] = self.process(x[i])
        return result


class BBDMode:
    """
    BBD Mode for Isengard Delay.
    
    This mode emulates Bucket Brigade Device (BBD) delay characteristics:
    - Noise that tracks signal level via compander
    - Clock jitter modulation
    - Limited bandwidth (lowpass filter)
    - Added noise that follows signal level
    
    Parameters:
    - delay_time_ms: Delay time in milliseconds
    - feedback: Feedback amount (0.0 to 1.0)
    - mod_rate: Clock jitter rate in Hz
    - mod_depth: Clock jitter depth (0.0 to 1.0)
    - noise: Noise amount (0.0 to 1.0)
    - tone: Tone control (lowpass filter cutoff)
    - mix: Wet/dry mix (0.0 to 1.0)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize BBDMode.
        
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
            interpolation='linear'  # BBD typically has lower quality interpolation
        )
        self.delay_right = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='linear'
        )
        
        # BBD compander for noise tracking
        self.compander = BBDCompander(noise_amount=0.01, sample_rate=sample_rate)
        
        # Clock jitter LFO (random waveform)
        self.jitter_lfo = LFO(
            rate_hz=10.0,
            depth=0.001,
            waveform='random',
            sample_rate=sample_rate
        )
        
        # DC blocker for input
        self.dc_blocker = OnePoleFilter(
            cutoff_hz=10.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        
        # Parameters
        self.params = {
            'delay_time_ms': 500.0,
            'feedback': 0.5,
            'mod_rate': 10.0,
            'mod_depth': 0.1,
            'noise': 0.01,  # 0.0 to 0.1
            'tone': 0.5,  # 0.0 = darker, 1.0 = brighter
            'mix': 0.5,  # 0.0 = dry only, 1.0 = wet only
        }
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
        self.jitter_lfo.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_left.set_sample_rate(sample_rate)
        self.delay_right.set_sample_rate(sample_rate)
        self.compander.set_sample_rate(sample_rate)
        self.jitter_lfo.set_sample_rate(sample_rate)
        self.dc_blocker.set_sample_rate(sample_rate)
    
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
        """Set clock jitter rate in Hz."""
        self.params['mod_rate'] = np.clip(rate, 1.0, 50.0)
        self.jitter_lfo.set_rate(rate)
    
    def set_mod_depth(self, depth: float):
        """Set clock jitter depth (0.0 to 1.0)."""
        self.params['mod_depth'] = np.clip(depth, 0.0, 1.0)
        # Scale to small values for jitter
        self.jitter_lfo.set_depth(depth * 0.005)
    
    def set_noise(self, noise: float):
        """Set noise amount (0.0 to 0.1)."""
        self.params['noise'] = np.clip(noise, 0.0, 0.1)
        self.compander.set_noise_amount(noise)
    
    def set_tone(self, tone: float):
        """Set tone control (0.0 = darker, 1.0 = brighter)."""
        self.params['tone'] = np.clip(tone, 0.0, 1.0)
        # Map tone to BBD lowpass cutoff: 0.0 -> 2000Hz, 1.0 -> 8000Hz
        cutoff = 2000.0 + 6000.0 * tone
        self.compander.set_cutoff(cutoff)
    
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
            elif key == 'noise':
                self.set_noise(value)
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
        2. Apply BBD compander (noise tracking + lowpass)
        3. Get jitter modulation value
        4. Apply jitter to delay lines
        5. Get delayed outputs
        6. Apply feedback
        7. Write to delay lines
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
        
        # Step 2: Apply BBD compander (noise tracking + filtering)
        # This applies the BBD characteristic to the input
        input_l = self.compander.process(input_l)
        input_r = self.compander.process(input_r)
        
        # Step 3: Get jitter modulation value and advance LFO
        jitter_value = self.jitter_lfo.process_sample()
        
        # Step 4: Apply jitter to delay lines
        mod_depth = self.params['mod_depth'] * 0.005
        mod_samples = (self.params['delay_time_ms'] / 1000.0 * self.sample_rate) * mod_depth
        
        self.delay_left.set_modulation(mod_samples, jitter_value)
        self.delay_right.set_modulation(mod_samples * 0.8, jitter_value * 0.9)
        
        # Step 5: Get delayed outputs (read without writing)
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Step 6: Apply feedback
        feedback = self.params['feedback']
        feedback_l = delayed_l * feedback
        feedback_r = delayed_r * feedback
        
        # Step 7: Mix feedback with input and write to delay lines
        mixed_l = input_l + feedback_l
        mixed_r = input_r + feedback_r
        
        self.delay_left.process(mixed_l)
        self.delay_right.process(mixed_r)
        
        # Step 8: Apply dry/wet mix
        dry_l = input_l
        dry_r = input_r
        mix = self.params['mix']
        output_l = dry_l * (1.0 - mix) + delayed_l * mix
        output_r = dry_r * (1.0 - mix) + delayed_r * mix
        
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
        return "BBD"


# Test
if __name__ == "__main__":
    print("Testing BBDMode...")
    
    # Create BBD mode
    bbd_mode = BBDMode(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    bbd_mode.set_parameters({
        'delay_time_ms': 500.0,
        'feedback': 0.5,
        'mod_rate': 10.0,
        'mod_depth': 0.5,
        'noise': 0.01,
        'tone': 0.5,
        'mix': 1.0
    })
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)  # 1 second
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = bbd_mode.process_block(test_signal)
    
    print(f'Input shape: {test_signal.shape}')
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    print(f'Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
    
    # Check that delay appears at ~500ms
    delay_samples = int(500.0 / 1000.0 * 44100)
    print(f'Expected delay at sample {delay_samples}')
    print(f'Output at delay position L: {output[delay_samples, 0]:.6f}')
    print(f'Output at delay position R: {output[delay_samples, 1]:.6f}')
    
    print('\nBBDMode test completed successfully!')

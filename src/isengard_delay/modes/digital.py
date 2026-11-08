"""
Digital Mode Implementation

Based on ValhallaDelay Digital mode (E018-E019)

Characteristics:
- Clean digital delay
- Age parameter controls bit depth (50% = 12-bit)
- No modulation (unless specified)
- Precise, artifact-free delay

Age Mapping (E019):
- Age 0% = 24-bit
- Age 50% = 12-bit
- Age 100% = 8-bit
- Formula: bits = 24 - (int)(age * 16)
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine
from isengard_shared.filters import OnePoleFilter


class BitCrusher:
    """
    Bit depth reduction effect.
    
    Simulates the effect of low bit-depth digital systems by quantizing
    the signal to a specified number of bits.
    
    Parameters:
        bits: Number of bits (8-24)
    """
    
    def __init__(self, bits: int = 16):
        self.bits = np.clip(bits, 1, 24)
        self._update_step()
    
    def set_bits(self, bits: int):
        """Set the number of bits."""
        self.bits = np.clip(bits, 1, 24)
        self._update_step()
    
    def _update_step(self):
        """Calculate quantization step size."""
        if self.bits > 0:
            self.step = 2.0 / (2.0 ** self.bits)
        else:
            self.step = 0.0
    
    def process(self, x: float) -> float:
        """Quantize a single sample to the specified bit depth."""
        if self.bits >= 24:
            return x  # No quantization
        
        # Quantize to specified bits
        quantized = np.floor(x / self.step + 0.5) * self.step
        
        # Add dithering to reduce quantization artifacts
        # Simple triangular dither
        dither = (np.random.random() - 0.5) * self.step
        
        return quantized + dither * 0.5  # Reduced dither for subtlety
    
    def process_block(self, x: np.ndarray) -> np.ndarray:
        """Quantize a block of samples."""
        if self.bits >= 24:
            return x
        
        # Quantize
        quantized = np.floor(x / self.step + 0.5) * self.step
        
        # Add dither
        dither = (np.random.random(x.shape) - 0.5) * self.step
        
        return quantized + dither * 0.5


class DigitalMode:
    """
    Digital Mode for Isengard Delay.
    
    This mode emulates clean digital delay with bit depth reduction
    controlled by the Age parameter.
    
    Parameters:
    - delay_time_ms: Delay time in milliseconds
    - feedback: Feedback amount (0.0 to 1.0)
    - age: Age parameter (0.0 to 1.0) controlling bit depth
    - tone: Tone control (lowpass filter cutoff)
    - mix: Wet/dry mix (0.0 to 1.0)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize DigitalMode.
        
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
            interpolation='linear'  # Digital mode can use linear for efficiency
        )
        self.delay_right = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='linear'
        )
        
        # Bit crusher for age parameter
        self.bit_crusher = BitCrusher(bits=16)
        
        # DC blocker for input
        self.dc_blocker = OnePoleFilter(
            cutoff_hz=10.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        
        # Tone control (lowpass filter)
        self.tone_filter = OnePoleFilter(
            cutoff_hz=10000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        
        # Parameters
        self.params = {
            'delay_time_ms': 500.0,
            'feedback': 0.5,
            'age': 0.0,  # 0.0 = 24-bit, 1.0 = 8-bit
            'tone': 0.5,  # 0.0 = dark, 1.0 = bright
            'mix': 0.5,  # 0.0 = dry only, 1.0 = wet only
        }
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
    
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
    
    def set_feedback(self, feedback: float):
        """Set feedback amount (0.0 to 1.0)."""
        self.params['feedback'] = np.clip(feedback, 0.0, 0.999)
    
    def set_age(self, age: float):
        """
        Set age parameter (0.0 to 1.0).
        
        Age Mapping (E019):
        - Age 0% = 24-bit
        - Age 50% = 12-bit
        - Age 100% = 8-bit
        - Formula: bits = 24 - (int)(age * 16)
        """
        age = np.clip(age, 0.0, 1.0)
        self.params['age'] = age
        
        # Calculate bit depth
        # bits = 24 - floor(age * 16)
        bits = 24 - int(age * 16)
        bits = np.clip(bits, 8, 24)
        
        self.bit_crusher.set_bits(bits)
    
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
            elif key == 'age':
                self.set_age(value)
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
        2. Apply bit crushing (age parameter)
        3. Get delayed outputs
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
        
        # Step 2: Apply bit crushing (in the input path for Digital mode)
        # This simulates the digital degradation
        input_l = self.bit_crusher.process(input_l)
        input_r = self.bit_crusher.process(input_r)
        
        # Step 3: Get delayed outputs (read without writing)
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Step 4: Apply feedback
        feedback = self.params['feedback']
        feedback_l = delayed_l * feedback
        feedback_r = delayed_r * feedback
        
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
        return "Digital"


# Test
if __name__ == "__main__":
    print("Testing DigitalMode...")
    
    # Create Digital mode
    digital_mode = DigitalMode(sample_rate=44100, max_delay_ms=5000.0)
    
    # Test with different age values
    for age in [0.0, 0.5, 1.0]:
        print(f"\n--- Testing with Age = {age} (bits = {24 - int(age * 16)}) ---")
        
        digital_mode.reset()
        digital_mode.set_parameters({
            'delay_time_ms': 500.0,
            'feedback': 0.0,  # No feedback for cleaner test
            'age': age,
            'tone': 0.5,
            'mix': 1.0
        })
        
        # Generate test signal (sine wave for better quantization visibility)
        t = np.arange(44100, dtype=np.float32) / 44100
        test_signal = np.zeros((44100, 2), dtype=np.float32)
        test_signal[:, 0] = 0.3 * np.sin(2 * np.pi * 1000.0 * t)
        test_signal[:, 1] = test_signal[:, 0]
        
        # Process
        output = digital_mode.process_block(test_signal)
        
        print(f'Output peak: {np.max(np.abs(output)):.6f}')
        print(f'Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
        
        # Check that delay appears at ~500ms
        delay_samples = int(500.0 / 1000.0 * 44100)
        print(f'Output at delay position: {output[delay_samples, 0]:.6f}')
    
    print('\nDigitalMode test completed successfully!')

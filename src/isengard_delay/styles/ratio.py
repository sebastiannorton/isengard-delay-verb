"""
Ratio Style Implementation

Based on ValhallaDelay Ratio style (E026)

Characteristics:
- Delay times related by musical ratios
- Creates rhythmic delay patterns

Ratio Calculation: delay2Ms = delay1Ms * ratio
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine


class RatioStyle:
    """
    Ratio Style for Isengard Delay.
    
    This style has two delay lines per channel with delay times
    related by a musical ratio (e.g., 1:2, 2:3, 3:4, etc.).
    
    Parameters:
    - ratio: Ratio between delay 1 and delay 2 (0.1 to 2.0)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize RatioStyle.
        
        Args:
            sample_rate: Audio sample rate in Hz
            max_delay_ms: Maximum delay time in milliseconds
        """
        self.sample_rate = sample_rate
        self.max_delay_ms = max_delay_ms
        
        # Delay lines for left channel
        self.delay_l1 = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='cubic'
        )
        self.delay_l2 = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='cubic'
        )
        
        # Delay lines for right channel
        self.delay_r1 = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='cubic'
        )
        self.delay_r2 = DelayLine(
            max_delay_seconds=max_delay_ms / 1000.0,
            sample_rate=sample_rate,
            interpolation='cubic'
        )
        
        # Parameters
        self.params = {
            'ratio': 0.5,  # 0.1 to 2.0
        }
    
    def reset(self):
        """Reset all internal state."""
        self.delay_l1.reset()
        self.delay_l2.reset()
        self.delay_r1.reset()
        self.delay_r2.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_l1.set_sample_rate(sample_rate)
        self.delay_l2.set_sample_rate(sample_rate)
        self.delay_r1.set_sample_rate(sample_rate)
        self.delay_r2.set_sample_rate(sample_rate)
    
    def set_delay_time(self, delay_time_ms: float):
        """
        Set base delay time.
        
        Args:
            delay_time_ms: Base delay time in milliseconds
        """
        ratio = self.params['ratio']
        
        # delay2 = delay1 * ratio
        delay1_ms = delay_time_ms
        delay2_ms = delay_time_ms * ratio
        
        self.delay_l1.set_delay_time(delay1_ms / 1000.0)
        self.delay_l2.set_delay_time(delay2_ms / 1000.0)
        self.delay_r1.set_delay_time(delay1_ms / 1000.0)
        self.delay_r2.set_delay_time(delay2_ms / 1000.0)
    
    def set_ratio(self, ratio: float):
        """Set ratio between delay 1 and 2 (0.1 to 2.0)."""
        self.params['ratio'] = np.clip(ratio, 0.1, 2.0)
    
    def set_parameters(self, params: dict):
        """Set all parameters at once."""
        for key, value in params.items():
            if key == 'ratio':
                self.set_ratio(value)
    
    def get_parameters(self) -> dict:
        """Get current parameters."""
        return self.params.copy()
    
    def process(self, input_l: float, input_r: float, delay_time_ms: float) -> Tuple[float, float]:
        """
        Process a sample pair through the Ratio style.
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            delay_time_ms: Base delay time in milliseconds
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Set delay times
        self.set_delay_time(delay_time_ms)
        
        # Process left channel: Delay 1 -> Delay 2
        delayed_l1 = self.delay_l1.read()
        self.delay_l1.process(input_l)
        
        delayed_l2 = self.delay_l2.read()
        self.delay_l2.process(delayed_l1)
        
        # Process right channel: Delay 1 -> Delay 2
        delayed_r1 = self.delay_r1.read()
        self.delay_r1.process(input_r)
        
        delayed_r2 = self.delay_r2.read()
        self.delay_r2.process(delayed_r1)
        
        # Output is the sum of both delays
        output_l = delayed_l1 + delayed_l2
        output_r = delayed_r1 + delayed_r2
        
        return output_l, output_r
    
    def process_block(self, input_block: np.ndarray, delay_time_ms: float) -> np.ndarray:
        """
        Process a block of audio samples.
        
        Args:
            input_block: Input audio as numpy array (N, 2)
            delay_time_ms: Base delay time in milliseconds
            
        Returns:
            Output audio as numpy array (N, 2)
        """
        num_samples = input_block.shape[0]
        output_block = np.zeros((num_samples, 2), dtype=np.float32)
        
        for i in range(num_samples):
            input_l = input_block[i, 0]
            input_r = input_block[i, 1]
            
            output_l, output_r = self.process(input_l, input_r, delay_time_ms)
            output_block[i, 0] = output_l
            output_block[i, 1] = output_r
        
        return output_block
    
    def get_name(self) -> str:
        """Get style name."""
        return "Ratio"


# Test
if __name__ == "__main__":
    print("Testing RatioStyle...")
    
    ratio = RatioStyle(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    ratio.set_parameters({'ratio': 0.5})  # delay2 = delay1 * 0.5
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = ratio.process_block(test_signal, delay_time_ms=500.0)
    
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    
    # Check delays at different positions
    delay1_samples = int(500.0 / 1000.0 * 44100)
    delay2_samples = int(250.0 / 1000.0 * 44100)  # 500 * 0.5
    
    print(f'Output at delay1 (500ms): {output[delay1_samples, 0]:.6f}')
    print(f'Output at delay2 (250ms): {output[delay2_samples, 0]:.6f}')
    
    print('\nRatioStyle test completed successfully!')

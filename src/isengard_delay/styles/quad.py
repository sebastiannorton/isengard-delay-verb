"""
Quad Style Implementation

Based on ValhallaDelay Quad style (E028)

Characteristics:
- Four delay lines
- Complex stereo routing
- Creates dense, rich delay textures

Signal Flow:
Left Input -> Left Delay 1 -> Left Delay 2 -> Left Output
            -> Right Delay 1 -> Right Delay 2 -> Right Output
Right Input -> Right Delay 1 -> Right Delay 2 -> Right Output
            -> Left Delay 1 -> Left Delay 2 -> Left Output
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine


class QuadStyle:
    """
    Quad Style for Isengard Delay.
    
    This style has four delay lines with complex stereo routing,
    creating dense, rich delay textures.
    
    Parameters:
    - spread: Stereo spread (0.0 to 1.0)
    - width: Width control (0.0 to 1.0)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize QuadStyle.
        
        Args:
            sample_rate: Audio sample rate in Hz
            max_delay_ms: Maximum delay time in milliseconds
        """
        self.sample_rate = sample_rate
        self.max_delay_ms = max_delay_ms
        
        # Four delay lines
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
            'spread': 0.0,  # 0.0 = mono, 1.0 = max stereo spread
            'width': 0.5,   # 0.0 to 1.0
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
        spread = self.params['spread']
        width = self.params['width']
        
        # Calculate delay times with spread and width
        # L1: base_delay * (1.0 - spread * 0.25)
        # L2: base_delay * (1.0 + spread * 0.25) * (1.0 - width * 0.25)
        # R1: base_delay * (1.0 + spread * 0.25)
        # R2: base_delay * (1.0 - spread * 0.25) * (1.0 + width * 0.25)
        
        delay_l1 = delay_time_ms * (1.0 - spread * 0.25)
        delay_l2 = delay_time_ms * (1.0 + spread * 0.25) * (1.0 - width * 0.25)
        delay_r1 = delay_time_ms * (1.0 + spread * 0.25)
        delay_r2 = delay_time_ms * (1.0 - spread * 0.25) * (1.0 + width * 0.25)
        
        self.delay_l1.set_delay_time(delay_l1 / 1000.0)
        self.delay_l2.set_delay_time(delay_l2 / 1000.0)
        self.delay_r1.set_delay_time(delay_r1 / 1000.0)
        self.delay_r2.set_delay_time(delay_r2 / 1000.0)
    
    def set_spread(self, spread: float):
        """Set stereo spread (0.0 to 1.0)."""
        self.params['spread'] = np.clip(spread, 0.0, 1.0)
    
    def set_width(self, width: float):
        """Set width (0.0 to 1.0)."""
        self.params['width'] = np.clip(width, 0.0, 1.0)
    
    def set_parameters(self, params: dict):
        """Set all parameters at once."""
        for key, value in params.items():
            if key == 'spread':
                self.set_spread(value)
            elif key == 'width':
                self.set_width(value)
    
    def get_parameters(self) -> dict:
        """Get current parameters."""
        return self.params.copy()
    
    def process(self, input_l: float, input_r: float, delay_time_ms: float) -> Tuple[float, float]:
        """
        Process a sample pair through the Quad style.
        
        Signal flow:
        Left Input -> Left Delay 1 -> Left Delay 2 -> Left Output
                    -> Right Delay 1 -> Right Delay 2 -> Right Output
        Right Input -> Right Delay 1 -> Right Delay 2 -> Right Output
                     -> Left Delay 1 -> Left Delay 2 -> Left Output
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            delay_time_ms: Base delay time in milliseconds
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Set delay times
        self.set_delay_time(delay_time_ms)
        
        # Get delayed outputs
        delayed_l1 = self.delay_l1.read()
        delayed_l2 = self.delay_l2.read()
        delayed_r1 = self.delay_r1.read()
        delayed_r2 = self.delay_r2.read()
        
        # Write to delay lines with cross-routing
        # L1 gets: input_l + input_r (cross from right)
        # L2 gets: delayed_l1
        # R1 gets: input_r + input_l (cross from left)
        # R2 gets: delayed_r1
        
        self.delay_l1.process(input_l + input_r * 0.5)
        self.delay_l2.process(delayed_l1)
        self.delay_r1.process(input_r + input_l * 0.5)
        self.delay_r2.process(delayed_r1)
        
        # Output: Sum of both delay lines per channel
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
        return "Quad"


# Test
if __name__ == "__main__":
    print("Testing QuadStyle...")
    
    quad = QuadStyle(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    quad.set_parameters({'spread': 0.5, 'width': 0.5})
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = quad.process_block(test_signal, delay_time_ms=500.0)
    
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    
    print('\nQuadStyle test completed successfully!')

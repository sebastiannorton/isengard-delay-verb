"""
Single Style Implementation

Based on ValhallaDelay Single style (E024)

Characteristics:
- Single delay line per channel
- Independent L/R delays
- Simplest style

Signal Flow:
Left Input -> Left Delay -> Left Output
Right Input -> Right Delay -> Right Output
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine


class SingleStyle:
    """
    Single Style for Isengard Delay.
    
    This is the simplest delay style with one delay line per channel.
    Each channel (L/R) has its own independent delay line.
    
    Parameters:
    - spread: Stereo spread (0.0 to 1.0) - controls delay time difference between L/R
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize SingleStyle.
        
        Args:
            sample_rate: Audio sample rate in Hz
            max_delay_ms: Maximum delay time in milliseconds
        """
        self.sample_rate = sample_rate
        self.max_delay_ms = max_delay_ms
        
        # Delay lines for left and right channels
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
        
        # Parameters
        self.params = {
            'spread': 0.0,  # 0.0 = mono, 1.0 = max stereo spread
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
    
    def set_delay_time(self, delay_time_ms: float, spread: float = 0.0):
        """
        Set delay time for both channels.
        
        Args:
            delay_time_ms: Base delay time in milliseconds
            spread: Stereo spread (0.0 to 1.0)
        """
        self.params['spread'] = np.clip(spread, 0.0, 1.0)
        
        # Calculate left and right delay times
        # Left: base_delay * (1.0 - spread * 0.5)
        # Right: base_delay * (1.0 + spread * 0.5)
        delay_l = delay_time_ms * (1.0 - spread * 0.5)
        delay_r = delay_time_ms * (1.0 + spread * 0.5)
        
        self.delay_left.set_delay_time(delay_l / 1000.0)
        self.delay_right.set_delay_time(delay_r / 1000.0)
    
    def set_spread(self, spread: float):
        """Set stereo spread (0.0 to 1.0)."""
        self.params['spread'] = np.clip(spread, 0.0, 1.0)
    
    def set_parameters(self, params: dict):
        """Set all parameters at once."""
        for key, value in params.items():
            if key == 'spread':
                self.set_spread(value)
    
    def get_parameters(self) -> dict:
        """Get current parameters."""
        return self.params.copy()
    
    def process(self, input_l: float, input_r: float, delay_time_ms: float) -> Tuple[float, float]:
        """
        Process a sample pair through the Single style.
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            delay_time_ms: Base delay time in milliseconds
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Set delay times (in case they changed)
        self.set_delay_time(delay_time_ms, self.params['spread'])
        
        # Get delayed outputs
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Write inputs to delay lines
        self.delay_left.process(input_l)
        self.delay_right.process(input_r)
        
        return delayed_l, delayed_r
    
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
        return "Single"


# Test
if __name__ == "__main__":
    print("Testing SingleStyle...")
    
    single = SingleStyle(sample_rate=44100, max_delay_ms=5000.0)
    
    # Set parameters
    single.set_parameters({'spread': 0.5})
    
    # Generate test signal (impulse)
    test_signal = np.zeros((44100, 2), dtype=np.float32)
    test_signal[0, 0] = 0.5
    test_signal[0, 1] = 0.5
    
    # Process
    output = single.process_block(test_signal, delay_time_ms=500.0)
    
    print(f'Output shape: {output.shape}')
    print(f'Output peak: {np.max(np.abs(output)):.6f}')
    
    # Check that delay appears at ~500ms
    delay_samples_l = int(500.0 * 0.75 / 1000.0 * 44100)  # Left is shorter
    delay_samples_r = int(500.0 * 1.25 / 1000.0 * 44100)  # Right is longer
    
    print(f'Output at left delay position: {output[delay_samples_l, 0]:.6f}')
    print(f'Output at right delay position: {output[delay_samples_r, 1]:.6f}')
    
    print('\nSingleStyle test completed successfully!')

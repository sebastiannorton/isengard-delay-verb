"""
PingPong Style Implementation

Based on ValhallaDelay PingPong style (E027)

Characteristics:
- Delays bounce between L/R channels
- Creates ping-pong echo effects

Signal Flow:
Left Input -> Left Delay -> Right Output
Right Input -> Right Delay -> Left Output
Feedback: Left Delay Out -> Right Delay In
          Right Delay Out -> Left Delay In
"""

import numpy as np
from typing import Tuple

from isengard_shared.delay_line import DelayLine


class PingPongStyle:
    """
    PingPong Style for Isengard Delay.
    
    This style creates ping-pong echo effects where the delays
    bounce between left and right channels.
    
    Parameters:
    - None (uses mode's delay time)
    """
    
    def __init__(self, sample_rate: int = 44100, max_delay_ms: float = 5000.0):
        """
        Initialize PingPongStyle.
        
        Args:
            sample_rate: Audio sample rate in Hz
            max_delay_ms: Maximum delay time in milliseconds
        """
        self.sample_rate = sample_rate
        self.max_delay_ms = max_delay_ms
        
        # Delay lines
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
        self.params = {}
        
        # Internal state for ping-pong direction
        self._direction = True  # True = L->R, False = R->L
    
    def reset(self):
        """Reset all internal state."""
        self.delay_left.reset()
        self.delay_right.reset()
        self._direction = True
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_left.set_sample_rate(sample_rate)
        self.delay_right.set_sample_rate(sample_rate)
    
    def set_delay_time(self, delay_time_ms: float):
        """
        Set delay time for both channels.
        
        Args:
            delay_time_ms: Delay time in milliseconds
        """
        self.delay_left.set_delay_time(delay_time_ms / 1000.0)
        self.delay_right.set_delay_time(delay_time_ms / 1000.0)
    
    def set_parameters(self, params: dict):
        """Set all parameters at once."""
        # PingPong style doesn't have its own parameters
        pass
    
    def get_parameters(self) -> dict:
        """Get current parameters."""
        return self.params.copy()
    
    def process(self, input_l: float, input_r: float, delay_time_ms: float) -> Tuple[float, float]:
        """
        Process a sample pair through the PingPong style.
        
        Signal flow:
        - Input L goes to Left Delay
        - Input R goes to Right Delay
        - Left Delay output goes to Right Output
        - Right Delay output goes to Left Output
        - Feedback: Left Delay Out -> Right Delay In
                    Right Delay Out -> Left Delay In
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            delay_time_ms: Delay time in milliseconds
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Set delay times
        self.set_delay_time(delay_time_ms)
        
        # Get delayed outputs
        delayed_l = self.delay_left.read()
        delayed_r = self.delay_right.read()
        
        # Write to delay lines with cross-feedback
        # Left delay gets: input_l + feedback from right delay
        # Right delay gets: input_r + feedback from left delay
        feedback_l = delayed_r  # Right delay output feeds left delay
        feedback_r = delayed_l  # Left delay output feeds right delay
        
        self.delay_left.process(input_l + feedback_l)
        self.delay_right.process(input_r + feedback_r)
        
        # Output: Left delay output goes to right, right delay output goes to left
        output_l = delayed_r
        output_r = delayed_l
        
        return output_l, output_r
    
    def process_block(self, input_block: np.ndarray, delay_time_ms: float) -> np.ndarray:
        """
        Process a block of audio samples.
        
        Args:
            input_block: Input audio as numpy array (N, 2)
            delay_time_ms: Delay time in milliseconds
            
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
        return "PingPong"


# Test
if __name__ == "__main__":
    print("Testing PingPongStyle...")
    
    pingpong = PingPongStyle(sample_rate=44100, max_delay_ms=5000.0)
    
    # Generate test signal (impulse on left only)
    test_signal = np.zeros((44100, 2), dtype=np.float32)
    test_signal[0, 0] = 0.5  # Left only
    
    # Process
    output = pingpong.process_block(test_signal, delay_time_ms=500.0)
    
    print(f'Output shape: {output.shape}')
    print(f'Output peak L: {np.max(np.abs(output[:, 0])):.6f}')
    print(f'Output peak R: {np.max(np.abs(output[:, 1])):.6f}')
    
    # Check that left input appears on right output at 500ms
    delay_samples = int(500.0 / 1000.0 * 44100)
    print(f'Output at 500ms L: {output[delay_samples, 0]:.6f}')
    print(f'Output at 500ms R: {output[delay_samples, 1]:.6f}')
    
    print('\nPingPongStyle test completed successfully!')

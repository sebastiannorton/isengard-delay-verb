"""
Early Reflections Implementation

Early reflection generation for Isengard Verb.

This module generates early reflections for different reverb modes.
Early reflections are the first discrete echoes that arrive before
the dense late reverberation.

Each mode has a different early reflection pattern based on the
reference hardware/algorithm.
"""

import numpy as np
from typing import List, Tuple, Dict, Any

from isengard_shared.filters import OnePoleFilter
from isengard_shared.delay_line import DelayLine


class TapDelay:
    """
    A simple tap delay that stores input and can be read back after a delay.
    
    This is used for early reflection taps where we need to:
    1. Store the input at time t
    2. Read it back at time t + delay
    """
    
    def __init__(self, delay_ms: float, sample_rate: int = 44100):
        """
        Initialize tap delay.
        
        Args:
            delay_ms: Delay time in milliseconds
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.delay_samples = int(np.ceil(delay_ms * sample_rate / 1000.0))
        self.buffer = np.zeros(self.delay_samples, dtype=np.float32)
        self.write_pos = 0
    
    def reset(self):
        """Reset the buffer."""
        self.buffer.fill(0.0)
        self.write_pos = 0
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.delay_samples = int(np.ceil(self.delay_samples * sample_rate / self.sample_rate))
        self.buffer = np.zeros(self.delay_samples, dtype=np.float32)
    
    def write(self, sample: float):
        """
        Write a sample to the buffer.
        
        Args:
            sample: Sample to write
        """
        self.buffer[self.write_pos] = sample
        self.write_pos = (self.write_pos + 1) % self.delay_samples
    
    def read(self) -> float:
        """
        Read the delayed sample.
        
        Returns:
            Sample from delay_samples ago
        """
        read_pos = (self.write_pos) % self.delay_samples
        return self.buffer[read_pos]


class EarlyReflections:
    """
    Early reflection generator.
    
    Generates early reflections based on room geometry and mode.
    Each mode has a different early reflection pattern.
    
    Implementation:
    - Uses multiple tap delays for each reflection
    - Applies stereo panning to each tap
    - Includes high-frequency damping
    - Supports pre-delay
    """
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize early reflections generator.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        
        # Parameters
        self.params = {
            'size': 0.5,       # Room size (0.0 to 1.0)
            'width': 0.5,      # Stereo width (0.0 to 1.0)
            'pre_delay': 50.0, # Pre-delay in ms
            'early_level': 0.5, # Early reflection level (0.0 to 1.0)
        }
        
        # Tap delays and gains for early reflections
        # Each tap is: (delay_ms, gain_l, gain_r)
        self.taps = []
        
        # Tap delay objects
        self.tap_delays_l = []
        self.tap_delays_r = []
        
        # Pre-delay line
        self.pre_delay_line = DelayLine(
            max_delay_seconds=0.2,
            sample_rate=sample_rate
        )
        self.pre_delay_line.set_delay_time(self.params['pre_delay'] / 1000.0)
        
        # Damping filter for early reflections
        self.damping_filter = OnePoleFilter(
            cutoff_hz=10000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        
        # Initialize with default taps
        self._init_default_taps()
    
    def _init_default_taps(self):
        """Initialize with default tap configuration."""
        # Default taps (generic room)
        self.taps = [
            (20.0, 0.8, 0.6),   # First reflection
            (40.0, 0.6, 0.8),   # Second reflection
            (60.0, 0.5, 0.5),   # Third reflection
            (80.0, 0.4, 0.7),   # Fourth reflection
        ]
        
        # Create tap delays
        self._update_tap_delays()
    
    def _update_tap_delays(self):
        """Update tap delays based on current taps."""
        self.tap_delays_l = []
        self.tap_delays_r = []
        
        for tap_delay_ms, _, _ in self.taps:
            delay_l = TapDelay(tap_delay_ms, self.sample_rate)
            delay_r = TapDelay(tap_delay_ms, self.sample_rate)
            self.tap_delays_l.append(delay_l)
            self.tap_delays_r.append(delay_r)
    
    def reset(self):
        """Reset all internal state."""
        self.pre_delay_line.reset()
        for delay in self.tap_delays_l:
            delay.reset()
        for delay in self.tap_delays_r:
            delay.reset()
        self.damping_filter.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.pre_delay_line.set_sample_rate(sample_rate)
        for delay in self.tap_delays_l:
            delay.set_sample_rate(sample_rate)
        for delay in self.tap_delays_r:
            delay.set_sample_rate(sample_rate)
        self.damping_filter.set_sample_rate(sample_rate)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set all parameters at once."""
        for key, value in params.items():
            if key in self.params:
                self.params[key] = value
        
        # Update pre-delay
        self.pre_delay_line.set_delay_time(self.params['pre_delay'] / 1000.0)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.params.copy()
    
    def set_size(self, size: float):
        """Set room size."""
        self.params['size'] = np.clip(size, 0.0, 1.0)
    
    def set_width(self, width: float):
        """Set stereo width."""
        self.params['width'] = np.clip(width, 0.0, 1.0)
    
    def set_pre_delay(self, pre_delay_ms: float):
        """Set pre-delay time."""
        self.params['pre_delay'] = np.clip(pre_delay_ms, 0.0, 200.0)
        self.pre_delay_line.set_delay_time(pre_delay_ms / 1000.0)
    
    def set_early_level(self, level: float):
        """Set early reflection level."""
        self.params['early_level'] = np.clip(level, 0.0, 1.0)
    
    def set_taps(self, taps: List[Tuple[float, float, float]]):
        """
        Set the tap configuration.
        
        Args:
            taps: List of (delay_ms, gain_l, gain_r) tuples
        """
        self.taps = taps
        self._update_tap_delays()
    
    def set_mode(self, mode: str):
        """
        Set the reverb mode and configure taps accordingly.
        
        Args:
            mode: Reverb mode name (e.g., '1972', '1978', 'NOW1')
        """
        # Mode-specific tap configurations
        self.taps = self._get_taps_for_mode(mode)
        self._update_tap_delays()
    
    def _get_taps_for_mode(self, mode: str) -> List[Tuple[float, float, float]]:
        """
        Get tap configuration for a specific mode.
        
        Args:
            mode: Reverb mode name
            
        Returns:
            List of (delay_ms, gain_l, gain_r) tuples
        """
        # Mode-specific configurations
        mode_taps = {
            # 1970s modes
            '1972': [  # EMT 140 Plate
                (15.0, 0.6, 0.5),
                (30.0, 0.4, 0.6),
            ],
            '1974': [  # AMS RMX16
                (20.0, 0.55, 0.45),
                (45.0, 0.5, 0.5),
                (75.0, 0.45, 0.55),
            ],
            '1975': [  # Eventide SP2016
                (18.0, 0.6, 0.4),
                (42.0, 0.5, 0.5),
                (72.0, 0.4, 0.6),
            ],
            '1976': [  # EMT 250
                (25.0, 0.55, 0.5),
                (55.0, 0.5, 0.55),
                (90.0, 0.45, 0.6),
            ],
            '1977': [  # Quantec Room Simulator
                (22.0, 0.58, 0.45),
                (50.0, 0.52, 0.5),
                (85.0, 0.48, 0.55),
            ],
            '1978': [  # Lexicon 224
                (25.0, 0.6, 0.5),
                (50.0, 0.5, 0.6),
                (75.0, 0.5, 0.5),
                (100.0, 0.4, 0.6),
            ],
            '1979': [  # AMS RMX16 Variant
                (20.0, 0.55, 0.4),
                (45.0, 0.5, 0.45),
                (75.0, 0.45, 0.5),
            ],
            
            # 1980s modes
            '1980': [  # Lexicon 224X
                (25.0, 0.55, 0.45),
                (55.0, 0.5, 0.5),
                (90.0, 0.45, 0.55),
                (120.0, 0.4, 0.6),
            ],
            '1981': [  # Yamaha Rev1
                (15.0, 0.6, 0.45),
                (35.0, 0.55, 0.5),
                (60.0, 0.5, 0.55),
                (90.0, 0.45, 0.6),
            ],
            '1982': [  # Sony DRP-F300
                (25.0, 0.58, 0.45),
                (55.0, 0.52, 0.5),
                (90.0, 0.48, 0.55),
                (130.0, 0.42, 0.6),
            ],
            '1983': [  # AKG ADR68K
                (20.0, 0.58, 0.4),
                (45.0, 0.52, 0.45),
                (75.0, 0.48, 0.5),
                (110.0, 0.42, 0.55),
            ],
            '1984': [  # Roland SRV-2000
                (30.0, 0.55, 0.5),
                (60.0, 0.5, 0.55),
                (90.0, 0.45, 0.6),
                (120.0, 0.4, 0.65),
            ],
            '1985': [  # Lexicon 300
                (25.0, 0.55, 0.5),
                (55.0, 0.5, 0.55),
                (85.0, 0.45, 0.6),
                (120.0, 0.4, 0.65),
            ],
            '1986': [  # Yamaha Rev5
                (20.0, 0.6, 0.4),
                (45.0, 0.55, 0.45),
                (75.0, 0.5, 0.5),
                (110.0, 0.45, 0.55),
            ],
            '1987': [  # Lexicon 480L
                (20.0, 0.6, 0.4),
                (45.0, 0.55, 0.45),
                (75.0, 0.5, 0.5),
                (110.0, 0.45, 0.55),
                (150.0, 0.4, 0.6),
            ],
            
            # 1990s modes
            '1990': [  # Lexicon PCM70
                (25.0, 0.58, 0.45),
                (55.0, 0.52, 0.5),
                (90.0, 0.48, 0.55),
                (130.0, 0.42, 0.6),
            ],
            '1991': [  # Yamaha Rev7
                (20.0, 0.6, 0.4),
                (45.0, 0.55, 0.45),
                (75.0, 0.5, 0.5),
                (110.0, 0.45, 0.55),
            ],
            '1992': [  # Eventide H3000
                (15.0, 0.55, 0.4),
                (40.0, 0.5, 0.45),
                (70.0, 0.45, 0.5),
                (120.0, 0.4, 0.55),
                (180.0, 0.35, 0.6),
            ],
            '1993': [  # TC Electronic M3000
                (20.0, 0.58, 0.4),
                (50.0, 0.52, 0.45),
                (85.0, 0.48, 0.5),
                (130.0, 0.42, 0.55),
            ],
            '1994': [  # Lexicon PCM80
                (25.0, 0.56, 0.45),
                (55.0, 0.51, 0.5),
                (90.0, 0.47, 0.53),
                (130.0, 0.42, 0.58),
            ],
            '1995': [  # Yamaha SPX90
                (20.0, 0.6, 0.4),
                (45.0, 0.55, 0.45),
                (75.0, 0.5, 0.5),
                (110.0, 0.45, 0.55),
            ],
            
            # Modern modes
            'NOW1': [  # Modern Algorithm 1
                (15.0, 0.55, 0.35),
                (35.0, 0.5, 0.4),
                (65.0, 0.45, 0.45),
                (105.0, 0.4, 0.5),
                (155.0, 0.35, 0.55),
            ],
            'NOW2': [  # Modern Algorithm 2
                (10.0, 0.5, 0.3),
                (30.0, 0.45, 0.35),
                (60.0, 0.4, 0.4),
                (100.0, 0.35, 0.45),
                (150.0, 0.3, 0.5),
                (210.0, 0.25, 0.55),
            ],
        }
        
        # Return mode-specific taps if available, otherwise default
        return mode_taps.get(mode, [
            (20.0, 0.8, 0.6),
            (40.0, 0.6, 0.8),
            (60.0, 0.5, 0.5),
            (80.0, 0.4, 0.7),
        ])
    
    def process_sample(self, input_l: float, input_r: float) -> Tuple[float, float]:
        """
        Process a sample pair through early reflections.
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            
        Returns:
            Tuple of (output_l, output_r) with early reflections
        """
        # Apply pre-delay
        input_l_delayed = self.pre_delay_line.process(input_l)
        input_r_delayed = self.pre_delay_line.process(input_r)
        
        # Write to all tap delays
        for delay_l, delay_r in zip(self.tap_delays_l, self.tap_delays_r):
            delay_l.write(input_l_delayed)
            delay_r.write(input_r_delayed)
        
        # Process through each tap
        output_l = 0.0
        output_r = 0.0
        
        for i, (tap_delay_ms, gain_l, gain_r) in enumerate(self.taps):
            if i < len(self.tap_delays_l):
                # Read delayed signals
                delayed_l = self.tap_delays_l[i].read()
                delayed_r = self.tap_delays_r[i].read()
                
                # Apply gain and stereo panning
                # Width parameter affects stereo separation
                width = self.params['width']
                
                # Mix delayed signals with gains
                output_l += delayed_l * gain_l * (0.5 + 0.5 * width)
                output_r += delayed_r * gain_r * (0.5 + 0.5 * width)
                
                # Cross-feed for stereo width
                output_l += delayed_r * gain_r * (0.5 - 0.5 * width) * 0.5
                output_r += delayed_l * gain_l * (0.5 - 0.5 * width) * 0.5
        
        # Apply damping
        output_l = self.damping_filter.process(output_l)
        output_r = self.damping_filter.process(output_r)
        
        # Apply early level
        early_level = self.params['early_level']
        output_l *= early_level
        output_r *= early_level
        
        return output_l, output_r
    
    def process_block(self, input_block: np.ndarray) -> np.ndarray:
        """
        Process a block of audio samples.
        
        Args:
            input_block: Input audio as numpy array (N, 2)
            
        Returns:
            Output audio as numpy array (N, 2)
        """
        num_samples = input_block.shape[0]
        output_block = np.zeros((num_samples, 2), dtype=np.float32)
        
        for i in range(num_samples):
            output_l, output_r = self.process_sample(input_block[i, 0], input_block[i, 1])
            output_block[i, 0] = output_l
            output_block[i, 1] = output_r
        
        return output_block


# Test
if __name__ == "__main__":
    print("Testing EarlyReflections...")
    
    er = EarlyReflections(sample_rate=44100)
    
    # Test with different modes
    for mode in ['1972', '1978', '1987', 'NOW1']:
        print(f"\nMode: {mode}")
        er.set_mode(mode)
        
        test_signal = np.zeros((44100, 2), dtype=np.float32)
        test_signal[0, 0] = 0.5
        test_signal[0, 1] = 0.5
        
        output = er.process_block(test_signal)
        
        print(f'  Output peak: {np.max(np.abs(output)):.6f}')
        print(f'  Output RMS: {np.sqrt(np.mean(output**2)):.6f}')
    
    print('\nEarlyReflections test completed successfully!')

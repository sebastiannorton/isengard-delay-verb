"""
Mode 1977 - Quantec Room Simulator

Based on the Quantec Room Simulator (1977).

Characteristics:
- Room simulation
- Short, dense decay
- Characteristic "room" sound
- Minimal early reflections

Category: Room
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1977(VerbModeBase):
    """
    Quantec Room Simulator (1977).
    
    The Quantec was known for its room simulation capabilities,
    creating short, dense reverberation suitable for room emulation.
    """
    
    name = "1977"
    year = 1977
    description = "Quantec Room Simulator - Short, dense room reverb"
    category = "Room"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.3,        # Short decay for room
        'size': 0.4,         # Small room
        'damping': 0.6,      # More damping for room
        'damping_freq': 7000.0,
        'diffusion': 0.9,    # Very high diffusion for room
        'mod_rate': 0.6,
        'mod_depth': 0.2,
        'pre_delay': 20.0,   # Very short pre-delay
        'early_level': 0.3,  # Less early reflections
        'width': 0.5,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Quantec-specific parameters."""
        self.fdn.comb_delays_ms = [400.0, 500.0, 600.0, 700.0]
        self.fdn.comb_feedbacks = [0.70, 0.72, 0.74, 0.76]
        self.fdn.allpass_delays_ms = [3.0, 5.0]
        self.fdn.allpass_feedbacks = [0.8, 0.85]
        
        self._update_fdn()
        
        # Quantec had minimal early reflections
        self.early_reflections.taps = [
            (10.0, 0.5, 0.4),
            (20.0, 0.4, 0.5),
        ]
    
    def get_name(self) -> str:
        return self.name
    
    def get_year(self) -> int:
        return self.year
    
    def get_description(self) -> str:
        return self.description
    
    def get_category(self) -> str:
        return self.category


# Test
if __name__ == "__main__":
    print("Testing Mode1977 (Quantec)...")
    mode = Mode1977(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1977 test completed successfully!')

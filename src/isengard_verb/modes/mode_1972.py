"""
Mode 1972 - EMT 140 Plate Reverb

Based on the EMT 140 plate reverb (1972).

Characteristics:
- Plate reverb emulation
- Dense, smooth decay
- Limited early reflections
- Characteristic metallic sheen

Category: Plate
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1972(VerbModeBase):
    """
    EMT 140 Plate Reverb (1972).
    
    The EMT 140 was one of the first commercial plate reverbs,
    known for its smooth, dense decay and characteristic sound.
    """
    
    name = "1972"
    year = 1972
    description = "EMT 140 Plate Reverb - Smooth, dense plate reverb with metallic character"
    category = "Plate"
    
    # Mode-specific default parameters
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.6,        # Plate has longer decay
        'size': 0.7,         # Large plate
        'damping': 0.6,      # More damping for plate
        'damping_freq': 8000.0,  # Lower damping frequency
        'diffusion': 0.7,    # High diffusion for plate
        'mod_rate': 0.3,     # Slow modulation
        'mod_depth': 0.15,   # Moderate depth
        'pre_delay': 40.0,   # Shorter pre-delay for plate
        'early_level': 0.4,  # Less early reflections
        'width': 0.6,        # Moderate width
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize EMT 140-specific parameters."""
        # EMT 140 had specific characteristics:
        # - Plate size: ~1.5m x 2m
        # - Decay time: ~3-4 seconds
        # - Diffusion: High
        
        # Configure FDN for plate characteristics
        # Use longer comb delays and higher diffusion
        self.fdn.comb_delays_ms = [1200.0, 1400.0, 1600.0, 1800.0]
        self.fdn.comb_feedbacks = [0.82, 0.84, 0.86, 0.88]
        self.fdn.allpass_delays_ms = [6.0, 8.0]
        self.fdn.allpass_feedbacks = [0.7, 0.75]
        
        # Update FDN with these parameters
        self._update_fdn()
        
        # Configure early reflections for plate
        # EMT 140 had minimal early reflections
        self.early_reflections.taps = [
            (15.0, 0.6, 0.5),   # First reflection
            (30.0, 0.4, 0.6),   # Second reflection
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
    print("Testing Mode1972 (EMT 140 Plate)...")
    
    mode = Mode1972(sample_rate=44100)
    
    # Generate impulse response
    ir = mode.get_impulse_response(duration_seconds=2.0)
    
    print(f'IR shape: {ir.shape}')
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print(f'IR RMS: {np.sqrt(np.mean(ir**2)):.6f}')
    
    print('\nMode1972 test completed successfully!')

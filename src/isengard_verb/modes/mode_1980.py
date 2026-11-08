"""
Mode 1980 - Lexicon 224X

Based on the Lexicon 224X (1980).

Characteristics:
- Enhanced version of Lexicon 224
- More programs and flexibility
- Rich, dense digital reverb
- Improved stereo imaging

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1980(VerbModeBase):
    """
    Lexicon 224X (1980).
    
    The Lexicon 224X was an enhanced version of the classic 224,
    offering more programs and improved sound quality.
    """
    
    name = "1980"
    year = 1980
    description = "Lexicon 224X - Enhanced digital reverb with rich, dense decay and improved stereo"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.65,       # Longer decay than 224
        'size': 0.75,        # Larger space
        'damping': 0.45,
        'damping_freq': 12000.0,
        'diffusion': 0.75,   # Higher diffusion
        'mod_rate': 0.35,
        'mod_depth': 0.12,
        'pre_delay': 70.0,
        'early_level': 0.45,
        'width': 0.75,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Lexicon 224X-specific parameters."""
        # 224X had more complex routing than 224
        self.fdn.comb_delays_ms = [1100.0, 1300.0, 1500.0, 1700.0]
        self.fdn.comb_feedbacks = [0.81, 0.83, 0.85, 0.87]
        self.fdn.allpass_delays_ms = [6.5, 8.5]
        self.fdn.allpass_feedbacks = [0.72, 0.77]
        
        self._update_fdn()
        
        # 224X had more elaborate early reflections
        self.early_reflections.taps = [
            (20.0, 0.55, 0.45),
            (40.0, 0.5, 0.5),
            (60.0, 0.45, 0.55),
            (90.0, 0.4, 0.6),
            (120.0, 0.35, 0.65),
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
    print("Testing Mode1980 (Lexicon 224X)...")
    mode = Mode1980(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR shape: {ir.shape}')
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print(f'IR RMS: {np.sqrt(np.mean(ir**2)):.6f}')
    print('Mode1980 test completed successfully!')

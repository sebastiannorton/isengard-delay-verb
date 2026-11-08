"""
Isengard Verb DSP Components

This package contains the DSP components for the reverb:
- FDN: Feedback Delay Network
- Early Reflections: Tap generation
- Modulation: LFOs and modulation matrix
- Color: Color system (1970s, 1980s, Now)
- Filters: Damping filters, tone controls
"""

from .fdn import FDNReverb
from .early_reflections import EarlyReflections
from .modulation import ModulationMatrix, LFO
from .color import ColorSystem

__all__ = ['FDNReverb', 'EarlyReflections', 'ModulationMatrix', 'LFO', 'ColorSystem']

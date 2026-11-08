"""
Filters for Isengard Verb

Additional filters specific to the reverb:
- Damping filters
- Tone controls
- Air filters
"""

# For now, this is a placeholder that re-exports from shared filters
from isengard_shared.filters import (
    AllpassFilter,
    CombFilter,
    OnePoleFilter,
    BiquadFilter,
)

__all__ = ['AllpassFilter', 'CombFilter', 'OnePoleFilter', 'BiquadFilter']

"""
Isengard Delay Styles

This package contains all delay style implementations:
- SingleStyle: Single delay line per channel
- DualStyle: Two independent delay lines per channel
- RatioStyle: Delay times related by musical ratios
- PingPongStyle: Delays bounce between L/R channels
- QuadStyle: Four delay lines with complex stereo routing
"""

from .single import SingleStyle
from .dual import DualStyle
from .ratio import RatioStyle
from .pingpong import PingPongStyle
from .quad import QuadStyle

__all__ = [
    'SingleStyle',
    'DualStyle',
    'RatioStyle',
    'PingPongStyle',
    'QuadStyle',
]

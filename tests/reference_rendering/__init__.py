# Reference Rendering Framework
# For rendering reference outputs

"""
Reference rendering framework for Isengard plugin testing.

This module provides tools for:
- Rendering reference plugin outputs
- Saving outputs with metadata
- Comparing with implementation

All renderings are:
- Deterministic and reproducible
- Configurable via JSON files
- Integrated with the analysis tools
"""

from .render import ReferenceRenderer

__all__ = [
    'ReferenceRenderer',
]

__version__ = '1.0.0'
__description__ = 'Reference rendering framework for Isengard plugin testing'

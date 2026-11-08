# Parameter Sweep Framework
# For automated parameter testing

"""
Parameter sweep framework for automated testing of Isengard plugins.

This module provides tools for:
- Sweeping parameters through their ranges
- Rendering outputs for each parameter value
- Analyzing and comparing results
- Generating reports

All sweeps are:
- Deterministic and reproducible
- Configurable via JSON files
- Integrated with the analysis tools
"""

from .sweep import ParameterSweep

__all__ = [
    'ParameterSweep',
]

__version__ = '1.0.0'
__description__ = 'Parameter sweep framework for Isengard plugin testing'

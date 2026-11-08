"""
Isengard Delay Modes

This package contains all delay mode implementations:
- TapeMode: Analog tape emulation with wow/flutter
- HiFiMode: Clean high-fidelity delay
- BBDMode: Bucket Brigade Device emulation
- DigitalMode: Digital delay with bit crushing
- GhostMode: Frequency shifting and diffusion
- PitchMode: Pitch shifting in feedback
- RevPitchMode: Reverse delay with pitch shifting
"""

from .tape import TapeMode
from .hifi import HiFiMode
from .bbd import BBDMode
from .digital import DigitalMode
from .ghost import GhostMode
from .pitch import PitchMode
from .revpitch import RevPitchMode

__all__ = [
    "TapeMode",
    "HiFiMode",
    "BBDMode",
    "DigitalMode",
    "GhostMode",
    "PitchMode",
    "RevPitchMode",
]

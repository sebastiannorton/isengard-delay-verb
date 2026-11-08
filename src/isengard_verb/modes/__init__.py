"""
Isengard Verb Modes

This package contains all 22 reverb mode implementations:
- 1970s: 1972 (EMT 140), 1974 (AMS RMX16), 1975 (Eventide SP2016), 1976 (EMT 250), 1977 (Quantec), 1978 (Lexicon 224), 1979
- 1980s: 1980 (Lexicon 224X), 1981 (Yamaha Rev1), 1982, 1983, 1984, 1985 (Lexicon 300), 1986 (Yamaha Rev5), 1987 (Lexicon 480L)
- 1990s: 1990 (Lexicon PCM70), 1991 (Yamaha Rev7), 1992 (Eventide H3000), 1993 (TC Electronic M3000), 1994 (Lexicon PCM80), 1995 (Yamaha SPX90)
- NOW: NOW1, NOW2

Each mode has unique FDN parameters and early reflection patterns.
"""

# Import all modes
from .base import VerbModeBase
from .mode_1972 import Mode1972
from .mode_1974 import Mode1974
from .mode_1975 import Mode1975
from .mode_1976 import Mode1976
from .mode_1977 import Mode1977
from .mode_1978 import Mode1978
from .mode_1979 import Mode1979
from .mode_1980 import Mode1980
from .mode_1981 import Mode1981
from .mode_1982 import Mode1982
from .mode_1983 import Mode1983
from .mode_1984 import Mode1984
from .mode_1985 import Mode1985
from .mode_1986 import Mode1986
from .mode_1987 import Mode1987
from .mode_1990 import Mode1990
from .mode_1991 import Mode1991
from .mode_1992 import Mode1992
from .mode_1993 import Mode1993
from .mode_1994 import Mode1994
from .mode_1995 import Mode1995
from .mode_now1 import ModeNOW1
from .mode_now2 import ModeNOW2

__all__ = [
    'VerbModeBase',
    'Mode1972', 'Mode1974', 'Mode1975', 'Mode1976', 'Mode1977', 'Mode1978', 'Mode1979',
    'Mode1980', 'Mode1981', 'Mode1982', 'Mode1983', 'Mode1984', 'Mode1985', 'Mode1986', 'Mode1987',
    'Mode1990', 'Mode1991', 'Mode1992', 'Mode1993', 'Mode1994', 'Mode1995',
    'ModeNOW1', 'ModeNOW2',
]

# Mode registry for easy lookup
MODE_REGISTRY = {
    '1972': Mode1972,
    '1974': Mode1974,
    '1975': Mode1975,
    '1976': Mode1976,
    '1977': Mode1977,
    '1978': Mode1978,
    '1979': Mode1979,
    '1980': Mode1980,
    '1981': Mode1981,
    '1982': Mode1982,
    '1983': Mode1983,
    '1984': Mode1984,
    '1985': Mode1985,
    '1986': Mode1986,
    '1987': Mode1987,
    '1990': Mode1990,
    '1991': Mode1991,
    '1992': Mode1992,
    '1993': Mode1993,
    '1994': Mode1994,
    '1995': Mode1995,
    'NOW1': ModeNOW1,
    'NOW2': ModeNOW2,
}

def get_mode(mode_name: str, sample_rate: int = 44100):
    """Get a mode instance by name."""
    if mode_name in MODE_REGISTRY:
        return MODE_REGISTRY[mode_name](sample_rate)
    else:
        raise ValueError(f"Unknown mode: {mode_name}")

def list_modes() -> list:
    """List all available mode names."""
    return list(MODE_REGISTRY.keys())

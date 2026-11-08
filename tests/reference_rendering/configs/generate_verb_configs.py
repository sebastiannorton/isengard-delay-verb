#!/usr/bin/env python3
"""
Generate test configurations for all 22 ValhallaVintageVerb modes.

This script creates comprehensive test configurations for each mode
with all three color settings (1970s, 1980s, Now).
"""

import json
import os

# All 22 VintageVerb modes
VERB_MODES = [
    # 1970s modes
    "1972",   # EMT 140 plate
    "1974",   # AMS RMX16
    "1975",   # Eventide SP2016
    "1976",   # EMT 250
    "1977",   # Quantec Room Simulator
    "1978",   # Lexicon 224
    "1979",   # AMS RMX16 (alternate)
    
    # 1980s modes
    "1980",   # Lexicon 224X
    "1981",   # Yamaha Rev1
    "1982",   # AMS RMX16 (variant)
    "1983",   # EMT 250 (variant)
    "1984",   # Quantec (variant)
    "1985",   # Lexicon 300
    "1986",   # Yamaha Rev5
    "1987",   # Lexicon 480L
    
    # 1990s/2000s modes
    "1990",   # Lexicon PCM70
    "1991",   # Yamaha Rev7
    "1992",   # Eventide H3000
    "1993",   # TC Electronic M3000
    "1994",   # Lexicon PCM80
    "1995",   # Yamaha SPX90
    "NOW1",   # Modern algorithm 1
    "NOW2",   # Modern algorithm 2
]

# Color settings
COLORS = ["1970s", "1980s", "Now"]

# Signal types to use for different modes
SIGNAL_TYPES = {
    "plate": ["impulse", "white"],
    "hall": ["impulse", "white"],
    "room": ["impulse", "pink"],
    "ambience": ["impulse", "sine"],
}

# Mode categories (for determining signal type)
MODE_CATEGORIES = {
    "1972": "plate",      # EMT 140
    "1974": "plate",      # AMS RMX16
    "1975": "room",       # Eventide SP2016
    "1976": "hall",       # EMT 250
    "1977": "room",       # Quantec
    "1978": "hall",       # Lexicon 224
    "1979": "room",
    "1980": "hall",       # Lexicon 224X
    "1981": "hall",       # Yamaha Rev1
    "1982": "room",
    "1983": "hall",
    "1984": "room",
    "1985": "hall",       # Lexicon 300
    "1986": "hall",       # Yamaha Rev5
    "1987": "hall",       # Lexicon 480L
    "1990": "hall",       # Lexicon PCM70
    "1991": "hall",       # Yamaha Rev7
    "1992": "room",       # Eventide H3000
    "1993": "room",       # TC Electronic M3000
    "1994": "hall",       # Lexicon PCM80
    "1995": "room",       # Yamaha SPX90
    "NOW1": "hall",
    "NOW2": "ambience",
}

# Default parameters for verb
DEFAULT_VERB_PARAMS = {
    "mix": 1.0,
    "predelay": 50.0,
    "decay": 0.5,
    "size": 0.5,
    "attack": 0.0,
    "bassMult": 1.0,
    "bassXover": 200.0,
    "highCut": 10000.0,
    "damping": 0.5,
    "dampingFreq": 10000.0,
    "modRate": 0.5,
    "modDepth": 0.3,
    "earlyLateBalance": 0.5,
    "width": 0.5,
    "inputGain": 0.0,
    "outputGain": 0.0
}

# Mode-specific parameter overrides
MODE_PARAMS = {
    "1972": {"decay": 0.6, "modDepth": 0.2},  # EMT 140 - longer decay, subtle modulation
    "1974": {"decay": 0.5, "modRate": 0.3},   # AMS RMX16
    "1976": {"decay": 0.7, "size": 0.6},      # EMT 250 - larger
    "1978": {"decay": 0.5, "modDepth": 0.4},  # Lexicon 224 - more modulation
    "1980": {"decay": 0.55, "modRate": 0.6},  # Lexicon 224X
    "1985": {"decay": 0.6, "size": 0.6},      # Lexicon 300
    "1987": {"decay": 0.7, "size": 0.7},      # Lexicon 480L - largest
    "1990": {"decay": 0.5, "modDepth": 0.5},  # PCM70
    "1992": {"decay": 0.4, "modRate": 1.0},   # H3000 - fast modulation
    "1995": {"decay": 0.45, "size": 0.4},     # SPX90 - smaller
    "NOW1": {"decay": 0.6, "modDepth": 0.3},
    "NOW2": {"decay": 0.5, "modRate": 0.8},
}

# Color-specific parameter overrides
COLOR_PARAMS = {
    "1970s": {"highCut": 8000.0, "damping": 0.6},  # Darker, more damping
    "1980s": {"highCut": 12000.0, "damping": 0.5}, # Brighter
    "Now": {"highCut": 15000.0, "damping": 0.4},    # Brightest, least damping
}


def generate_verb_config(mode, color, signal_type="impulse"):
    """Generate a single verb mode configuration."""
    
    category = MODE_CATEGORIES.get(mode, "hall")
    
    # Build parameters
    params = DEFAULT_VERB_PARAMS.copy()
    
    # Apply mode-specific overrides
    if mode in MODE_PARAMS:
        params.update(MODE_PARAMS[mode])
    
    # Apply color-specific overrides
    if color in COLOR_PARAMS:
        params.update(COLOR_PARAMS[color])
    
    # Determine duration based on decay
    decay = params.get("decay", 0.5)
    duration = max(4.0, min(12.0, 4.0 + decay * 8.0))
    
    config = {
        "name": f"Verb {mode} Mode - {color} Color - {signal_type.capitalize()} Signal",
        "description": f"Reference rendering for {mode} mode with {color} color using {signal_type} signal.",
        "plugin": "verb",
        "mode": mode,
        "color": color,
        "parameters": params,
        "signal": {
            "type": signal_type,
            "position": 0,
            "amplitude": 0.5
        },
        "sample_rate": 44100,
        "duration_seconds": duration,
        "block_size": 1024,
        "notes": f"{mode} mode emulation with {color} color. Category: {category}. Duration adjusted for decay time."
    }
    
    return config


def main():
    """Generate all verb mode configurations."""
    
    # Create directories
    base_dir = "/workspace/isengard-project/tests/reference_rendering/configs"
    verb_dir = os.path.join(base_dir, "verb-modes")
    param_sweep_dir = os.path.join(base_dir, "parameter-sweeps")
    
    os.makedirs(verb_dir, exist_ok=True)
    os.makedirs(param_sweep_dir, exist_ok=True)
    
    # Generate verb mode configurations
    print("Generating verb mode configurations...")
    count = 0
    existing_files = set()
    
    # Check existing files
    if os.path.exists(verb_dir):
        for f in os.listdir(verb_dir):
            if f.endswith('.json'):
                existing_files.add(f)
    
    for mode in VERB_MODES:
        for color in COLORS:
            # Create impulse config (always)
            config = generate_verb_config(mode, color, "impulse")
            filename = f"{mode}-{color}-impulse.json"
            
            if filename not in existing_files:
                filepath = os.path.join(verb_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(config, f, indent=2)
                count += 1
                print(f"  Created: {filename}")
            else:
                print(f"  Skipped (exists): {filename}")
            
            # Create white noise config for halls and plates
            category = MODE_CATEGORIES.get(mode, "hall")
            if category in ["hall", "plate"]:
                config = generate_verb_config(mode, color, "white")
                filename = f"{mode}-{color}-white-noise.json"
                
                if filename not in existing_files:
                    filepath = os.path.join(verb_dir, filename)
                    with open(filepath, 'w') as f:
                        json.dump(config, f, indent=2)
                    count += 1
                    print(f"  Created: {filename}")
                else:
                    print(f"  Skipped (exists): {filename}")
    
    print(f"\nGenerated {count} verb mode configurations")
    
    # Generate parameter sweep configurations
    print("\nGenerating parameter sweep configurations...")
    
    # Verb parameter sweeps
    verb_param_sweeps = [
        {
            "name": "Verb Decay Sweep",
            "description": "Sweep decay parameter from 0.1 to 0.9",
            "plugin": "verb",
            "mode": "1978",
            "color": "1980s",
            "parameter": "decay",
            "range": [0.1, 0.9],
            "steps": 17,
            "scale": "linear",
            "signal_type": "impulse",
            "sample_rate": 44100,
            "duration_seconds": 6.0,
            "base_params": {
                "mix": 1.0,
                "predelay": 50.0,
                "size": 0.5,
                "attack": 0.0,
                "bassMult": 1.0,
                "highCut": 10000.0,
                "damping": 0.5,
                "modRate": 0.5,
                "modDepth": 0.3
            },
            "notes": "Test how decay affects reverb tail length"
        },
        {
            "name": "Verb Size Sweep",
            "description": "Sweep size parameter from 0.1 to 0.9",
            "plugin": "verb",
            "mode": "1978",
            "color": "1980s",
            "parameter": "size",
            "range": [0.1, 0.9],
            "steps": 17,
            "scale": "linear",
            "signal_type": "impulse",
            "sample_rate": 44100,
            "duration_seconds": 5.0,
            "base_params": {
                "mix": 1.0,
                "predelay": 50.0,
                "decay": 0.5,
                "attack": 0.0,
                "bassMult": 1.0,
                "highCut": 10000.0,
                "damping": 0.5,
                "modRate": 0.5,
                "modDepth": 0.3
            },
            "notes": "Test how size affects reverb density and spacing"
        },
        {
            "name": "Verb Mod Depth Sweep",
            "description": "Sweep modDepth parameter from 0.0 to 1.0",
            "plugin": "verb",
            "mode": "1978",
            "color": "1980s",
            "parameter": "modDepth",
            "range": [0.0, 1.0],
            "steps": 21,
            "scale": "linear",
            "signal_type": "white",
            "sample_rate": 44100,
            "duration_seconds": 5.0,
            "base_params": {
                "mix": 1.0,
                "predelay": 50.0,
                "decay": 0.5,
                "size": 0.5,
                "attack": 0.0,
                "bassMult": 1.0,
                "highCut": 10000.0,
                "damping": 0.5,
                "modRate": 0.5
            },
            "notes": "Test how modulation depth affects spectral characteristics"
        },
        {
            "name": "Verb High Cut Sweep",
            "description": "Sweep highCut parameter from 1000 to 15000 Hz",
            "plugin": "verb",
            "mode": "1978",
            "color": "Now",
            "parameter": "highCut",
            "range": [1000.0, 15000.0],
            "steps": 15,
            "scale": "logarithmic",
            "signal_type": "white",
            "sample_rate": 44100,
            "duration_seconds": 5.0,
            "base_params": {
                "mix": 1.0,
                "predelay": 50.0,
                "decay": 0.5,
                "size": 0.5,
                "attack": 0.0,
                "bassMult": 1.0,
                "damping": 0.5,
                "modRate": 0.5,
                "modDepth": 0.3
            },
            "notes": "Test frequency-dependent damping"
        },
        {
            "name": "Verb Damping Sweep",
            "description": "Sweep damping parameter from 0.0 to 1.0",
            "plugin": "verb",
            "mode": "1978",
            "color": "1980s",
            "parameter": "damping",
            "range": [0.0, 1.0],
            "steps": 21,
            "scale": "linear",
            "signal_type": "white",
            "sample_rate": 44100,
            "duration_seconds": 5.0,
            "base_params": {
                "mix": 1.0,
                "predelay": 50.0,
                "decay": 0.5,
                "size": 0.5,
                "attack": 0.0,
                "bassMult": 1.0,
                "highCut": 10000.0,
                "modRate": 0.5,
                "modDepth": 0.3
            },
            "notes": "Test high-frequency damping"
        }
    ]
    
    # Delay parameter sweeps
    delay_param_sweeps = [
        {
            "name": "Delay Feedback Sweep",
            "description": "Sweep feedback parameter from 0.0 to 0.95",
            "plugin": "delay",
            "mode": "Tape",
            "style": "Single",
            "parameter": "feedback",
            "range": [0.0, 0.95],
            "steps": 20,
            "scale": "linear",
            "signal_type": "impulse",
            "sample_rate": 44100,
            "duration_seconds": 5.0,
            "base_params": {
                "mix": 1.0,
                "delayTimeMs": 500.0,
                "modRate": 1.0,
                "modDepth": 0.3,
                "drive": 0.5
            },
            "notes": "Test feedback stability and echo decay"
        },
        {
            "name": "Delay Time Sweep",
            "description": "Sweep delayTimeMs from 50ms to 1000ms",
            "plugin": "delay",
            "mode": "Digital",
            "style": "Single",
            "parameter": "delayTimeMs",
            "range": [50.0, 1000.0],
            "steps": 20,
            "scale": "logarithmic",
            "signal_type": "impulse",
            "sample_rate": 44100,
            "duration_seconds": 3.0,
            "base_params": {
                "mix": 1.0,
                "feedback": 0.5,
                "modRate": 0.0,
                "modDepth": 0.0
            },
            "notes": "Test delay time accuracy and interpolation"
        },
        {
            "name": "Delay Mod Depth Sweep",
            "description": "Sweep modDepth from 0.0 to 1.0",
            "plugin": "delay",
            "mode": "Tape",
            "style": "Single",
            "parameter": "modDepth",
            "range": [0.0, 1.0],
            "steps": 21,
            "scale": "linear",
            "signal_type": "sine",
            "sample_rate": 44100,
            "duration_seconds": 3.0,
            "base_params": {
                "mix": 1.0,
                "feedback": 0.5,
                "delayTimeMs": 500.0,
                "modRate": 1.0,
                "drive": 0.5
            },
            "notes": "Test modulation depth effect on pitch variation"
        },
        {
            "name": "Delay Age Sweep (Digital Mode)",
            "description": "Sweep age parameter from 0.0 to 1.0 in Digital mode",
            "plugin": "delay",
            "mode": "Digital",
            "style": "Single",
            "parameter": "age",
            "range": [0.0, 1.0],
            "steps": 21,
            "scale": "linear",
            "signal_type": "sine",
            "sample_rate": 44100,
            "duration_seconds": 3.0,
            "base_params": {
                "mix": 1.0,
                "feedback": 0.5,
                "delayTimeMs": 500.0,
                "modRate": 0.0,
                "modDepth": 0.0
            },
            "notes": "Test bit crushing effect (50% = 12-bit)"
        },
        {
            "name": "Delay Diffusion Amount Sweep",
            "description": "Sweep diffusionAmount from 0.0 to 1.0",
            "plugin": "delay",
            "mode": "Tape",
            "style": "Single",
            "parameter": "diffusionAmount",
            "range": [0.0, 1.0],
            "steps": 21,
            "scale": "linear",
            "signal_type": "white",
            "sample_rate": 44100,
            "duration_seconds": 5.0,
            "base_params": {
                "mix": 1.0,
                "feedback": 0.7,
                "delayTimeMs": 500.0,
                "modRate": 1.0,
                "modDepth": 0.3,
                "diffusionSize": 0.5
            },
            "notes": "Test diffusion network effect on echo density"
        }
    ]
    
    # Save parameter sweep configurations
    all_sweeps = verb_param_sweeps + delay_param_sweeps
    
    existing_sweeps = set()
    if os.path.exists(param_sweep_dir):
        for f in os.listdir(param_sweep_dir):
            if f.endswith('.json'):
                existing_sweeps.add(f)
    
    sweep_count = 0
    for sweep in all_sweeps:
        # Create filename
        plugin = sweep["plugin"]
        param = sweep["parameter"]
        mode = sweep.get("mode", "")
        style = sweep.get("style", "")
        color = sweep.get("color", "")
        
        parts = [plugin, param]
        if mode:
            parts.append(mode)
        if style:
            parts.append(style)
        if color:
            parts.append(color)
        
        filename = '-'.join(parts).lower() + "-sweep.json"
        
        if filename not in existing_sweeps:
            filepath = os.path.join(param_sweep_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(sweep, f, indent=2)
            sweep_count += 1
            print(f"  Created: {filename}")
        else:
            print(f"  Skipped (exists): {filename}")
    
    print(f"\nGenerated {sweep_count} parameter sweep configurations")
    print(f"\nTotal configurations created: {count + sweep_count}")


if __name__ == "__main__":
    main()

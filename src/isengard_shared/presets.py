"""
Preset Management System

This module provides preset management for Isengard plugins.

Features:
- Save/load presets to/from JSON files
- Factory presets for both plugins
- Preset validation
- DAW project recall support
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class Preset:
    """
    A single preset for Isengard Delay or Verb.
    
    Attributes:
        name: Preset name
        plugin: 'delay' or 'verb'
        parameters: Dictionary of parameter values
        metadata: Additional metadata (author, date, description, etc.)
    """
    
    def __init__(
        self,
        name: str,
        plugin: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a preset.
        
        Args:
            name: Preset name
            plugin: 'delay' or 'verb'
            parameters: Dictionary of parameter values
            metadata: Optional metadata dictionary
        """
        self.name = name
        self.plugin = plugin.lower()
        self.parameters = parameters.copy()
        self.metadata = metadata or {}
        
        # Set default metadata
        if 'author' not in self.metadata:
            self.metadata['author'] = 'Isengard'
        if 'date' not in self.metadata:
            self.metadata['date'] = datetime.now().isoformat()
        if 'version' not in self.metadata:
            self.metadata['version'] = '1.0'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preset to dictionary."""
        return {
            'name': self.name,
            'plugin': self.plugin,
            'parameters': self.parameters,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Preset':
        """Create preset from dictionary."""
        return cls(
            name=data.get('name', 'Unnamed'),
            plugin=data.get('plugin', 'unknown'),
            parameters=data.get('parameters', {}),
            metadata=data.get('metadata', {})
        )
    
    def save(self, path: str):
        """
        Save preset to a JSON file.
        
        Args:
            path: File path (should end with .json)
        """
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'Preset':
        """
        Load preset from a JSON file.
        
        Args:
            path: File path
            
        Returns:
            Preset instance
        """
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        return f"Preset(name='{self.name}', plugin='{self.plugin}')"


class PresetManager:
    """
    Manages presets for Isengard plugins.
    
    Features:
    - Save/load presets
    - Organize presets by plugin
    - Factory presets
    - User presets
    """
    
    # Default preset directories
    DEFAULT_PRESET_DIR = 'presets'
    DELAY_PRESET_DIR = 'presets/delay'
    VERB_PRESET_DIR = 'presets/verb'
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize preset manager.
        
        Args:
            base_dir: Base directory for presets (defaults to current directory)
        """
        self.base_dir = Path(base_dir or '.')
        self.presets: Dict[str, List[Preset]] = {
            'delay': [],
            'verb': [],
        }
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure preset directories exist."""
        (self.base_dir / self.DELAY_PRESET_DIR).mkdir(parents=True, exist_ok=True)
        (self.base_dir / self.VERB_PRESET_DIR).mkdir(parents=True, exist_ok=True)
    
    def save_preset(self, preset: Preset) -> str:
        """
        Save a preset to disk.
        
        Args:
            preset: Preset to save
            
        Returns:
            Path to the saved preset file
        """
        # Determine directory based on plugin type
        if preset.plugin == 'delay':
            dir_path = self.base_dir / self.DELAY_PRESET_DIR
        else:
            dir_path = self.base_dir / self.VERB_PRESET_DIR
        
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create filename
        filename = f"{preset.name}.json"
        # Sanitize filename
        filename = ''.join(c for c in filename if c.isalnum() or c in ('-', '_', '.', ' '))
        filename = filename.strip().replace(' ', '_')
        
        filepath = dir_path / filename
        
        # Add counter if file exists
        counter = 1
        while filepath.exists():
            filepath = dir_path / f"{preset.name}_{counter}.json"
            counter += 1
        
        preset.save(str(filepath))
        
        # Add to memory
        self.presets[preset.plugin].append(preset)
        
        return str(filepath)
    
    def load_preset(self, path: str) -> Preset:
        """
        Load a preset from disk.
        
        Args:
            path: Path to preset file
            
        Returns:
            Preset instance
        """
        preset = Preset.load(path)
        
        # Add to memory
        self.presets[preset.plugin].append(preset)
        
        return preset
    
    def load_all_presets(self):
        """Load all presets from disk."""
        # Load delay presets
        delay_dir = self.base_dir / self.DELAY_PRESET_DIR
        if delay_dir.exists():
            for filepath in delay_dir.glob('*.json'):
                try:
                    preset = Preset.load(str(filepath))
                    self.presets['delay'].append(preset)
                except Exception as e:
                    print(f"Warning: Could not load {filepath}: {e}")
        
        # Load verb presets
        verb_dir = self.base_dir / self.VERB_PRESET_DIR
        if verb_dir.exists():
            for filepath in verb_dir.glob('*.json'):
                try:
                    preset = Preset.load(str(filepath))
                    self.presets['verb'].append(preset)
                except Exception as e:
                    print(f"Warning: Could not load {filepath}: {e}")
    
    def get_preset(self, plugin: str, name: str) -> Optional[Preset]:
        """
        Get a preset by name.
        
        Args:
            plugin: 'delay' or 'verb'
            name: Preset name
            
        Returns:
            Preset instance or None if not found
        """
        for preset in self.presets.get(plugin, []):
            if preset.name == name:
                return preset
        return None
    
    def list_presets(self, plugin: str) -> List[str]:
        """
        List all preset names for a plugin.
        
        Args:
            plugin: 'delay' or 'verb'
            
        Returns:
            List of preset names
        """
        return [p.name for p in self.presets.get(plugin, [])]
    
    def delete_preset(self, plugin: str, name: str) -> bool:
        """
        Delete a preset.
        
        Args:
            plugin: 'delay' or 'verb'
            name: Preset name
            
        Returns:
            True if deleted, False if not found
        """
        # Find and remove from memory
        presets = self.presets.get(plugin, [])
        for i, preset in enumerate(presets):
            if preset.name == name:
                del presets[i]
                
                # Delete from disk
                if preset.plugin == 'delay':
                    dir_path = self.base_dir / self.DELAY_PRESET_DIR
                else:
                    dir_path = self.base_dir / self.VERB_PRESET_DIR
                
                for filepath in dir_path.glob('*.json'):
                    try:
                        loaded = Preset.load(str(filepath))
                        if loaded.name == name:
                            os.remove(str(filepath))
                            return True
                    except:
                        pass
                
                return True
        
        return False
    
    def create_factory_presets(self):
        """Create factory presets for both plugins."""
        
        # Delay factory presets
        delay_presets = [
            Preset(
                name='Tape Slap',
                plugin='delay',
                parameters={
                    'mode': 'tape',
                    'style': 'single',
                    'delay_time_ms': 150,
                    'feedback': 0.3,
                    'mod_rate': 0.8,
                    'mod_depth': 0.2,
                    'mix': 0.4,
                    'drive': 0.2,
                },
                metadata={'author': 'Isengard', 'category': 'Tape'}
            ),
            Preset(
                name='HiFi Echo',
                plugin='delay',
                parameters={
                    'mode': 'hifi',
                    'style': 'dual',
                    'delay_time_ms': 300,
                    'delay_time_l_ms': 300,
                    'delay_time_r_ms': 350,
                    'feedback': 0.5,
                    'mod_rate': 0.3,
                    'mod_depth': 0.1,
                    'mix': 0.5,
                },
                metadata={'author': 'Isengard', 'category': 'Clean'}
            ),
            Preset(
                name='BBD Chorus',
                plugin='delay',
                parameters={
                    'mode': 'bbd',
                    'style': 'pingpong',
                    'delay_time_ms': 200,
                    'feedback': 0.4,
                    'mod_rate': 1.5,
                    'mod_depth': 0.3,
                    'age': 0.5,
                    'mix': 0.6,
                },
                metadata={'author': 'Isengard', 'category': 'Modulation'}
            ),
            Preset(
                name='Digital Delay',
                plugin='delay',
                parameters={
                    'mode': 'digital',
                    'style': 'ratio',
                    'delay_time_ms': 500,
                    'feedback': 0.6,
                    'age': 0.0,
                    'mix': 0.5,
                },
                metadata={'author': 'Isengard', 'category': 'Clean'}
            ),
            Preset(
                name='Ghost Shift',
                plugin='delay',
                parameters={
                    'mode': 'ghost',
                    'style': 'quad',
                    'delay_time_ms': 400,
                    'feedback': 0.5,
                    'frequency_shift': 0.1,
                    'era': 0.7,
                    'mix': 0.5,
                },
                metadata={'author': 'Isengard', 'category': 'Special'}
            ),
        ]
        
        # Verb factory presets
        verb_presets = [
            Preset(
                name='1970s Plate',
                plugin='verb',
                parameters={
                    'mode': '1972',
                    'color': '1970s',
                    'decay': 0.7,
                    'size': 0.8,
                    'damping': 0.6,
                    'mix': 0.4,
                },
                metadata={'author': 'Isengard', 'category': 'Plate'}
            ),
            Preset(
                name='1980s Hall',
                plugin='verb',
                parameters={
                    'mode': '1978',
                    'color': '1980s',
                    'decay': 0.6,
                    'size': 0.7,
                    'damping': 0.5,
                    'mix': 0.5,
                },
                metadata={'author': 'Isengard', 'category': 'Hall'}
            ),
            Preset(
                name='Lexicon 480L',
                plugin='verb',
                parameters={
                    'mode': '1987',
                    'color': '1980s',
                    'decay': 0.7,
                    'size': 0.8,
                    'diffusion': 0.8,
                    'mix': 0.45,
                },
                metadata={'author': 'Isengard', 'category': 'Hall'}
            ),
            Preset(
                name='Modern Ambience',
                plugin='verb',
                parameters={
                    'mode': 'NOW1',
                    'color': 'Now',
                    'decay': 0.6,
                    'size': 0.75,
                    'damping': 0.3,
                    'diffusion': 0.9,
                    'mix': 0.4,
                },
                metadata={'author': 'Isengard', 'category': 'Modern'}
            ),
            Preset(
                name='Eventide H3000',
                plugin='verb',
                parameters={
                    'mode': '1992',
                    'color': 'Now',
                    'decay': 0.65,
                    'size': 0.8,
                    'mod_rate': 0.25,
                    'mod_depth': 0.2,
                    'mix': 0.5,
                },
                metadata={'author': 'Isengard', 'category': 'Ambience'}
            ),
        ]
        
        # Save all factory presets
        for preset in delay_presets + verb_presets:
            self.save_preset(preset)
        
        return len(delay_presets) + len(verb_presets)


# Factory preset data for easy access
FACTORY_PRESETS_DELAY = [
    {
        'name': 'Tape Slap',
        'parameters': {
            'mode': 'tape', 'style': 'single', 'delay_time_ms': 150,
            'feedback': 0.3, 'mod_rate': 0.8, 'mod_depth': 0.2, 'mix': 0.4, 'drive': 0.2
        }
    },
    {
        'name': 'HiFi Echo',
        'parameters': {
            'mode': 'hifi', 'style': 'dual', 'delay_time_ms': 300,
            'delay_time_l_ms': 300, 'delay_time_r_ms': 350, 'feedback': 0.5,
            'mod_rate': 0.3, 'mod_depth': 0.1, 'mix': 0.5
        }
    },
    {
        'name': 'BBD Chorus',
        'parameters': {
            'mode': 'bbd', 'style': 'pingpong', 'delay_time_ms': 200,
            'feedback': 0.4, 'mod_rate': 1.5, 'mod_depth': 0.3, 'age': 0.5, 'mix': 0.6
        }
    },
    {
        'name': 'Digital Delay',
        'parameters': {
            'mode': 'digital', 'style': 'ratio', 'delay_time_ms': 500,
            'feedback': 0.6, 'age': 0.0, 'mix': 0.5
        }
    },
    {
        'name': 'Ghost Shift',
        'parameters': {
            'mode': 'ghost', 'style': 'quad', 'delay_time_ms': 400,
            'feedback': 0.5, 'frequency_shift': 0.1, 'era': 0.7, 'mix': 0.5
        }
    },
]

FACTORY_PRESETS_VERB = [
    {
        'name': '1970s Plate',
        'parameters': {
            'mode': '1972', 'color': '1970s', 'decay': 0.7, 'size': 0.8,
            'damping': 0.6, 'mix': 0.4
        }
    },
    {
        'name': '1980s Hall',
        'parameters': {
            'mode': '1978', 'color': '1980s', 'decay': 0.6, 'size': 0.7,
            'damping': 0.5, 'mix': 0.5
        }
    },
    {
        'name': 'Lexicon 480L',
        'parameters': {
            'mode': '1987', 'color': '1980s', 'decay': 0.7, 'size': 0.8,
            'diffusion': 0.8, 'mix': 0.45
        }
    },
    {
        'name': 'Modern Ambience',
        'parameters': {
            'mode': 'NOW1', 'color': 'Now', 'decay': 0.6, 'size': 0.75,
            'damping': 0.3, 'diffusion': 0.9, 'mix': 0.4
        }
    },
    {
        'name': 'Eventide H3000',
        'parameters': {
            'mode': '1992', 'color': 'Now', 'decay': 0.65, 'size': 0.8,
            'mod_rate': 0.25, 'mod_depth': 0.2, 'mix': 0.5
        }
    },
]


# Test
if __name__ == "__main__":
    print("Testing Preset Management...")
    
    # Create preset manager
    manager = PresetManager(base_dir='./test_presets')
    
    # Create and save a test preset
    preset = Preset(
        name='Test Preset',
        plugin='verb',
        parameters={'mode': '1978', 'decay': 0.7, 'mix': 0.5},
        metadata={'author': 'Test', 'description': 'A test preset'}
    )
    
    filepath = manager.save_preset(preset)
    print(f"Saved preset to: {filepath}")
    
    # Load the preset
    loaded = manager.load_preset(filepath)
    print(f"Loaded preset: {loaded}")
    print(f"  Parameters: {loaded.parameters}")
    
    # List presets
    print(f"\nVerb presets: {manager.list_presets('verb')}")
    
    # Create factory presets
    num_created = manager.create_factory_presets()
    print(f"\nCreated {num_created} factory presets")
    
    # Cleanup test directory
    import shutil
    if os.path.exists('./test_presets'):
        shutil.rmtree('./test_presets')
    
    print('\nPreset management test completed successfully!')

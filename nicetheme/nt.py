"""
NiceTheme API Module

This module provides a NiceGUI-inspired API for creating themed components.
Import this module as 'nt' to access all NiceTheme components:

    from nicetheme import nt
    
    # Optional: Initialize with custom theme directories
    nt.initialize(themes_dirs=['path/to/my/themes'])
    
    nt.button('Click me', variant='primary')
    nt.select(['A', 'B', 'C'])
    nt.icon('home')
"""
from typing import List, Optional
from pathlib import Path

# ... (Global state)
_manager = None
_bridge = None

def initialize(themes_dirs: Optional[List[Path]] = None):
    """Initializes the NiceTheme system with optional custom theme directories."""
    global _manager, _bridge
    if _manager is None:
        _manager = ThemeManager(themes_dirs=themes_dirs)
        # Registry is initialized within Manager
        _bridge = ThemeBridge(_manager, _manager._registry)
    return _manager

# Import atomic components
from .components.atoms import (
    button,
    select_button,
    icon,
    palette_icon,
    select,
    slider,
    tab,
    toggle,
    dangerous_button,
)

# Import molecular components
from .components.molecules import theme_config, histogram, header
from .components.organisms import terminal

# Import core utilities (for convenience)
from .core import ThemeManager, ThemeBridge, ThemeRegistry

__all__ = [
    # Atomic components
    'button',
    'select_button',
    'dangerous_button',
    'icon',
    'palette_icon',
    'select',
    'slider',
    'tab',
    'toggle',
    # Molecular components
    'theme_config',
    'histogram',
    'header',
    # Organisms
    'terminal',
    # Core utilities
    'ThemeManager',
    'ThemeBridge',
    'ThemeRegistry',
]

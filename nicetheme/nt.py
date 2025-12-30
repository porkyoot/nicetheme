"""
NiceTheme API Module

This module provides a NiceGUI-inspired API for creating themed components.
Import this module as 'nt' to access all NiceTheme components:

    from nicetheme import nt
    
    nt.button('Click me', variant='primary')
    nt.select(['A', 'B', 'C'])
    nt.icon('home')
"""

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
)

# Import molecular components
from .components.molecules import theme_config

# Import core utilities (for convenience)
from .core import ThemeManager, ThemeBridge, ThemeRegistry

__all__ = [
    # Atomic components
    'button',
    'select_button',
    'icon',
    'palette_icon',
    'select',
    'slider',
    'tab',
    'toggle',
    # Molecular components
    'theme_config',
    # Core utilities
    'ThemeManager',
    'ThemeBridge',
    'ThemeRegistry',
]

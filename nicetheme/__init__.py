"""
NiceTheme - A powerful theming engine for NiceGUI

This package provides advanced theming capabilities for NiceGUI applications,
including support for palettes, textures, layouts, and typography.

Basic usage:
    from nicetheme import nt
    
    nt.button('Click me', variant='primary')
    nt.select(['Option 1', 'Option 2'])
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# Import the main API module
from . import nt

# Import core utilities for advanced usage
from .core import (
    ThemeManager,
    ThemeBridge,
    ThemeRegistry,
    Theme,
    Palette,
    Texture,
    Layout,
    Typography,
)

__all__ = [
    'nt',
    'ThemeManager',
    'ThemeBridge',
    'ThemeRegistry',
    'Theme',
    'Palette',
    'Texture',
    'Layout',
    'Typography',
]

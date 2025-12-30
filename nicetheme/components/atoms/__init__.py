"""
NiceTheme Atomic Components

Basic, reusable UI components with theme support.
"""

from .button import button, select_button
from .icon import palette_icon
from .select import select
from .slider import slider
from .tab import tab
from .toggle import toggle

# Try to import icon if it exists as a component class
try:
    from .icon import icon
except ImportError:
    # If icon is not a class in icon.py, we'll just have palette_icon
    icon = None

__all__ = [
    'button',
    'select_button',
    'palette_icon',
    'select',
    'slider',
    'tab',
    'toggle',
]

# Only add icon to __all__ if it exists
if icon is not None:
    __all__.append('icon')

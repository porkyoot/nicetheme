#!/usr/bin/env python3
"""
Test script to verify NiceTheme package API

This script demonstrates the new NiceGUI-inspired API for NiceTheme.
Run this in another project after installing NiceTheme.

Installation:
    pip install /path/to/NiceTheme

Usage:
    python test_nicetheme_api.py
"""

from nicegui import ui
from nicetheme import nt

# Example 1: Using nt.button
with ui.page('/'):
    ui.label('NiceTheme API Test').classes('text-2xl font-bold mb-4')
    
    # Test button component
    nt.button('Primary Button', variant='primary')
    nt.button('Secondary Button', variant='secondary')
    nt.button('Ghost Button', variant='ghost')
    
    # Test select component
    nt.select(['Option A', 'Option B', 'Option C'], label='Choose one')
    
    # Test slider
    nt.slider(min=0, max=100, value=50)
    
    # Test toggle
    nt.toggle(['Option 1', 'Option 2', 'Option 3'])
    
    ui.label('All components loaded successfully!').classes('text-green-600 mt-4')

# Example 2: Using core utilities
from nicetheme import ThemeManager, ThemeRegistry

# Initialize theme manager
manager = ThemeManager()
registry = ThemeRegistry()

print("✅ NiceTheme API test successful!")
print(f"Available components: {', '.join([x for x in dir(nt) if not x.startswith('_')])}")

if __name__ == '__main__':
    ui.run()

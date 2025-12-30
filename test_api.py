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
@ui.page('/')
def main_page():
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

    ui.separator().classes('my-4')
    
    ui.label('New Migrated Components').classes('text-xl font-bold mb-4')
    
    # Test Header
    nt.header(title='Section Header', subtitle='Migrated from Sortomatic', icon='settings')
    
    # Test Dangerous Button
    with ui.row().classes('items-center gap-4 py-4'):
        nt.dangerous_button(icon='delete', on_click=lambda: ui.notify('Boom!'), color='red')
        ui.label('Hold the button to trigger!')
        
    # Test Histogram
    with ui.row().classes('items-center gap-4 py-4'):
        nt.histogram([0.1, 0.3, 0.5, 0.9, 0.6, 0.2, 0.8], label='CPU Usage', color='var(--q-primary)')
        
    # Test Terminal
    terminal = nt.terminal(title='System Logs', height='200px')
    terminal.log('System initialized...', color='#00ff00')
    terminal.log('Loading components...', color='#ffff00')
    terminal.log('Error: Coffee not found', color='#ff0000')

# Example 2: Using core utilities
from nicetheme import ThemeManager, ThemeRegistry

# Initialize theme manager
manager = ThemeManager()
registry = ThemeRegistry()

print("✅ NiceTheme API test successful!")
print(f"Available components: {', '.join([x for x in dir(nt) if not x.startswith('_')])}")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

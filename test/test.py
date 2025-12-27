
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from nicegui import ui
from nicetheme.core.manager import ThemeManager
from nicetheme.core.registry import ThemeRegistry
from nicetheme.core.themes import Theme, Typography, Palette, Texture, Layout
from nicetheme.components.atoms.button import button, select_button
from nicetheme.components.atoms.select import select
from nicetheme.components.atoms.icon import palette_icon, texture_icon, theme_icon

# Initialize Registry and Manager
registry = ThemeRegistry(None)
manager = ThemeManager()

# Setup Defaults if Registry is empty or to ensure we have a valid theme
def get_default_theme() -> Theme:
    # Palette
    if registry.palettes:
        # Pick one if available, prefer 'solarized' if it exists to match previous context or just the first
        palettes = registry.palettes.get('solarized') or next(iter(registry.palettes.values()))
    else:
        light_palette = Palette(
            name="default", mode="light",
            primary="#007bff", secondary="#6c757d",
            positive="#28a745", negative="#dc3545", warning="#ffc107", info="#17a2b8", debug="#f8f9fa",
            inative="#adb5bd", colors={}, custom_colors={},
            content=["#000000", "#333333"], surface=["#ffffff", "#f8f9fa"],
            shadow="#000000", highlight="#ffffff", border="#e0e0e0"
        )
        dark_palette = Palette(
            name="default", mode="dark",
            primary="#007bff", secondary="#6c757d",
            positive="#28a745", negative="#dc3545", warning="#ffc107", info="#17a2b8", debug="#f8f9fa",
            inative="#adb5bd", colors={}, custom_colors={},
            content=["#ffffff", "#e0e0e0"], surface=["#121212", "#1e1e1e"],
            shadow="#000000", highlight="#333333", border="#444444"
        )
        palettes = {'light': light_palette, 'dark': dark_palette}

    # Texture
    if registry.textures:
        texture = registry.textures.get('frosted_glass') or next(iter(registry.textures.values()))
    else:
        texture = Texture(shadow_intensity=0.1, highlight_intensity=0.2, opacity=1.0, border_width=1.0, css="")

    # Layout
    if registry.layouts:
        layout = registry.layouts.get('relaxed') or next(iter(registry.layouts.values()))
    else:
        layout = Layout(roundness=4.0, density=1.0)

    # Typography (Manual as it's not scanned fully)
    typography = Typography(primary="Roboto", secondary="sans-serif", scale=1.0, title_case="title_case")

    return Theme(palettes=palettes, texture=texture, layout=layout, typography=typography)

theme = get_default_theme()
manager.apply(theme)

# UI Showcase
with ui.column().classes('w-full items-center p-8 gap-8 bg-gray-100 dark:bg-gray-900 min-h-screen'):
    
    ui.label('NiceTheme Atomic Elements').classes('text-4xl font-bold text-gray-800 dark:text-gray-100 mb-8')

    # Atom: Buttons
    with ui.card().classes('w-full max-w-4xl p-6'):
        ui.label('Buttons').classes('text-2xl font-semibold mb-4 text-gray-700')
        with ui.row().classes('w-full gap-4 items-center flex-wrap'):
            button('Primary Button', on_click=lambda: ui.notify('Primary Clicked'))
            button('Secondary Button', variant='secondary', on_click=lambda: ui.notify('Secondary Clicked'))
            button('Ghost Button', variant='ghost', on_click=lambda: ui.notify('Ghost Clicked'))
            button(icon='home', on_click=lambda: ui.notify('Icon Clicked'))
            button('Rotatable', icon='refresh', rotate_icon=True)
            
            ui.separator().classes('vertical')
            
            select_button('Select Button', on_click=lambda: ui.notify('Select Button'))
            select_button('With Icon', icon='settings', on_click=lambda: ui.notify('With Icon'))

    # Atom: Selects
    with ui.card().classes('w-full max-w-4xl p-6'):
        ui.label('Selects').classes('text-2xl font-semibold mb-4 text-gray-700')
        with ui.row().classes('w-full gap-4 items-start flex-wrap'):
            select(['Option 1', 'Option 2', 'Option 3'], label='Standard Select', value='Option 1').classes('w-48')
            select({'a': 'Apple', 'b': 'Banana'}, label='Mapped Select', value='a').classes('w-48')
            with select(['Item 1', 'Item 2'], label='Outlined').props('outlined').classes('w-48'):
                pass # Context manager usage check if valid (ui.select is context manager?) - Yes it inherits from Element
            
            # Rich select example
            rich_opts = [
                {'label': 'Google', 'value': 'google', 'icon': 'public'},
                {'label': 'Facebook', 'value': 'facebook', 'icon': 'share'},
            ]
            select(rich_opts, label='Rich Select', value='google').classes('w-48')

            # Icon Only
            select(['A', 'B'], label='Icon Only', icon_only=True, value='A').classes('w-12')

    # Atom: Icons (Theme System)
    with ui.card().classes('w-full max-w-4xl p-6'):
        ui.label('Theme Icons').classes('text-2xl font-semibold mb-4 text-gray-700')
        ui.label('Visual representations of theme components').classes('text-sm text-gray-500 mb-4')
        with ui.row().classes('gap-8 items-center justify-center bg-gray-50 p-8 rounded-lg'):
            with ui.column().classes('items-center gap-2'):
                palette_icon(theme.palette, size="64px")
                ui.label('Palette').classes('text-xs text-gray-500')

            with ui.column().classes('items-center gap-2'):
                texture_icon(theme.texture, theme.palette, theme.layout, size="64px")
                ui.label('Texture').classes('text-xs text-gray-500')
            
            with ui.column().classes('items-center gap-2'):
                theme_icon(theme, size="64px")
                ui.label('Full Theme').classes('text-xs text-gray-500')

ui.run(port=8080, title='NiceTheme Showcase', show=False, reload=True)
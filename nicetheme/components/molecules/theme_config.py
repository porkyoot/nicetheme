from nicegui import ui
from typing import Optional
from nicetheme.components.atoms.tab import tab
from nicetheme.components.atoms.toggle import toggle
from nicetheme.components.atoms.select import select
from nicetheme.components.atoms.slider import palette_slider
from nicetheme.core.manager import ThemeManager
from nicetheme.core.registry import ThemeRegistry

class theme_config(ui.column):
    def __init__(self, manager: ThemeManager, registry: ThemeRegistry):
        super().__init__()
        
        self.manager = manager
        self.registry = registry

        # Local state to track which palette object we are currently editing
        self._palette: Optional[Palette] = None
        
        palette_options = []
        if self.registry and self.registry.palettes:
            # Build palette options for the select
            for name in self.registry.palettes.keys():
                 palette_options.append({
                     'label': {'label': name.title(), 'icon': 'palette'},
                     'value': name
                 })
        
        # CSS for the tab animation
        ui.add_head_html('''
            <style>
                .nt-tab-label {
                    max-width: 0;
                    opacity: 0;
                    overflow: hidden;
                    transition: max-width 0.3s ease, opacity 0.3s ease, margin-left 0.3s ease;
                    white-space: nowrap;
                    font-size: 0.875rem; /* text-sm */
                    font-weight: 500;
                }
                .q-tab--active .nt-tab-label {
                    max-width: 150px;
                    opacity: 1;
                    margin-left: 8px;
                }
                .q-tab__content {
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                }
            </style>
        ''')
        
        with self:
            with ui.tabs().classes('w-full') as tabs:
                tab('Palette', icon='palette')
                tab('Texture', icon='texture')
                tab('Typography', icon='text_fields')
                tab('Layout', icon='view_quilt')
                
            with ui.tab_panels(tabs, value='Palette').classes('w-full bg-transparent'):
                with ui.tab_panel('Palette').classes('gap-4 column'):
                    
                    # Row 1: Mode Toggle & Palette Select
                    with ui.row().classes('w-full items-center justify-between'):
                        
                        # Mode Toggle
                        toggle_opts = [
                            {'value': 'light', 'icon': 'light_mode', 'label': None},
                            {'value': 'auto',  'icon': 'brightness_auto', 'label': None},
                            {'value': 'dark',  'icon': 'dark_mode', 'label': None},
                        ]
                        
                        color_map = {
                            'light': 'warning',
                            'auto': 'debug',
                            'dark': 'info'
                        }
                        
                        self._mode_toggle = toggle(toggle_opts, color_map=color_map, on_change=self._handle_mode_change)
                        self._mode_toggle.props('flat text-color=grey-7 round')

                        # Palette Select
                        self._palette_select = select(palette_options, label='Theme Palette', on_change=self._handle_palette_change).classes('w-48')

                    # Row 2: Color Sliders
                    with ui.column().classes('w-full gap-2'):
                        ui.label('Primary Accent').classes('text-xs opacity-60 font-bold mb-1')
                        self._primary_accent_slider = palette_slider(
                            colors={}, value='', on_change=self._update_primary_accent
                        )

                        ui.label('Secondary Accent').classes('text-xs opacity-60 font-bold mb-1')
                        self._secondary_accent_slider = palette_slider(
                            colors={}, value='', on_change=self._update_secondary_accent
                        )

        # Sync with manager
        self.manager.on_change(self._update_ui)
        self._update_ui()

    def _update_ui(self):
        """Updates the UI components based on the manager's current state."""
        if not self.manager.theme:
            return
            
        # 1. Update Mode Toggle
        self._mode_toggle.value = self.manager._mode
        
        # 2. Update Palette Select
        self._palette_select.value = self.manager.active_palette_name
        
        # 3. Resolve actual Palette object based on mode
        effective_mode = self.manager._mode
        if effective_mode == 'auto':
            effective_mode = 'light' # Simple fallback
            
        palette_set = self.registry.palettes.get(self.manager.active_palette_name)
        if palette_set:
            self._palette = palette_set.get(effective_mode)
            
        if self._palette:
            # 4. Update Sliders
            self._primary_accent_slider.set_colors(self._palette.colors, self._palette.primary)
            self._secondary_accent_slider.set_colors(self._palette.colors, self._palette.secondary)

    def _handle_palette_change(self, e):
        self.manager.active_palette_name = e.value
        # If we change the palette name, we should also update the manager's theme palettes
        palette_set = self.registry.palettes.get(e.value)
        if palette_set and self.manager.theme:
            self.manager.theme.palettes = palette_set
            self.manager.apply()

    def _handle_mode_change(self, e):
        self.manager.set_mode(e.value)

    def _update_primary_accent(self, color: str):
        if self._palette:
            self._palette.primary = color
            self.manager.apply()
        ui.notify(f'Primary updated to {color}')

    def _update_secondary_accent(self, color: str):
        if self._palette:
            self._palette.secondary = color
            self.manager.apply()
        ui.notify(f'Secondary updated to {color}')
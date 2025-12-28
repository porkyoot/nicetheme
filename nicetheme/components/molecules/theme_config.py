from nicegui import ui
from typing import Optional
from nicetheme.components.atoms.tab import tab
from nicetheme.components.atoms.toggle import toggle
from nicetheme.components.atoms.select import select
from nicetheme.components.atoms.slider import palette_slider
from nicetheme.core.manager import ThemeManager
from nicetheme.core.registry import ThemeRegistry

class theme_config(ui.column):
    def __init__(self, manager: Optional[ThemeManager] = None, registry: Optional[ThemeRegistry] = None):
        super().__init__()
        
        self.manager = manager
        self.registry = registry

        self.registry = registry
        
        palette_options = []
        if self.registry and self.registry.palettes:
            # For the purpose of this UI, we'll pick the 'solarized' palette or the first one in registry.
            # ThemeRegistry stores name -> { mode: Palette }
            palette_group = self.registry.palettes.get('solarized') or next(iter(self.registry.palettes.values()))
            self._palette = palette_group.get('light') or next(iter(palette_group.values()))
            
            # Build palette options for the select
            for name in self.registry.palettes.keys():
                 palette_options.append({
                     'label': {'label': name.title(), 'icon': 'palette'},
                     'value': name
                 })
        else:
             # Fallback mock palette if no registry
             from nicetheme.core.themes import Palette
             self._palette = Palette(
                name='mock', 
                mode='light',
                colors={'blue': '#007bff', 'gray': '#6c757d'},
                greys={'100': '#f8f9fa', '900': '#212529'},
                primary='#007bff', 
                secondary='#6c757d',
                positive='#28a745',
                negative='#dc3545',
                warning='#ffc107',
                info='#17a2b8',
                debug='#6c757d',
                inative='#adb5bd',
                content=['#212529'],
                surface=['#ffffff'],
                shadow='#000000',
                highlight='#ffffff',
                border='#dee2e6'
             )
             
             palette_options = [
                {'label': {'label': 'Solarized', 'icon': 'palette'}, 'value': 'solarized'},
                {'label': {'label': 'Metro', 'icon': 'grid_view'}, 'value': 'metro'},
             ]

        # CSS for the tab animation
        # We keep this here for now as it defines the 'nt-tab-label' behavior used by the atom
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
                
                /* Ensure tab content is centered and row-aligned */
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
                        
                        toggle(toggle_opts, value='auto', color_map=color_map).props('flat text-color=grey-7 round')


                        # Palette Select
                        select(palette_options, value='solarized', label='Theme Palette').classes('w-48')

                    # Row 2: Color Sliders
                    with ui.column().classes('w-full gap-2'):
                        # Primary Accent
                        ui.label('Primary Accent').classes('text-xs opacity-60 font-bold mb-1')
                        self._primary_accent_slider = palette_slider(
                            colors=self._palette.colors,
                            value=self._palette.primary,
                            on_change=self._update_primary_accent
                        )

                        # Secondary Accent
                        ui.label('Secondary Accent').classes('text-xs opacity-60 font-bold mb-1')
                        self._secondary_accent_slider = palette_slider(
                            colors=self._palette.colors,
                            value=self._palette.secondary,
                            on_change=self._update_secondary_accent
                        )

                with ui.tab_panel('Texture'):
                    ui.label('Texture Controls')
                    
                with ui.tab_panel('Typography'):
                    ui.label('Typography Controls')
                    
                with ui.tab_panel('Layout'):
                    ui.label('Layout Controls')

    def _update_primary_accent(self, color: str):
        self._palette.primary = color
        if self.manager and self.manager.theme:
             self.manager.apply(self.manager.theme) # Re-apply theme if possible
        ui.notify(f'Primary updated to {color}')

    def _update_secondary_accent(self, color: str):
        self._palette.secondary = color
        if self.manager and self.manager.theme:
             self.manager.apply(self.manager.theme)
        ui.notify(f'Secondary updated to {color}')

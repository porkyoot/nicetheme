from nicegui import ui
from typing import Optional
from nicetheme.components.atoms.tab import tab
from nicetheme.components.atoms.toggle import toggle
from nicetheme.components.atoms.select import select
from nicetheme.components.atoms.slider import palette_slider, slider, split_slider
from nicetheme.components.atoms.icon import palette_icon
from nicetheme.core.manager import ThemeManager
from nicetheme.core.registry import ThemeRegistry
from nicetheme.core.themes import Palette

class theme_config(ui.column):
    def __init__(self, manager: ThemeManager, registry: ThemeRegistry):
        super().__init__()
        
        self.manager = manager
        self.registry = registry

        # Local state to track which palette object we are currently editing
        self._palette: Optional[Palette] = None
        self._updating = False

        # Curated list of Google Fonts
        google_fonts = [
            "Roboto", "Open Sans", "Noto Sans JP", "Inter", "Lato", "Montserrat", 
            "Oswald", "Source Sans Pro", "Slabo 27px", "Raleway", "PT Sans", 
            "Merriweather", "Nunito Sans", "Prompt", "Work Sans", "Rubik",
            "Playfair Display", "Fira Sans", "Mukta", "Quicksand", "Karla",
            "Titillium Web", "Inconsolata", "Barlow", "Dosis", "Cabin",
            "Bitter", "Anton", "Oxygen", "Arvo", "Libre Baskerville", "Lobster",
            "Pacifico", "Shadows Into Light", "Dancing Script", "Bebas Neue",
            "Poppins", "Recursive"
        ]
        
        # Inject Google Fonts CSS
        families = "&family=".join([f.replace(' ', '+') for f in google_fonts])
        ui.add_head_html(f'<link href="https://fonts.googleapis.com/css2?family={families}&display=swap" rel="stylesheet">')

        # Combine with local fonts
        self._all_font_opts = []
        for name in self.registry.fonts:
             self._all_font_opts.append({
                 'label': name, 
                 'font': name,
                 'value': name,
                 'icon': 'computer'
             })
        
        for name in google_fonts:
             if not any(o['value'] == name for o in self._all_font_opts):
                  self._all_font_opts.append({
                      'label': name,
                      'font': name,
                      'value': name,
                      'icon': 'google'
                  })
        
        palette_options = []
        if self.registry and self.registry.palettes:
            # Build palette options for the select
            for name, palette_set in self.registry.palettes.items():
                 # Use light mode palette for the icon preview
                 icon_palette = palette_set.get('light') or next(iter(palette_set.values()))
                 palette_options.append({
                     'label': name.title(), 
                     'html': palette_icon.to_html(icon_palette, size="24px"),
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

                with ui.tab_panel('Texture').classes('gap-4 column'):
                    # Row 1: Texture Select
                    with ui.row().classes('w-full items-center justify-between'):
                        texture_options = list(self.registry.textures.keys()) if self.registry else []
                        self._texture_select = select(
                            texture_options, 
                            label='Base Texture', 
                            on_change=self._handle_texture_change
                        ).classes('w-full')

                    # Row 2: Shadow / Highlight Intensity (Split Slider)
                    with ui.column().classes('w-full gap-1'):
                        ui.label('Shadow & Highlight').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                        self._shadow_highlight_slider = split_slider(
                            limit=2.0,
                            step=0.05,
                            color_left='info',
                            color_right='warning',
                            on_change=self._update_shadow_highlight
                        )

                    # Row 3: Blur / Opacity
                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('col gap-1'):
                            ui.label('Blur').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                            self._blur_slider = slider(min=0, max=40, step=1, on_change=self._update_blur)
                            
                        with ui.column().classes('col gap-1'):
                            ui.label('Opacity').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                            self._opacity_slider = slider(min=0, max=1, step=0.01, on_change=self._update_opacity)

                    # Row 4: Border Width
                    with ui.column().classes('w-full gap-1'):
                        ui.label('Border Width').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                        self._border_slider = slider(
                            min=0, max=10, step=0.5, 
                            on_change=self._update_border_width
                        )

                with ui.tab_panel('Typography').classes('gap-4 column'):
                    # Font Selection
                    with ui.column().classes('w-full gap-2'):
                        self._font_primary_select = select(
                            options=self._all_font_opts,
                            label='Primary Font',
                            on_change=lambda e: self._update_font(e.value, is_main=True),
                            on_filter=self._filter_fonts
                        ).classes('w-full')

                        self._font_secondary_select = select(
                            options=self._all_font_opts,
                            label='Secondary Font',
                            on_change=lambda e: self._update_font(e.value, is_main=False),
                            on_filter=self._filter_fonts
                        ).classes('w-full')

                    # Font Scale
                    with ui.column().classes('w-full gap-1'):
                        ui.label('Font Scale').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                        self._font_scale_slider = slider(
                            min=0.5, max=2.0, step=0.05, 
                            on_change=self._update_font_scale
                        )

                    # Case Toggle
                    with ui.column().classes('w-full gap-1'):
                        ui.label('Text Case').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                        case_opts = [
                            {'value': 'none', 'icon': 'block', 'label': None},
                            {'value': 'lowercase', 'label': 'aa'},
                            {'value': 'title_case', 'label': 'Aa'},
                            {'value': 'uppercase', 'label': 'AA'},
                        ]
                        self._case_toggle = toggle(case_opts, on_change=self._update_text_case)

        # Sync with manager
        self.manager.on_change(self._update_ui)
        self._update_ui()

    def _update_ui(self):
        """Updates the UI components based on the manager's current state."""
        if not self.manager.theme:
            return
        
        self._updating = True
        try:
            
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

            # 5. Update Texture UI
            if self.manager.theme and self.manager.theme.texture:
                tex = self.manager.theme.texture
                self._shadow_highlight_slider.slider_left.value = tex.shadow_intensity
                self._shadow_highlight_slider.slider_right.value = tex.highlight_intensity
                
                self._blur_slider.value = tex.blur
                self._opacity_slider.value = tex.opacity
                self._border_slider.value = tex.border_width
                
                # Disable blur if opacity is 0
                self._blur_slider.disable() if tex.opacity == 0 else self._blur_slider.enable()

            # 6. Update Typography UI
            if self.manager.theme and self.manager.theme.typography:
                typo = self.manager.theme.typography
                self._font_primary_select.value = typo.primary
                self._font_secondary_select.value = typo.secondary
                self._font_scale_slider.value = typo.scale
                self._case_toggle.value = typo.title_case
            
        finally:
            self._updating = False

    def _handle_palette_change(self, e):
        if self._updating: return
        self.manager.active_palette_name = e.value
        palette_set = self.registry.palettes.get(e.value)
        if palette_set and self.manager.theme:
            self.manager.theme.palettes = palette_set
            self.manager.apply()

    def _handle_mode_change(self, e):
        if self._updating: return
        self.manager.set_mode(e.value)

    def _update_primary_accent(self, color: str):
        if self._updating: return
        if self._palette:
            self._palette.primary = color
            self.manager.apply()
        ui.notify(f'Primary updated to {color}')

    def _update_secondary_accent(self, color: str):
        if self._updating: return
        if self._palette:
            self._palette.secondary = color
            self.manager.apply()
        ui.notify(f'Secondary updated to {color}')

    def _handle_texture_change(self, e):
        if self._updating: return
        texture = self.registry.textures.get(e.value)
        if texture and self.manager.theme:
            self.manager.theme.texture = texture
            self.manager.apply()
            self._update_ui()

    def _update_shadow_highlight(self, values: dict):
        if self._updating: return
        if self.manager.theme and self.manager.theme.texture:
            self.manager.theme.texture.shadow_intensity = values['left']
            self.manager.theme.texture.highlight_intensity = values['right']
            self.manager.apply()

    def _update_blur(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.texture:
            self.manager.theme.texture.blur = int(e.value)
            self.manager.apply()

    def _update_opacity(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.texture:
            self.manager.theme.texture.opacity = e.value
            self._blur_slider.disable() if e.value == 0 else self._blur_slider.enable()
            self.manager.apply()

    def _update_border_width(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.texture:
            self.manager.theme.texture.border_width = e.value
            self.manager.apply()

    def _filter_fonts(self, value: str):
        if not value:
            return self._all_font_opts
        return [opt for opt in self._all_font_opts if value.lower() in (opt['value'] or "").lower()]

    def _update_font(self, font_name: str, is_main: bool):
        if self._updating: return
        if not self.manager.theme or not font_name:
            return
            
        # Check if it's a Google Font (not in registry.fonts)
        if font_name not in self.registry.fonts:
            # Inject Google Font
            font_family = font_name.replace(' ', '+')
            ui.add_head_html(f'<link href="https://fonts.googleapis.com/css2?family={font_family}&display=swap" rel="stylesheet">')
            
        if is_main:
            self.manager.theme.typography.primary = font_name
        else:
            self.manager.theme.typography.secondary = font_name
            
        self.manager.apply()

    def _update_font_scale(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.typography:
            self.manager.theme.typography.scale = float(e.value)
            self.manager.apply()

    def _update_text_case(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.typography:
            self.manager.theme.typography.title_case = e.value
            self.manager.apply()
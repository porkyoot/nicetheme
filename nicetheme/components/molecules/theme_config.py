from nicegui import ui
from typing import Optional, List, Dict
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

        # Curated list of Google Fonts - kept for UI options
        google_fonts = [
            "Roboto", "Open Sans", "Noto Sans JP", "Inter", "Lato", "Montserrat", 
            "Oswald", "Source Sans Pro", "Slabo 27px", "Raleway", "PT Sans", 
            "Merriweather", "Nunito Sans", "Prompt", "Work Sans", "Rubik",
            "Playfair Display", "Fira Sans", "Mukta", "Quicksand", "Karla",
            "Titillium Web", "Inconsolata", "Barlow", "Dosis", "Cabin",
            "Bitter", "Anton", "Oxygen", "Arvo", "Libre Baskerville", "Lobster",
            "Pacifico", "Shadows Into Light", "Dancing Script", "Bebas Neue",
            "Poppins", "Recursive", "Sniglet"
        ]
        google_fonts.sort()
        
        # Combine with local fonts
        self._all_font_opts = []
        for name in self.registry.fonts:
             self._all_font_opts.append({
                 'label': name, 
                 'font': name,
                 'value': name,
                 'origin': 'local',
                 'icon': 'computer'
             })
        
        # Simple Google "G" Icon (MDI path)
        google_svg = '<svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: currentColor;"><path d="M21.35,11.1H12.18V13.83H18.69C18.36,17.64 15.19,19.27 12.19,19.27C8.36,19.27 5,16.25 5,12C5,7.9 8.2,4.73 12.2,4.73C15.29,4.73 17.1,6.7 17.1,6.7L19,4.72C19,4.72 16.56,2 12.1,2C6.42,2 2.03,6.8 2.03,12C2.03,17.05 6.16,22 12.25,22C17.6,22 21.5,18.33 21.5,12.91C21.5,11.76 21.35,11.1 21.35,11.1V11.1Z"/></svg>'

        for name in google_fonts:
             if not any(o['value'] == name for o in self._all_font_opts):
                  self._all_font_opts.append({
                      'label': name,
                      'font': name,
                      'value': name,
                      'origin': 'google',
                      'html': google_svg
                  })
        
        # Add browser default fonts at the end
        browser_fonts = [
            ('serif', 'Serif'),
            ('sans-serif', 'Sans-serif'),
            ('monospace', 'Monospace'),
            ('cursive', 'Cursive'),
            ('fantasy', 'Fantasy'),
            ('system-ui', 'System UI')
        ]
        
        for value, label in browser_fonts:
            self._all_font_opts.append({
                'label': label,
                'font': value,
                'value': value,
                'origin': 'browser',
                'icon': 'language'  # Browser/globe icon
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
                            ui.label('Opacity').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                            self._opacity_slider = slider(min=0, max=1, step=0.01, on_change=self._update_opacity)

                        with ui.column().classes('col gap-1') as self._blur_container:
                            ui.label('Blur').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                            self._blur_slider = slider(min=0, max=40, step=1, on_change=self._update_blur)

                with ui.tab_panel('Typography').classes('gap-4 column'):
                    # Font Selection
                    with ui.column().classes('w-full gap-2'):
                        # Primary Font and Text Case on same row
                        with ui.row().classes('w-full gap-4'):
                            self._font_primary_select = select(
                                options=self._all_font_opts,
                                label='Primary Font',
                                on_change=lambda e: self._update_font(e.value, font_type='primary'),
                                on_filter=self._filter_fonts
                            ).classes('flex-1')
                            
                            # Text Case Toggle
                            with ui.column().classes('gap-1'):
                                ui.label('Text Case').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                                case_opts = [
                                    {'value': 'none', 'icon': 'block', 'label': None, 'tooltip': 'No text transformation'},
                                    {'value': 'lowercase', 'label': 'aa', 'tooltip': 'Convert to lowercase'},
                                    {'value': 'titlecase', 'label': 'Aa', 'tooltip': 'Convert to Title Case'},
                                    {'value': 'uppercase', 'label': 'AA', 'tooltip': 'Convert to UPPERCASE'},
                                ]
                                self._case_toggle = toggle(case_opts, on_change=self._update_text_case).props('no-caps').classes('nt-case-toggle')

                        # Secondary and Mono on same row
                        with ui.row().classes('w-full gap-4'):
                            self._font_secondary_select = select(
                                options=self._all_font_opts,
                                label='Secondary Font',
                                on_change=lambda e: self._update_font(e.value, font_type='secondary'),
                                on_filter=self._filter_fonts
                            ).classes('flex-1')

                            self._font_mono_select = select(
                                options=self._all_font_opts,
                                label='Mono Font',
                                on_change=lambda e: self._update_font(e.value, font_type='mono'),
                                on_filter=self._filter_fonts
                            ).classes('flex-1')

                    # Font Scale
                    with ui.column().classes('w-full gap-1'):
                        ui.label('Font Scale').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                        self._font_scale_slider = slider(
                            min=0.5, max=2.0, step=0.05, 
                            on_change=self._update_font_scale
                        )

                with ui.tab_panel('Layout').classes('gap-4 column'):
                    # Row 1: Border & Roundness
                    with ui.row().classes('w-full gap-4'):
                        # Border
                        with ui.column().classes('col gap-1'):
                            ui.label('Border').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                            self._border_slider = slider(min=0, max=4, step=1, on_change=self._update_border)
                        
                        # Roundness
                        with ui.column().classes('col gap-1'):
                            ui.label('Roundness').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                            self._roundness_slider = slider(min=0, max=32, step=1, on_change=self._update_roundness)

                    # Row 2: Density
                    with ui.column().classes('w-full gap-1'):
                        ui.label('Density').classes('text-[10px] opacity-60 font-bold uppercase tracking-wider')
                        self._density_slider = slider(min=0.5, max=1.5, step=0.05, on_change=self._update_density)
                    
        # Sync with manager
        self.manager.bind(self._update_ui)
        self._update_ui(self.manager)

    def _update_ui(self, manager: ThemeManager):
        """Updates the UI components based on the manager's current state."""
        if not self.manager.theme:
            return
        
        self._updating = True
        try:
            
            # 1. Update Mode Toggle
            self._mode_toggle.value = self.manager.mode
            
            # 2. Update Palette Select
            self._palette_select.value = self.manager.active_palette_name
            
            # 3. Resolve actual Palette object based on mode
            self._palette = self.manager.get_active_palette()
                
            if self._palette:
                # 4. Update Sliders - resolve color references to actual hex values
                self._primary_accent_slider.set_colors(
                    self._palette.colors, 
                    self._palette.resolve_color(self._palette.primary)
                )
                self._secondary_accent_slider.set_colors(
                    self._palette.colors, 
                    self._palette.resolve_color(self._palette.secondary)
                )

            # 5. Update Texture UI
            if self.manager.theme and self.manager.theme.texture:
                tex = self.manager.theme.texture
                
                # Sync texture select dropdown - find matching registered texture
                current_texture_name = None
                for name, registered_tex in self.registry.textures.items():
                    # Check if this is the same texture object or has matching properties
                    if registered_tex is tex or (
                        registered_tex.shadow_intensity == tex.shadow_intensity and
                        registered_tex.highlight_intensity == tex.highlight_intensity and
                        registered_tex.blur == tex.blur and
                        registered_tex.opacity == tex.opacity
                    ):
                        current_texture_name = name
                        break
                
                if current_texture_name:
                    self._texture_select.value = current_texture_name
                
                # Update texture sliders
                self._shadow_highlight_slider.slider_left.value = tex.shadow_intensity
                self._shadow_highlight_slider.slider_right.value = tex.highlight_intensity
                
                self._blur_slider.value = tex.blur
                self._opacity_slider.value = tex.opacity
                
                self._blur_container.set_visibility(tex.opacity < 1)

            # 6. Update Typography UI
            if self.manager.theme and self.manager.theme.typography:
                typo = self.manager.theme.typography
                
                # Helper to find or add a font option (case-insensitive, auto-loads Google Fonts)
                fonts_added = False
                def find_or_add_font(font_name: str) -> str:
                    nonlocal fonts_added
                    if not font_name:
                        return ''
                    
                    # First try exact match
                    for opt in self._all_font_opts:
                        if opt.get('value') == font_name:
                            return font_name
                    
                    # Try case-insensitive match
                    font_lower = font_name.lower()
                    for opt in self._all_font_opts:
                        if opt.get('value', '').lower() == font_lower:
                            return opt.get('value')
                    
                    # Not found - assume it's a Google Font and add it
                    # Simple Google "G" Icon (MDI path)
                    google_svg = '<svg viewBox="0 0 24 24" style="width: 20px; height: 20px; fill: currentColor;"><path d="M21.35,11.1H12.18V13.83H18.69C18.36,17.64 15.19,19.27 12.19,19.27C8.36,19.27 5,16.25 5,12C5,7.9 8.2,4.73 12.2,4.73C15.29,4.73 17.1,6.7 17.1,6.7L19,4.72C19,4.72 16.56,2 12.1,2C6.42,2 2.03,6.8 2.03,12C2.03,17.05 6.16,22 12.25,22C17.6,22 21.5,18.33 21.5,12.91C21.5,11.76 21.35,11.1 21.35,11.1V11.1Z"/></svg>'
                    
                    # Add to options with proper casing (Title Case)
                    title_cased = ' '.join(word.capitalize() for word in font_name.split())
                    new_option = {
                        'label': title_cased,
                        'font': title_cased,
                        'value': title_cased,
                        'origin': 'google',
                        'html': google_svg
                    }
                    self._all_font_opts.append(new_option)
                    fonts_added = True
                    
                    # Inject the Google Font CSS
                    font_url = title_cased.replace(' ', '+')
                    ui.add_head_html(f'<link href="https://fonts.googleapis.com/css2?family={font_url}&display=swap" rel="stylesheet">')
                    
                    return title_cased
                
                # Find/add all fonts
                primary_font = find_or_add_font(typo.primary)
                secondary_font = find_or_add_font(typo.secondary)
                mono_font = find_or_add_font(typo.mono)
                
                # If fonts were added, update all selects' options
                if fonts_added:
                    # Convert list back to dict format for select component
                    options_dict = {opt.get('value'): opt for opt in self._all_font_opts if opt.get('value')}
                    self._font_primary_select.options = options_dict
                    self._font_secondary_select.options = options_dict
                    self._font_mono_select.options = options_dict
                    self._font_primary_select.update()
                    self._font_secondary_select.update()
                    self._font_mono_select.update()
                
                # Set values
                self._font_primary_select.set_value(primary_font)
                self._font_secondary_select.set_value(secondary_font)
                self._font_mono_select.set_value(mono_font)
                self._font_scale_slider.value = typo.scale
                self._case_toggle.value = typo.title_case

            # 7. Update Layout UI
            if self.manager.theme and self.manager.theme.layout:
                layout = self.manager.theme.layout
                self._border_slider.value = layout.border
                self._roundness_slider.value = layout.roundness
                self._density_slider.value = layout.density
            
        finally:
            self._updating = False

    def _handle_palette_change(self, e):
        if self._updating: return
        self.manager.set_palette(e.value)

    def _handle_mode_change(self, e):
        if self._updating: return
        self.manager.set_mode(e.value)

    def _update_primary_accent(self, color: str):
        if self._updating: return
        # Using specific method
        self.manager.update_primary_color(color)
        ui.notify(f'Primary updated to {color}')

    def _update_secondary_accent(self, color: str):
        if self._updating: return
        # Use manager method for consistent state management
        self.manager.update_secondary_color(color)
        ui.notify(f'Secondary updated to {color}')

    def _handle_texture_change(self, e):
        if self._updating: return
        texture = self.registry.textures.get(e.value)
        if texture and self.manager.theme:
            self.manager.theme.texture = texture
            self.manager.refresh()

    def _update_shadow_highlight(self, values: dict):
        if self._updating: return
        if self.manager.theme and self.manager.theme.texture:
            self.manager.theme.texture.shadow_intensity = values['left']
            self.manager.theme.texture.highlight_intensity = values['right']
            self.manager.refresh()

    def _update_blur(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.texture:
            self.manager.theme.texture.blur = int(e.value)
            self.manager.refresh()

    def _update_opacity(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.texture:
            self.manager.theme.texture.opacity = e.value
            self._blur_container.set_visibility(e.value < 1)
            self.manager.refresh()

    def _update_border(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.layout:
            self.manager.theme.layout.border = e.value
            self.manager.refresh()

    def _update_roundness(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.layout:
            self.manager.theme.layout.roundness = e.value
            self.manager.refresh()

    def _update_density(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.layout:
            self.manager.theme.layout.density = e.value
            self.manager.refresh()

    def _filter_fonts(self, value: str):
        if not value:
            return self._all_font_opts
        return [opt for opt in self._all_font_opts if value.lower() in (opt['value'] or "").lower()]

    def _update_font(self, font_name: str, font_type: str):
        if self._updating: return
        if not self.manager.theme or not font_name:
            return
            
        # Bridge loads ALL fonts at init. So we just set the value.
        if font_type == 'primary':
            self.manager.theme.typography.primary = font_name
        elif font_type == 'secondary':
            self.manager.theme.typography.secondary = font_name
        elif font_type == 'mono':
            self.manager.theme.typography.mono = font_name
            
        self.manager.refresh()

    def _update_font_scale(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.typography:
            self.manager.theme.typography.scale = float(e.value)
            self.manager.refresh()

    def _update_text_case(self, e):
        if self._updating: return
        if self.manager.theme and self.manager.theme.typography:
            self.manager.theme.typography.title_case = e.value
            self.manager.refresh()
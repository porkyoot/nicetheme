from nicegui import ui
from typing import List
import os
from .manager import ThemeManager
from .registry import ThemeRegistry
from .themes import Palette, Texture, Layout, Typography

class ThemeBridge:
    """
    THE BRIDGE: Handles synchronization between ThemeManager state 
    and the NiceGUI frontend (CSS variables, Quasar config).
    """
    def __init__(self, manager: ThemeManager, registry: ThemeRegistry):
        self.manager = manager
        self.registry = registry
        
        # Subscribe to changes automatically
        self.manager.bind(self.sync)
        
        # Inject static resources
        self._inject_static_styles()
        self._inject_google_fonts()
        self._inject_local_fonts()

        # Initial Variable Injection (SSR friendly)
        if self.manager.theme:
            palette = self.manager.get_active_palette()
            if palette:
                css_vars = self._generate_css_vars_dict(self.manager, palette)
                
                # Unwrap dict to css string
                css_lines = [f"{k}: {v};" for k, v in css_vars.items()]
                vars_block = "\n  ".join(css_lines)
                
                # Check mode
                mode = self.manager.get_effective_mode()
                if mode == 'dark':
                    ui.add_head_html(f"<style>body.body--dark {{ {vars_block} }}</style>")
                else:
                    ui.add_head_html(f"<style>:root {{ {vars_block} }}</style>")

    def sync(self, manager: ThemeManager):
        """Called whenever the manager notifies of a change."""
        theme = manager.theme
        if not theme:
            return

        palette = manager.get_active_palette()
        if not palette:
            return

        # 1. Update Quasar/NiceGUI global colors
        ui.colors(
            primary=palette.resolve_color(palette.primary),
            secondary=palette.resolve_color(palette.secondary),
            positive=palette.resolve_color(palette.positive),
            negative=palette.resolve_color(palette.negative),
            warning=palette.resolve_color(palette.warning),
            info=palette.resolve_color(palette.info),
            accent=palette.resolve_color(palette.content[0]) if palette.content else palette.resolve_color(palette.primary),
            dark=palette.resolve_color('base03'),
        )

        # 2. Generate CSS Variables Dictionary
        css_vars = self._generate_css_vars_dict(manager, palette)
        
        # 3. Update CSS Variables & Body Class via JS (Dynamic & Fast)
        import json
        mode = manager.get_effective_mode()
        is_dark = mode == 'dark'
        
        js_cmd = f"""
        const vars = {json.dumps(css_vars)};
        Object.entries(vars).forEach(([k,v]) => document.documentElement.style.setProperty(k, v));
        
        // Toggle Body Classes
        if ({str(is_dark).lower()}) {{
            document.body.classList.add('body--dark');
            document.body.classList.remove('body--light');
            document.querySelector('#app').classList.add('q-dark'); // Standard Quasar
        }} else {{
            document.body.classList.remove('body--dark');
            document.body.classList.add('body--light');
            document.querySelector('#app').classList.remove('q-dark');
        }}
        """
        try:
            ui.run_javascript(js_cmd)
        except (AssertionError, RuntimeError):
            # No active client/loop (e.g. during startup), skip JS update
            pass

    def _generate_css_vars_dict(self, manager: ThemeManager, palette: Palette) -> dict:
        """Generates a flat dictionary of CSS variables."""
        css_vars = {}
        
        # Helper for resolving colors
        def rc(val): return palette.resolve_color(val)
        
        # Helper to hex to rgb
        def hex_to_rgb(hex_code):
            hex_code = hex_code.lstrip('#')
            if len(hex_code) == 3: hex_code = ''.join([c*2 for c in hex_code])
            return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
            
        def to_rgb_str(val):
            try:
                c = rc(val)
                if c.startswith('#'):
                    h = hex_to_rgb(c)
                    return f"{h[0]}, {h[1]}, {h[2]}"
                return "0, 0, 0" # Fallback
            except:
                return "0, 0, 0"

        # 1. Palette Colors
        css_vars["--nt-primary"] = rc(palette.primary)
        css_vars["--nt-secondary"] = rc(palette.secondary)
        css_vars["--nt-positive"] = rc(palette.positive)
        css_vars["--nt-negative"] = rc(palette.negative)
        css_vars["--nt-warning"] = rc(palette.warning)
        css_vars["--nt-info"] = rc(palette.info)
        css_vars["--nt-inactive"] = rc(palette.inative)

        # Custom & Named Colors
        for name, color in palette.colors.items():
            css_vars[f"--nt-color-{name}"] = rc(color)

        # Greys
        for name, color in palette.greys.items():
            css_vars[f"--nt-color-{name}"] = rc(color)

        # 2. Surface (with Padding)
        if palette.surface:
            css_vars["--nt-surface-rgb"] = to_rgb_str(palette.surface[0])
            css_vars["--nt-surface-page"] = rc(palette.surface[0])
            
            # Pad up to 6 levels (0-5)
            last_surface = palette.surface[-1]
            for i in range(6):
                if i < len(palette.surface):
                    val = palette.surface[i]
                else:
                    val = last_surface
                css_vars[f"--nt-surface-{i}"] = rc(val)
        
        # 3. Content
        if palette.content:
            css_vars["--nt-content-rgb"] = to_rgb_str(palette.content[0])
            css_vars["--nt-content-accent"] = rc(palette.content[0])
            
            for i, cont in enumerate(palette.content):
                css_vars[f"--nt-content-{i}"] = rc(cont)

        # 4. Texture Colors
        css_vars["--nt-shadow-color"] = rc(palette.shadow)
        css_vars["--nt-shadow-rgb"] = to_rgb_str(palette.shadow)
        css_vars["--nt-highlight-color"] = rc(palette.highlight)
        css_vars["--nt-highlight-rgb"] = to_rgb_str(palette.highlight)
        css_vars["--nt-border-color"] = rc(palette.border)
        css_vars["--nt-border-rgb"] = to_rgb_str(palette.border)

        # 5. Theme Settings (Layout, Texture, Typography)
        if manager.theme:
            if manager.theme.layout:
                layout = manager.theme.layout
                css_vars["--nt-roundness"] = str(layout.roundness)
                css_vars["--nt-border-width"] = str(layout.border)
                css_vars["--nt-density"] = str(layout.density)
            
            if manager.theme.texture:
                texture = manager.theme.texture
                css_vars["--nt-shadow-intensity"] = str(texture.shadow_intensity)
                css_vars["--nt-highlight-intensity"] = str(texture.highlight_intensity)
                css_vars["--nt-opacity"] = str(texture.opacity)
                css_vars["--nt-blur"] = str(texture.blur)

            if manager.theme.typography:
                typo = manager.theme.typography
                css_vars["--nt-font-primary"] = f"'{typo.primary}'"
                css_vars["--nt-font-secondary"] = f"'{typo.secondary}'"
                css_vars["--nt-font-scale"] = str(typo.scale)
                
                transform_map = {
                     "lowercase": "lowercase",
                     "uppercase": "uppercase",
                     "titlecase": "capitalize",
                     "title_case": "capitalize",
                     "none": "none"
                }
                css_vars["--nt-text-transform-title"] = transform_map.get(typo.title_case, "none")
        
        return css_vars

    def _inject_static_styles(self):
        """Injects static CSS files."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(current_dir), 'assets')
        
        for css_file in ['icons.css', 'sliders.css', 'components.css', 'global_overrides.css']:
            path = os.path.join(assets_dir, css_file)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    ui.add_head_html(f"<style>{f.read()}</style>")

    def _inject_google_fonts(self):
        # A curated list of Google Fonts
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
        families = "&family=".join([f.replace(' ', '+') for f in google_fonts])
        ui.add_head_html(f'<link href="https://fonts.googleapis.com/css2?family={families}&display=swap" rel="stylesheet">')

    def _inject_local_fonts(self):
        """Generates @font-face rules for local fonts registered in the Registry."""
        if not self.registry or not self.registry.fonts:
            return

        css_rules = []
        for name, url in self.registry.fonts.items():
            rule = f"""
            @font-face {{
                font-family: '{name}';
                src: url('{url}');
            }}
            """
            css_rules.append(rule)
        
        if css_rules:
            ui.add_head_html(f"<style>{''.join(css_rules)}</style>")


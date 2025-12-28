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
        )

        # 2. Generate CSS
        css_styles = self._generate_css(manager, palette)
        
        # 3. Inject CSS (The Side Effect)
        # Note: Ideally we would update existing style tag, but appending works (cascading)
        ui.add_head_html(f"<style>{css_styles}</style>")

    def _generate_css(self, manager: ThemeManager, palette: Palette) -> str:
        """Pure logic: Converts objects to CSS string"""
        css_lines = []
        
        # Helper for resolving colors
        def rc(val): return palette.resolve_color(val)

        # Generate CSS Variables for Palette
        css_lines.append(f"--nt-primary: {rc(palette.primary)};")
        css_lines.append(f"--nt-secondary: {rc(palette.secondary)};")
        css_lines.append(f"--nt-positive: {rc(palette.positive)};")
        css_lines.append(f"--nt-negative: {rc(palette.negative)};")
        css_lines.append(f"--nt-warning: {rc(palette.warning)};")
        css_lines.append(f"--nt-info: {rc(palette.info)};")
        css_lines.append(f"--nt-inactive: {rc(palette.inative)};")

        # Custom & Named Colors
        for name, color in palette.colors.items():
            css_lines.append(f"--nt-color-{name}: {rc(color)};")

        # Surface
        for i, surf in enumerate(palette.surface):
            css_lines.append(f"--nt-surface-{i}: {rc(surf)};")
            if i == 0: css_lines.append(f"--nt-surface-page: {rc(surf)};")
        
        # Content
        for i, cont in enumerate(palette.content):
            css_lines.append(f"--nt-content-{i}: {rc(cont)};")
            if i == 0: css_lines.append(f"--nt-content-accent: {rc(cont)};")
        
        # Texture colors
        css_lines.append(f"--nt-shadow-color: {rc(palette.shadow)};")
        css_lines.append(f"--nt-highlight-color: {rc(palette.highlight)};")
        css_lines.append(f"--nt-border-color: {rc(palette.border)};")

        # Handle Texture/Layout/Typography from manager._theme...
        if manager.theme:
            if manager.theme.layout:
                layout = manager.theme.layout
                css_lines.append(f"--nt-roundness: {layout.roundness};")
                css_lines.append(f"--nt-density: {layout.density};")
            
            if manager.theme.texture:
                texture = manager.theme.texture
                css_lines.append(f"--nt-shadow-intensity: {texture.shadow_intensity};")
                css_lines.append(f"--nt-highlight-intensity: {texture.highlight_intensity};")
                css_lines.append(f"--nt-opacity: {texture.opacity};")

            if manager.theme.typography:
                typo = manager.theme.typography
                css_lines.append(f"--nt-font-primary: {typo.primary};")
                css_lines.append(f"--nt-font-secondary: {typo.secondary};")
                css_lines.append(f"--nt-font-scale: {typo.scale};")
                
                transform_map = {
                     "lowercase": "lowercase",
                     "uppercase": "uppercase",
                     "titlecase": "capitalize",
                     "title_case": "capitalize",
                     "none": "none"
                }
                val = transform_map.get(typo.title_case, "none")
                css_lines.append(f"--nt-text-transform-title: {val};")

        # Append specific texture CSS if present
        extra_css = ""
        if manager.theme and manager.theme.texture and manager.theme.texture.css:
            extra_css = manager.theme.texture.css

        # Wrap in :root or body class based on mode
        mode = manager.get_effective_mode()
        
        vars_block = "\n  ".join(css_lines)
        
        if mode == 'dark':
            return f"body.body--dark {{ {vars_block} }} \n {extra_css}"
        else:
            return f":root {{ {vars_block} }} \n {extra_css}"

    def _inject_static_styles(self):
        """Injects static CSS files."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(current_dir), 'assets')
        
        for css_file in ['icons.css', 'sliders.css', 'components.css']:
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


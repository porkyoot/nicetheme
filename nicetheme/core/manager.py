from nicegui import ui
from typing import Dict, List, Optional
from .themes import Theme, Palette, Texture, Layout, Typography

class ThemeManager:
    """
    Manages the application of themes to the NiceGUI app.
    Translates Theme objects into NiceGUI colors, CSS variables, and other settings.
    """

    def __init__(self):
        self.theme: Optional[Theme] = None
        self.active_palette_name: str = 'solarized'
        self._mode: Literal['light', 'dark', 'auto'] = 'light'
        self._listeners: List[Callable[[], None]] = []

    def on_change(self, listener: Callable[[], None]):
        """Registers a listener for theme changes."""
        self._listeners.append(listener)

    def _notify_listeners(self):
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                print(f"Error notifying listener: {e}")

    def apply(self, theme: Optional[Theme] = None):
        """
        Applies the given theme to the application.
        If no theme is provided, re-applies the current theme.
        """
        if theme:
            self.theme = theme
        
        if not self.theme:
            return

        # Use current mode to find which palette to apply for global Quasar
        # 'auto' usually means follow system, but for now we'll pick light if auto
        effective_mode = self._mode
        if effective_mode == 'auto':
            effective_mode = 'light' # TODO: detect system mode?
            
        palette = self.theme.palettes.get(effective_mode) or next(iter(self.theme.palettes.values()))
        
        self._apply_palettes(self.theme.palettes, effective_mode)
        self._apply_texture(self.theme.texture, palette) 
        self._apply_layout(self.theme.layout)
        self._apply_typography(self.theme.typography)
        self._inject_static_styles()
        self._notify_listeners()

    def set_mode(self, mode: str):
        self._mode = mode
        self.apply()

    def _apply_palettes(self, palettes: Dict[str, Palette], active_mode: str):
        # Determine base palette for global Quasar config
        base_palette = palettes.get(active_mode) or next(iter(palettes.values()))
        
        # 1. Update Quasar/NiceGUI brand colors
        # Use resolve_color method from Palette
        ui.colors(
            primary=base_palette.resolve_color(base_palette.primary),
            secondary=base_palette.resolve_color(base_palette.secondary),
            positive=base_palette.resolve_color(base_palette.positive),
            negative=base_palette.resolve_color(base_palette.negative),
            warning=base_palette.resolve_color(base_palette.warning),
            info=base_palette.resolve_color(base_palette.info),
            accent=base_palette.resolve_color(base_palette.content[0]) if base_palette.content else base_palette.resolve_color(base_palette.primary),
        )

        css_styles: List[str] = []

        for mode, palette in palettes.items():
            # Generate Vars for this palette
            vars_list = []
            
            # Helper to resolve
            def rc(ref): return palette.resolve_color(ref)

            # Surface
            for i, surf in enumerate(palette.surface):
                vars_list.append(f"--nt-surface-{i}: {rc(surf)};")
                if i == 0: vars_list.append(f"--nt-surface-page: {rc(surf)};")
            
            # Content
            for i, cont in enumerate(palette.content):
                vars_list.append(f"--nt-content-{i}: {rc(cont)};")
                if i == 0: vars_list.append(f"--nt-content-accent: {rc(cont)};")
            
            # Texture colors (now in Palette)
            vars_list.append(f"--nt-shadow-color: {rc(palette.shadow)};")
            vars_list.append(f"--nt-highlight-color: {rc(palette.highlight)};")
            vars_list.append(f"--nt-border-color: {rc(palette.border)};")
            
            # Base Colors (Apply to Root only? Or both? Actually colors like primary usually stay same, but let's allow override)
            # If mode is light (or default), we put everything in :root
            # If mode is dark, we put in body.body--dark
            
            brand_vars = [
                f"--nt-primary: {rc(palette.primary)};",
                f"--nt-secondary: {rc(palette.secondary)};",
                f"--nt-positive: {rc(palette.positive)};",
                f"--nt-negative: {rc(palette.negative)};",
                f"--nt-warning: {rc(palette.warning)};",
                f"--nt-info: {rc(palette.info)};",
                f"--nt-inactive: {rc(palette.inative)};",
            ]
            
            # Custom & Named Colors
            for name, color in palette.colors.items():
                brand_vars.append(f"--nt-color-{name}: {rc(color)};")
            
            all_vars = brand_vars + vars_list
            
            if mode == 'light':
                css_styles.append(":root {\n  " + "\n  ".join(all_vars) + "\n}")
            elif mode == 'dark':
                css_styles.append("\nbody.body--dark {\n  " + "\n  ".join(all_vars) + "\n}")
                
        ui.add_head_html(f"<style>{''.join(css_styles)}</style>")


    def _apply_texture(self, texture: Texture, palette: Palette):
        
        css_vars = []
        css_vars.append(f"--nt-shadow-intensity: {texture.shadow_intensity};")
        css_vars.append(f"--nt-highlight-intensity: {texture.highlight_intensity};")
        css_vars.append(f"--nt-opacity: {texture.opacity};")
        css_vars.append(f"--nt-border-width: {texture.border_width}px;")
        
        self._inject_css_vars(css_vars)
        
        if texture.css:
             ui.add_head_html(f"<style>{texture.css}</style>")


    def _apply_layout(self, layout: Layout):
        css_vars = []
        # Roundness factor - can be used as a multiplier for px values
        css_vars.append(f"--nt-roundness: {layout.roundness};")
        # Density - can be used for spacing multipliers
        css_vars.append(f"--nt-density: {layout.density};")
        
        self._inject_css_vars(css_vars)

    def _apply_typography(self, typography: Typography):
        css_vars = []
        css_vars.append(f"--nt-font-primary: {typography.primary};")
        css_vars.append(f"--nt-font-secondary: {typography.secondary};")
        css_vars.append(f"--nt-font-scale: {typography.scale};")
        
        if typography.title_case:
             # Map 'title_case' enum to CSS values
             transform_map = {
                 "lowercase": "lowercase",
                 "uppercase": "uppercase",
                 "title_case": "capitalize", # capitalize is closest to title case in CSS
                 "none": "none"
             }
             val = transform_map.get(typography.title_case, "none")
             css_vars.append(f"--nt-text-transform-title: {val};")

        self._inject_css_vars(css_vars)

    def _inject_css_vars(self, vars_list: List[str]):
        """Helper to inject a list of CSS variables into :root"""
        styles = ":root {\n  " + "\n  ".join(vars_list) + "\n}"
        ui.add_head_html(f"<style>{styles}</style>")

    def _inject_static_styles(self):
        """Injects static CSS files."""
        # Assume assets/icons.css is relative to this file's package structure
        import os
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(current_dir), 'assets')
        icons_css_path = os.path.join(assets_dir, 'icons.css')
        
        if os.path.exists(icons_css_path):
            with open(icons_css_path, 'r') as f:
                css_content = f.read()
            ui.add_head_html(f"<style>{css_content}</style>")
        else:
            print(f"Warning: icons.css not found at {icons_css_path}")

        sliders_css_path = os.path.join(assets_dir, 'sliders.css')
        if os.path.exists(sliders_css_path):
            with open(sliders_css_path, 'r') as f:
                css_content = f.read()
            ui.add_head_html(f"<style>{css_content}</style>")
        else:
            print(f"Warning: sliders.css not found at {sliders_css_path}")

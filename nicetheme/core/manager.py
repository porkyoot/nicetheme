from nicegui import ui
from typing import Dict, List
from .themes import Theme, Palette, Texture, Layout, Typography

class ThemeManager:
    """
    Manages the application of themes to the NiceGUI app.
    Translates Theme objects into NiceGUI colors, CSS variables, and other settings.
    """

    def apply(self, theme: Theme):
        """
        Applies the given theme to the application.
        """
        self._apply_palette(theme.palette)
        self._apply_texture(theme.texture)
        self._apply_layout(theme.layout)
        self._apply_typography(theme.typography)

    def _apply_palette(self, palette: Palette):
        # 1. Update Quasar/NiceGUI brand colors
        ui.colors(
            primary=palette.primary,
            secondary=palette.secondary,
            positive=palette.positive,
            negative=palette.negative,
            warning=palette.warning,
            info=palette.info,
            accent=palette.content[0] if palette.content else palette.primary, # Fallback/Mapping
        )

        # 2. Generate CSS variables for the palette
        css_vars = []
        
        # Brand colors
        css_vars.append(f"--nt-primary: {palette.primary};")
        css_vars.append(f"--nt-secondary: {palette.secondary};")
        css_vars.append(f"--nt-positive: {palette.positive};")
        css_vars.append(f"--nt-negative: {palette.negative};")
        css_vars.append(f"--nt-warning: {palette.warning};")
        css_vars.append(f"--nt-info: {palette.info};")
        
        # Surface colors
        # Assuming list format: [page, dark, light]
        if len(palette.surface) >= 1:
            css_vars.append(f"--nt-surface-page: {palette.surface[0]};")
        if len(palette.surface) >= 2:
            css_vars.append(f"--nt-surface-dark: {palette.surface[1]};")
        if len(palette.surface) >= 3:
            css_vars.append(f"--nt-surface-light: {palette.surface[2]};")

        # Content colors
        # Assuming list format: [accent, darker]
        if len(palette.content) >= 1:
            css_vars.append(f"--nt-content-accent: {palette.content[0]};")
        if len(palette.content) >= 2:
            css_vars.append(f"--nt-content-dark: {palette.content[1]};")
            
        # Custom colors
        css_vars.append(f"--nt-inactive: {palette.inative};")
        for name, color in palette.colors.items():
             css_vars.append(f"--nt-color-{name}: {color};")

        # Inject CSS variables
        self._inject_css_vars(css_vars)

    def _apply_texture(self, texture: Texture):
        css_vars = []
        css_vars.append(f"--nt-shadow-color: {texture.shadow};")
        css_vars.append(f"--nt-shadow-intensity: {texture.shadow_intensity};")
        css_vars.append(f"--nt-highlight-color: {texture.highlight};")
        css_vars.append(f"--nt-highlight-intensity: {texture.highlight_intensity};")
        css_vars.append(f"--nt-opacity: {texture.opacity};")
        
        # Inject CSS variables
        self._inject_css_vars(css_vars)
        
        # Quasar/Other CSS overrides if needed
        # (e.g., overriding generic shadow classes if texture.css is provided or needed)
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
        
        # Text transform logic could be handled via class helpers or global reset
        # For now, we'll just expose it as a variable if helpful, or specific CSS
        if typography.title_case:
             # Map 'title_case' enum to CSS values
             transform_map = {
                 "lowercase": "lowercase",
                 "uppercase": "uppercase",
                 "title_case": "capitalize", # capitalize is closest to title case in CSS
                 None: "none"
             }
             val = transform_map.get(typography.title_case, "none")
             css_vars.append(f"--nt-text-transform-title: {val};")

        self._inject_css_vars(css_vars)

    def _inject_css_vars(self, vars_list: List[str]):
        """Helper to inject a list of CSS variables into :root"""
        styles = ":root {\n  " + "\n  ".join(vars_list) + "\n}"
        ui.add_head_html(f"<style>{styles}</style>")

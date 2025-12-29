import os
import yaml
from typing import Dict, Optional
from pathlib import Path
from nicegui import app
from .themes import Palette, Texture, Layout, Theme, Typography

class ThemeRegistry:
    """
    Scans and registers theme components (palettes, textures, layouts, fonts) from a directory.
    """

    def __init__(self, themes_dir: Optional[Path]):
        if themes_dir is None:
            # Default to 'themes' directory within the package if not provided
            # Assuming this file is in nicetheme/core/registry.py, go up two levels
            self.themes_dir = Path(__file__).parent.parent / "themes"
        
        self.palettes: Dict[str, Dict[str, Palette]] = {}
        self.textures: Dict[str, Texture] = {}
        self.layouts: Dict[str, Layout] = {}
        self.fonts: Dict[str, str] = {} # Name -> Relative Path or URL
        self.font_files: Dict[str, Path] = {} # Name -> Absolute Path
        self.themes: Dict[str, Theme] = {}

        self.scan()

    def scan(self):
        """Scans the themes directory for components."""
        if not self.themes_dir.exists():
            return

        self._scan_palettes(self.themes_dir / "palettes")
        self._scan_textures(self.themes_dir / "textures")
        self._scan_layouts(self.themes_dir / "layouts")
        self._scan_fonts(self.themes_dir / "fonts")

        self._scan_themes(self.themes_dir)

    def _scan_palettes(self, path: Path):
        if not path.exists(): return
        for file in path.glob("*.yaml"):
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    
                    # Handle 'palette' root key if present
                    if 'palette' in data:
                        data = data['palette']
                    
                    # Extract common and specific fields
                    common = data.copy()
                    dark_spec = common.pop('dark', {})
                    light_spec = common.pop('light', {})
                    
                    # Create Dark Palette
                    # Merge logic: dark_spec overrides common
                    dark_data = common.copy()
                    dark_data.update(dark_spec)
                    dark_data['mode'] = 'dark'
                    dark_palette = Palette(**dark_data)
                    
                    # Create Light Palette
                    # Merge logic: light_spec overrides (common merged with dark??)
                    # YAML said: "light: inherit from the dark for undefined fields"
                    # So Light Base = Dark Data (which is Common + Dark Overrides)
                    light_data = dark_data.copy()
                    # We need to remove 'mode' before update or overwrite it later
                    # Update with light spec
                    light_data.update(light_spec)
                    light_data['mode'] = 'light'
                    light_palette = Palette(**light_data)

                    self.palettes[file.stem] = {
                        'light': light_palette,
                        'dark': dark_palette
                    }
            except Exception:
                pass

    def _scan_textures(self, path: Path):
        if not path.exists(): return
        for file in path.glob("*.yaml"):
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    self.textures[file.stem] = Texture(**data)
            except Exception:
                pass

    def _scan_layouts(self, path: Path):
        if not path.exists(): return
        for file in path.glob("*.yaml"):
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    self.layouts[file.stem] = Layout(**data)
            except Exception:
                pass

    def _scan_fonts(self, path: Path):
        if not path.exists(): return
        
        # Serve the fonts directory statically so we can refer to them in CSS
        app.add_static_files("/fonts", str(path))

        for file in path.glob("*.*"):
            if file.suffix.lower() in [".otf", ".ttf", ".woff", ".woff2"]:
                # Registering the font name and its URL for usage
                # Assuming the user wants to reference them by filename stem
                self.fonts[file.stem] = f"/fonts/{file.name}"
                self.font_files[file.stem] = file

    def _scan_themes(self, path: Path):
        if not path.exists(): return
        for file in path.glob("*.yaml"):
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    
                    # Resolve texture and layout references
                    texture_name = data.get('texture')
                    layout_name = data.get('layout')
                    
                    # Ensure texture and layout are never None
                    default_texture = Texture(
                        shadow_intensity=0.2, highlight_intensity=0.1, opacity=1.0, blur=0
                    )
                    default_layout = Layout(
                        roundness=0.5, density=0.5, border=1.0
                    )
                    
                    texture = self.textures.get(texture_name, default_texture) if texture_name else default_texture
                    layout = self.layouts.get(layout_name, default_layout) if layout_name else default_layout
                    
                    # Create theme with resolved components
                    theme = Theme(
                        palette=data.get('palette', 'tailwind'),
                        texture_name=texture_name or 'default',
                        texture=texture,
                        layout_name=layout_name or 'default',
                        layout=layout,
                        typography=Typography(**data.get('typography', {
                            'primary': 'sans-serif',
                            'secondary': 'sans-serif',
                            'mono': 'monospace',
                            'scale': 1.0,
                            'title_case': 'none'
                        }))
                    )
                    self.themes[file.stem] = theme
            except Exception:
                pass
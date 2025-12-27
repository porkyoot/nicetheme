import os
import yaml
from typing import Dict, Optional
from pathlib import Path
from nicegui import app
from .themes import Palette, Texture, Layout, Typography

class ThemeRegistry:
    """
    Scans and registers theme components (palettes, textures, layouts, fonts) from a directory.
    """

    def __init__(self, themes_dir: Optional[Path]):
        if themes_dir is None:
            # Default to 'themes' directory within the package if not provided
            # Assuming this file is in nicetheme/core/registry.py, go up two levels
            self.themes_dir = Path(__file__).parent.parent / "themes"
        
        self.palettes: Dict[str, Palette] = {}
        self.textures: Dict[str, Texture] = {}
        self.layouts: Dict[str, Layout] = {}
        self.fonts: Dict[str, str] = {} # Name -> Relative Path or URL
        self.font_files: Dict[str, Path] = {} # Name -> Absolute Path

        self.scan()

    def scan(self):
        """Scans the themes directory for components."""
        if not self.themes_dir.exists():
            print(f"Theme directory {self.themes_dir} does not exist.")
            return

        self._scan_palettes(self.themes_dir / "palettes")
        self._scan_textures(self.themes_dir / "textures")
        self._scan_layouts(self.themes_dir / "layouts")
        self._scan_fonts(self.themes_dir / "fonts")

    def _scan_palettes(self, path: Path):
        if not path.exists(): return
        for file in path.glob("*.yaml"):
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    # Basic validation/mapping could go here. 
                    # Ideally we use dacite or pydantic, but simple dict unfolding works for now if keys match.
                    self.palettes[file.stem] = Palette(**data)
            except Exception as e:
                print(f"Error loading palette {file.name}: {e}")

    def _scan_textures(self, path: Path):
        if not path.exists(): return
        for file in path.glob("*.yaml"):
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    self.textures[file.stem] = Texture(**data)
            except Exception as e:
                print(f"Error loading texture {file.name}: {e}")

    def _scan_layouts(self, path: Path):
        if not path.exists(): return
        for file in path.glob("*.yaml"):
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    self.layouts[file.stem] = Layout(**data)
            except Exception as e:
                print(f"Error loading layout {file.name}: {e}")

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

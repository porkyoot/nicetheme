from dataclasses import dataclass, field
from typing import Literal, Dict, List, Optional



@dataclass
class Palette:
    name: str
    mode: Literal["light", "dark"]
    colors: Dict[str, str]
    greys: Dict[str, str]
    
    primary: str
    secondary: str
    positive: str
    negative: str
    warning: str
    info: str
    debug: str
    inative: str
    
    content: List[str]
    surface: List[str]
    shadow: str
    highlight: str
    border: str

    def resolve_color(self, color_ref: str) -> str:
        """Resolves a color reference (name) to a hex code or value."""
        if not color_ref: return ""
        if color_ref.startswith("#") or color_ref.startswith("rgb") or color_ref.startswith("hsl"): 
            return color_ref
        
        # Check colors
        if color_ref in self.colors:
            return self.colors[color_ref]
            
        # Check greys
        if color_ref in self.greys:
            return self.greys[color_ref]
            
        return color_ref # Fallback if not found

@dataclass
class Texture:
    shadow_intensity: float
    highlight_intensity: float
    opacity: float
    border_width: float
    css: str = ""

@dataclass
class Layout:
    roundness: float
    density: float

@dataclass
class Typography:
    primary: str
    secondary: str
    scale: float
    title_case: Literal["lowercase", "title_case", "uppercase", "none"]

@dataclass
class Theme:
    palettes: Dict[str, Palette]
    texture: Texture
    layout: Layout
    typography: Typography

    @property
    def palette(self) -> Palette:
        return self.palettes.get('light') or next(iter(self.palettes.values()))
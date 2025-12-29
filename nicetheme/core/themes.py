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

    def resolve_color(self, color_ref: str, depth: int = 10) -> str:
        """Resolves a color reference (name) to a hex code or value."""
        if not color_ref: return ""
        if depth <= 0: return color_ref

        # Check if valid CSS value
        if color_ref.startswith(("#", "rgb", "hsl", "var")):
            return color_ref
        
        # Check colors
        if color_ref in self.colors:
            return self.resolve_color(self.colors[color_ref], depth - 1)
            
        # Check greys
        if color_ref in self.greys:
            return self.resolve_color(self.greys[color_ref], depth - 1)

        # Check attributes (like primary, secondary)
        val = getattr(self, color_ref, None)
        if isinstance(val, str):
            return self.resolve_color(val, depth - 1)
            
        return color_ref # Fallback

@dataclass
class Texture:
    shadow_intensity: float
    highlight_intensity: float
    opacity: float
    blur: int
    button: str = ""
    card: str = ""
    progress: str = ""
    slider: str = ""
    toggle: str = ""
    chip: str = ""  # Also applies to badges
    menu: str = ""  # Also applies to tooltips and notifications

@dataclass
class Layout:
    roundness: float
    density: float
    border: float

@dataclass
class Typography:
    primary: str
    secondary: str
    mono: str
    scale: float
    title_case: Literal["lowercase", "title_case", "uppercase", "none"]

@dataclass
class Theme:
    palette: str  # Name of the palette to use
    texture: Texture
    layout: Layout
    typography: Typography
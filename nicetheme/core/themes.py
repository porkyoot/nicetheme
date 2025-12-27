import enum
from dataclasses import dataclass, field
from typing import Literal, Dict, List, Optional

@dataclass
class Palette:
    primary: str
    secondary: str
    content: List[str] #accent then darker
    surface: List[str] #dark_page, dark then lighter
    positive: str #success
    negative: str #error
    warning: str #warning
    info: str #info
    debug: str #debug

    #Custom Colors
    inative: str # grey
    colors: Dict[str, str] #must define at least one color for each of blue, cyan, green, yellow, orange, red, magenta, violet
    custom_colors: Dict[str, List[str]] #name -> colors by order of lightness for a given hue
    
@dataclass
class Texture:
    shadow: str
    shadow_intensity: float
    highlight: str
    highlight_intensity: float
    opacity: float
    
    css: str # see quasar styling for details ?

@dataclass
class Layout:
    roundness: float
    density: float

@dataclass
class Typography:
    primary: str
    secondary: str
    scale: float
    title_case: Literal["lowercase", "title_case", "uppercase"] # + None for no modifications

@dataclass
class Theme:
    palette: Palette
    texture: Texture
    layout: Layout
    typography: Typography
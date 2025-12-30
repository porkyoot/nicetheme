from typing import Callable, List, Literal, Optional
from .themes import Theme, Palette
from .registry import ThemeRegistry

class ThemeManager:
    """
    PURE BACKEND: Manages the state of the theme. 
    Does NOT know about HTML, CSS injection, or the browser.
    """
    def __init__(self, themes_dirs: Optional[List] = None):
        self._registry = ThemeRegistry(themes_dirs=themes_dirs)  # Use provided themes directories
        self._theme_name: str = 'default'
        self._theme: Optional[Theme] = self._registry.themes.get(self._theme_name)
        self._active_palette_name: str = self._theme.palette if self._theme else 'solarized'
        self._mode: Literal['light', 'dark', 'auto'] = 'auto'  # Default to auto (browser detect)
        self._listeners: List[Callable[['ThemeManager'], None]] = []

    def bind(self, callback: Callable[['ThemeManager'], None]):
        """Registers a listener (The Bridge or UI)"""
        self._listeners.append(callback)

    def unbind(self, callback: Callable[['ThemeManager'], None]):
        """Unregisters a listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self):
        for listener in self._listeners:
            listener(self)

    # --- Actions ---
    
    def apply_theme(self, theme: Theme, name: str = 'unknown'):
        self._theme = theme
        self._theme_name = name
        self._notify()

    def select_theme(self, name: str):
        """Loads a theme by name from the registry"""
        theme = self._registry.themes.get(name)
        if theme:
            self._theme = theme
            self._theme_name = name
            # Refresh palette name from new theme
            self._active_palette_name = theme.palette
            self._notify()

    def set_mode(self, mode: Literal['light', 'dark', 'auto']):
        self._mode = mode
        self._notify()

    def set_palette(self, name: str):
        self._active_palette_name = name
        if self._theme:
            self._theme.palette = name
        self._notify()
        
    def refresh(self):
        """Force a notification to update listeners (useful if generic properties changed)"""
        self._notify()

    def update_primary_color(self, color: str):
        # Logic to update specific part of the data model
        current_palette = self.get_active_palette()
        if current_palette:
            current_palette.primary = color
            self._notify()

    def update_secondary_color(self, color: str):
        # Logic to update secondary accent color
        current_palette = self.get_active_palette()
        if current_palette:
            current_palette.secondary = color
            self._notify()

    # --- Getters (Computed Properties) ---

    def get_effective_mode(self) -> str:
        if self._mode == 'auto':
            # When in auto mode, check the detected browser preference
            # This will be set by JavaScript media query detection
            return getattr(self, '_detected_mode', 'light')
        return self._mode
    
    def set_detected_mode(self, mode: Literal['light', 'dark']):
        """Sets the detected browser preference (called from JavaScript)"""
        self._detected_mode = mode
        if self._mode == 'auto':
            # Only notify if we're actually in auto mode
            self._notify()

    def apply_preferences(self, prefs: dict):
        """Applies a batch of preferences (e.g. from localStorage)"""
        if 'mode' in prefs: self._mode = prefs['mode']
        if 'palette' in prefs: 
            self._active_palette_name = prefs['palette']
            if self._theme: self._theme.palette = prefs['palette']
        
        if self._theme:
            if 'texture' in prefs: 
                self._theme.texture_name = prefs['texture']
                tex = self._registry.textures.get(prefs['texture'])
                if tex: self._theme.texture = tex
                
            if 'layout' in prefs: 
                self._theme.layout_name = prefs['layout']
                lay = self._registry.layouts.get(prefs['layout'])
                if lay: self._theme.layout = lay
            
            if 'typography' in prefs:
                typo_refs = prefs['typography']
                if self._theme.typography:
                    for k, v in typo_refs.items():
                        if hasattr(self._theme.typography, k):
                            setattr(self._theme.typography, k, v)
        
        # Palette overrides (active palette)
        if 'palette_overrides' in prefs:
            p = self.get_active_palette()
            if p:
                for k, v in prefs['palette_overrides'].items():
                    if hasattr(p, k):
                        setattr(p, k, v)
        
        self._notify()

    def get_active_palette(self) -> Optional[Palette]:
        if not self._theme: return None
        # Get the palette name from the theme
        palette_name = self._theme.palette
        # Get the palette from the registry
        palettes = self._registry.palettes.get(palette_name)
        if not palettes: return None
        return palettes.get(self.get_effective_mode())
    
    @property
    def theme_name(self) -> str:
        return self._theme_name

    @property
    def theme(self) -> Optional[Theme]:
        return self._theme

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def active_palette_name(self) -> str:
        return self._active_palette_name

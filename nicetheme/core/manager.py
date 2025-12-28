from typing import Callable, List, Literal, Optional
from .themes import Theme, Palette

class ThemeManager:
    """
    PURE BACKEND: Manages the state of the theme. 
    Does NOT know about HTML, CSS injection, or the browser.
    """
    def __init__(self):
        self._theme: Optional[Theme] = None
        self._active_palette_name: str = 'solarized'
        self._mode: Literal['light', 'dark', 'auto'] = 'light'
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
    
    def apply_theme(self, theme: Theme):
        self._theme = theme
        self._notify()

    def set_mode(self, mode: Literal['light', 'dark', 'auto']):
        self._mode = mode
        self._notify()

    def set_palette(self, name: str):
        self._active_palette_name = name
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
            return 'light' # Add system detection logic here if needed
        return self._mode

    def get_active_palette(self) -> Optional[Palette]:
        if not self._theme: return None
        palettes = self._theme.palettes.get(self._active_palette_name)
        if not palettes: return None
        return palettes.get(self.get_effective_mode())
    
    @property
    def theme(self) -> Optional[Theme]:
        return self._theme

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def active_palette_name(self) -> str:
        return self._active_palette_name

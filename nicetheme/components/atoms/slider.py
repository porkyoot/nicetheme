from nicegui import ui
from typing import Optional, Callable, Any, Dict

class slider(ui.slider):
    """
    Standard slider component aligned with Nice Design system.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We keep 'label' as a functional default for the design system
        # Quasar 'primary' color is now globally defaulted in ThemeManager
        self.props('label')
        self.classes('w-full')





class split_slider(ui.element):
    """
    A unified slider component with TWO distinct handles, splitting from a central zero.
    Controls TWO independent values (Left Value and Right Value).
    
    Structure:
    [ Left Slider (Max -> 0) ] | [ Right Slider (0 -> Max) ]
    
    The Left Slider is visually reversed so that its '0' is at the right end (center of component).
    """
    def __init__(self,
                 limit: float = 2.0,
                 step: float = 0.1,
                 value_left: float = 0.0,
                 value_right: float = 0.0,
                 color_left: str = 'primary',
                 color_right: str = 'secondary',
                 on_change: Optional[Callable[[Dict[str, float]], None]] = None):
        super().__init__('div')
        self.classes('relative-position w-full flex items-center justify-center my-1 gap-0 row no-wrap')
        # self.style('height: 40px;') 

        self._limit = limit
        self._step = step
        self._value_left = value_left
        self._value_right = value_right
        self._color_left = color_left
        self._color_right = color_right
        self._on_change = on_change
        
        with self:
            # --- Left Side Container ---
            with ui.row().classes('col flex items-center justify-end relative-position px-0').style('height: 32px;'):
                # Left Slider (Reverse Mode)
                self.slider_left = ui.slider(min=0, max=limit, step=step, value=value_left, on_change=self._handle_change_left)
                # 'reverse' prop makes 0 be at the right side.
                self.slider_left.props(f'reverse label track-size="4px" thumb-size="16px" :label-value="modelValue.toFixed(1)"')
                
                # Apply color (handle hex or var)
                if color_left.startswith('#') or color_left.startswith('var('):
                    self.slider_left.props(f':active-color="\'{color_left}\'" :thumb-color="\'{color_left}\'" :track-color="\'{color_left}\'"')
                else:
                    self.slider_left.props(f'color="{color_left}"')
                
                self.slider_left.classes('w-full')
                
            # --- Center Divider ---
            ui.element('div').classes('bg-grey-4').style('width: 2px; height: 12px; z-index: 10;')

            # --- Right Side Container ---
            with ui.row().classes('col flex items-center justify-start relative-position px-0').style('height: 32px;'):
                # Right Slider (Normal Mode)
                self.slider_right = ui.slider(min=0, max=limit, step=step, value=value_right, on_change=self._handle_change_right)
                self.slider_right.props(f'label track-size="4px" thumb-size="16px" :label-value="modelValue.toFixed(1)"')
                
                # Apply color (handle hex or var)
                if color_right.startswith('#') or color_right.startswith('var('):
                    self.slider_right.props(f':active-color="\'{color_right}\'" :thumb-color="\'{color_right}\'" :track-color="\'{color_right}\'"')
                else:
                    self.slider_right.props(f'color="{color_right}"')
                
                self.slider_right.classes('w-full')

    def _handle_change_left(self, e):
        self._value_left = e.value
        self._notify()

    def _handle_change_right(self, e):
        self._value_right = e.value
        self._notify()
        
    def _notify(self):
        if self._on_change:
            self._on_change({'left': self._value_left, 'right': self._value_right})

    def set_colors(self, color_left: str, color_right: str):
        """Updates the colors of the sliders."""
        self._color_left = color_left
        self._color_right = color_right
        
        for s, c in [(self.slider_left, color_left), (self.slider_right, color_right)]:
            # Clear old color props
            # Quasar props are additive in NiceGUI unless we are careful, 
            # but setting color="new" or :active-color="new" usually overrides.
            if c.startswith('#') or c.startswith('var('):
                s.props(f':active-color="\'{c}\'" :thumb-color="\'{c}\'" :track-color="\'{c}\'"')
            else:
                s.props(f'color="{c}"')


class palette_slider(ui.element):
    """
    A horizontal color selection bar resembling a slider.
    Displays a set of colors and emphasizes the selected one by expanding it.
    Ideal for selecting a color from a palette (e.g., 8 accent colors).
    """
    def __init__(self, 
                 colors: Dict[str, str],
                 value: str,
                 on_change: Optional[Callable[[str], None]] = None):
        super().__init__('div')
        self.classes('relative w-full nt-palette-slider-container')
        self.style('height: 32px;') # Ensure container has height
        
        self._color_list = list(colors.values())
        self._color_names = list(colors.keys())
        self._on_change = on_change
        
        # Initial index
        try:
            initial_index = self._color_list.index(value)
        except ValueError:
            initial_index = 0
            
        with self:
            # The Overlay (Lower Z-Index)
            self._overlay = ui.element('div').classes('nt-palette-slider-overlay')
            with self._overlay:
                self._render_items(initial_index)
            
            # The Slider (Higher Z-Index, Transparent Track)
            self._slider = ui.slider(min=0, max=max(0, len(self._color_list) - 1), value=initial_index)
            self._slider.classes('absolute-full nt-palette-slider')
            self._slider.props('track-size=0px height=32px') # Match container height
            self._slider.on_value_change(self._handle_slider_change)

    @property
    def value(self) -> int:
        return self._slider.value

    @value.setter
    def value(self, v: int):
        self._slider.value = v

    def _render_items(self, current_index: int):
        self._items = []
        for i, color in enumerate(self._color_list):
            is_selected = (i == current_index)
            flex_val = '4' if is_selected else '1'
            
            item = ui.element('div').classes('h-full transition-all duration-300 ease-out relative')
            item.style(f'background-color: {color}; flex: {flex_val};')
            
            # Selection indicator
            if is_selected:
                self._inject_indicator(item)
            
            self._items.append(item)

    def _inject_indicator(self, container):
        with container:
             ui.element('div').classes('absolute-center w-1.5 h-1.5 rounded-full bg-white/90 ring-1 ring-black/10').style('box-shadow: var(--nd-shadow-sm);')

    def _handle_slider_change(self, e):
        self._update_selection_visuals(int(e.value))
        if self._on_change:
            self._on_change(self._color_list[int(e.value)])

    def set_colors(self, colors: Dict[str, str], value: Optional[str] = None):
        """Updates the available colors and optionally the current value."""
        self._color_list = list(colors.values())
        self._color_names = list(colors.keys())
        
        self._slider.props(f'max={max(0, len(self._color_list) - 1)}')
        
        if value:
            try:
                self._slider.value = self._color_list.index(value)
            except ValueError:
                self._slider.value = 0
        elif self._slider.value >= len(self._color_list):
            self._slider.value = 0
            
        self._overlay.clear()
        with self._overlay:
            self._render_items(int(self._slider.value))

    def _update_selection_visuals(self, current_index: int):
        """Updates the transition and selection indicators without full re-render."""
        for i, item in enumerate(self._items):
            item.clear()
            if i == current_index:
                item.style(f'flex: 4;')
                self._inject_indicator(item)
            else:
                item.style(f'flex: 1;')


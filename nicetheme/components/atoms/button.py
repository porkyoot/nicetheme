from nicegui import ui
from typing import Optional, Literal, Union, Callable

# Mirroring NiceGUI's API structure
class button(ui.button):
    def __init__(
        self, 
        text: str = '', 
        variant: Literal['primary', 'secondary', 'ghost'] = 'primary',
        icon: Optional[str] = None,
        on_click = None,
        rotate_icon: bool = False,
        *args, **kwargs
    ):
        super().__init__(text, icon=icon, on_click=on_click, *args, **kwargs)
        
        if variant == 'secondary':
            self.props('color=secondary')
            
        elif variant == 'ghost':
            self.props('outline color=primary')
            
        # Handle rotate_icon logic with a semantic class
        if rotate_icon:
            self.classes('nt-btn-rotate')
            self.on('click', lambda: self.classes(toggle='nt-btn-rotated'))

class select_button(ui.element):
    """
    A button styled exactly like a Select component (using q-field).
    Useful for triggering menus or other interactions while maintaining the Select visual language.
    Contains logic for toggling the chevron rotation.
    """
    def __init__(self, 
                 label: str = '', 
                 icon: Optional[str] = None, 
                 icon_right: str = 'arrow_drop_down', 
                 icon_only: bool = False, 
                 custom_icon_builder: Optional[Callable] = None,
                 on_click: Optional[Callable] = None,
                 *args, **kwargs):
        
        super().__init__('q-field', *args, **kwargs)
        
        self.classes('cursor-pointer nt-select-button')
        self.props('borderless' if kwargs.get('borderless') else '') # Allow borderless override
        
        # Ensure label text doesn't float into the label position, but sits in the control (value) slot
        self._label_text = label
        self._icon_only = icon_only
        self._custom_icon_builder = custom_icon_builder
        
        # Internal state for rotation
        self._is_rotated = False

        # Build Slots
        self._update_slots(icon, icon_right)
        
        # Bind click - q-field has a native click event we can capture on the element
        # We wrap the on_click to allow rotation toggling
        if on_click:
            self.on('click', lambda e: (self.toggle_rotation(), on_click(e)))
        else:
             self.on('click', self.toggle_rotation)

    def _update_slots(self, icon, icon_right):
        # Main Content (Icon + Label)
        # We place both in 'control' slot to match the behavior of selected-item in ui.select
        # This ensures the icon has full opacity/color like the text, not the washed out 'prepend' style
        with self.add_slot('control'):
            with ui.element('div').classes('q-field__native row items-center gap-2'):
                if icon:
                    ui.icon(icon, size='sm')
                if self._label_text:
                    self._label_element = ui.label(self._label_text)
                    
        # Custom Icon Builder (Usually for complex icons on the left/center)
        if self._custom_icon_builder:
             with self.add_slot('prepend'): # Keep custom builder in prepend for now unless specified otherwise
                  self._custom_icon_builder()
        
        # Append Icon (Dropdown arrow)
        if icon_right:
            with self.add_slot('append'):
                self._icon_right_element = ui.icon(icon_right).classes('transition-transform duration-300')

    def set_label(self, text: str):
        self._label_text = text
        if hasattr(self, '_label_element'):
            self._label_element.text = text

    def toggle_rotation(self):
        """Toggles the rotation state of the right icon."""
        self._is_rotated = not self._is_rotated
        self._update_rotation_class()
        
    def reset_rotation(self):
        """Resets rotation to default (0 deg). Useful when menu closes."""
        self._is_rotated = False
        self._update_rotation_class()
        
    def _update_rotation_class(self):
        if hasattr(self, '_icon_right_element'):
            if self._is_rotated:
                self._icon_right_element.classes('rotate-180')
            else:
                self._icon_right_element.classes(remove='rotate-180')
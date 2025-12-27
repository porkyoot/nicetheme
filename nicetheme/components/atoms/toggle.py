from nicegui import ui
from typing import Dict, Any, Optional, List, Union

class toggle(ui.toggle):
    def __init__(self, options: Union[List, Dict], color_map: Optional[Dict[Any, str]] = None, **kwargs):
        """
        A toggle component that supports different active colors per option and rich option structures.
        
        :param options: Dictionary of options {value: label} OR List of values OR List of dicts (Quasar style).
        :param color_map: Dictionary mapping values to NiceGUI/Quasar color names.
        """
        self._raw_options = options
        
        # Prepare options for NiceGUI validation (must be keys/values only)
        # If options is a list of complex dicts (e.g. [{'label':..., 'value':...}]), 
        # NiceGUI's ChoiceElement will choke on validation if valid values aren't extracted.
        validation_options = options
        if isinstance(options, list) and options and isinstance(options[0], dict):
            # Extract just the values for the backend validator
            validation_options = [opt.get('value') for opt in options if 'value' in opt]

        super().__init__(validation_options, **kwargs)

        # Restore the full rich options for the frontend prop
        if validation_options != options:
             self._props['options'] = options
        
        self._color_map = color_map or {}
        
        if self._color_map:
            self.on_value_change(self._update_color)
            # Initial color set
            self._update_color()
            
    def _update_values_and_labels(self) -> None:
        """
        Extract values and labels from rich options if they exist.
        """
        if hasattr(self, '_raw_options') and isinstance(self._raw_options, list) and self._raw_options and isinstance(self._raw_options[0], dict):
             self._values = [opt.get('value') for opt in self._raw_options]
             self._labels = [opt.get('label', '') for opt in self._raw_options]
        else:
             super()._update_values_and_labels()

    def _update_options(self) -> None:
        """
        Override ChoiceElement behavior to include rich metadata in Quasar options.
        NiceGUI's Toggle uses indices as the 'value' prop for q-btn-toggle.
        We preserve this but merge in our rich metadata.
        """
        if hasattr(self, '_raw_options') and isinstance(self._raw_options, list) and self._raw_options and isinstance(self._raw_options[0], dict):
            # Mix our rich data with the required index-based values
            self._props['options'] = [
                {**opt, 'value': i} 
                for i, opt in enumerate(self._raw_options)
            ]
            self._props[self.VALUE_PROP] = self._value_to_model_value(self.value)
        else:
            super()._update_options()

    def _update_color(self):
        if self.value in self._color_map:
             self.props(f'toggle-color={self._color_map[self.value]}')
        else:
             # revert to default if no specific color mapped, or handle as needed
             # For now, we assume if color_map is used, all values might want one, 
             # or we let Quasar's default take over (which might be primary).
             pass 

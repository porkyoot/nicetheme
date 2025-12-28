from nicegui import ui
from typing import Any, Optional, Callable

class select(ui.select):
    def __init__(self, 
                 options: Any, 
                 icon_only: bool = False, 
                 prepend: Optional[Callable] = None,
                 on_filter: Optional[Callable] = None,
                 *args, **kwargs):
        
        # Remove deprecated parameter
        kwargs.pop('with_icons', None)
        
        # Normalize list of dicts to dict for NiceGUI
        if isinstance(options, list) and options and isinstance(options[0], dict):
            options = {(opt.get('value') or opt.get('label')): opt for opt in options if opt.get('value') or opt.get('label')}

        # Extract value from dict if passed
        if 'value' in kwargs and isinstance(kwargs['value'], dict):
            kwargs['value'] = kwargs['value'].get('value') or kwargs['value'].get('label')

        super().__init__(options, *args, **kwargs)
        
        # Detect if options have rich metadata (icon, html, font)
        is_rich = False
        if options:
            first = next(iter(options.values())) if isinstance(options, dict) else options[0]
            is_rich = isinstance(first, dict) and any(k in first for k in ['icon', 'html', 'font'])
        
        # Setup rich slots if needed
        if is_rich:
            self._setup_rich_slots()
            self.props(r':option-label="(opt) => opt.label && opt.label.label ? opt.label.label : (opt.label || opt)"')
            
        # Apply structural props
        self.props('popup-content-class="nd-select-menu"')
        
        # Setup search/filter
        if on_filter:
            self._on_filter_cb = on_filter
            self.props('use-input input-debounce="0"')
            self.on('input-value', self._handle_filter)
            self.on('click', self._handle_click)

        # Icon-only mode
        if icon_only:
            self.classes('nd-hide-label nd-mode-icon-only')
            
        # Prepend slot
        if prepend:
            with self.add_slot('prepend'):
                prepend()

    def _setup_rich_slots(self):
        """Setup Vue slots for rich options with icons, fonts, and HTML"""
        self.add_slot('option', r'''
            <q-item v-bind="props.itemProps">
                <q-item-section avatar v-if="props.opt.label.icon || props.opt.label.html">
                    <div v-if="props.opt.label.html" v-html="props.opt.label.html"></div>
                    <q-icon v-else :name="props.opt.label.icon" :color="props.opt.label.color" size="sm" />
                </q-item-section>
                <q-item-section>
                    <q-item-label :style="props.opt.label.font ? { 'font-family': props.opt.label.font } : {}">
                        {{ props.opt.label.label }}
                    </q-item-label>
                </q-item-section>
            </q-item>
        ''')

        self.add_slot('selected-item', r'''
            <div class="row items-center no-wrap gap-2" v-if="props.opt && props.opt.label">
                <div v-if="props.opt.label.html" v-html="props.opt.label.html"></div>
                <q-icon v-else-if="props.opt.label.icon" :name="props.opt.label.icon" :color="props.opt.label.color" size="sm" />
                <q-item-label :style="props.opt.label.font ? { 'font-family': props.opt.label.font } : {}">
                    {{ props.opt.label.label }}
                </q-item-label>
            </div>
        ''')

    def _handle_click(self, e):
        """Clear input and show all options on click"""
        self.run_method('updateInputValue', '')
        self._do_filter('')

    def _handle_filter(self, e):
        """Handle server-side filtering when user types"""
        val = (e.args if isinstance(e.args, str) else "").lower()
        self._do_filter(val)

    def _do_filter(self, val):
        """Execute filter callback and update options"""
        new_opts = self._on_filter_cb(val)
        
        # Normalize if callback returned a list
        if isinstance(new_opts, list) and new_opts and isinstance(new_opts[0], dict):
            new_opts = {(opt.get('value') or opt.get('label')): opt for opt in new_opts if opt.get('value') or opt.get('label')}
        
        self.options = new_opts
        self.update()
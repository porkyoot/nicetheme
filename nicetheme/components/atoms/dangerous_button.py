from nicegui import ui
from typing import Callable
from .button import button

class DangerousButton(ui.element):
    def __init__(
        self, 
        icon: str, 
        on_click: Callable, 
        color: str,
        hold_time: float = 1.5,
        tooltip: str = "Hold to confirm",
        size: str = 'md'
    ):
        """
        A button that requires holding to activate an action.
        Features a growing circular arc and works on mobile.
        """
        super().__init__('div')
        self.classes('relative inline-block')
        self.hold_time = hold_time
        self.btn_color = color
        self.on_click_callback = on_click
        self._is_holding = False
        self._progress = 0
        self._triggered = False
        
        # We wrap AppButton
        with self:
            self.classes('p-2') # Add padding so the arc can grow outside the button
            self.btn = button(
                icon=icon,
                variant='primary', # Changed from error to primary, controlled by color
                # shape='circle', # Button component might not have shape arg yet, checking...
                # size=size,
            ).classes('s-nuke-btn w-full h-full')
            # Assuming Button accepts classes. If it wraps ui.button, we might need to adjust.
            # In Sortomatic it was AppButton. Here we use our new Button.
            # We'll enforce circular shape via class 's-nuke-btn' which has border-radius full.
            
            # SVG Progress Ring Overlay
            # Button is 32px, we want the arc outside.
            # Using viewBox 120 120, Center 60 60
            # Button is at center with R~45. Arc at R=54.
            # Circumference = 2 * pi * 54 = ~339.3
            self.circumference = 339.3
            with ui.element('svg').classes('s-dangerous-btn__arc').style('position: absolute; top:0; left:0; width:100%; height:100%; z-index: 10; pointer-events: none;') as self.svg:
                self.svg.props('viewBox="0 0 120 120"')
                
                # Progress Arc
                self.circle = ui.element('circle').style(f'fill:none; stroke:{color}; stroke-width:8; stroke-dasharray:{self.circumference}; stroke-dashoffset:{self.circumference}; transition: none; filter: brightness(1.4);')
                self.circle.props(f'cx="60" cy="60" r="54" transform="rotate(-90 60 60)"')

            
            self.tooltip = ui.tooltip(tooltip)



        # Mouse Events
        self.btn.on('mousedown', self._start_hold)
        self.btn.on('mouseup', self._stop_hold)
        self.btn.on('mouseleave', self._stop_hold)
        
        # Touch Events (Mobile)
        self.btn.on('touchstart', self._start_hold)
        self.btn.on('touchend', self._stop_hold)
        self.btn.on('touchcancel', self._stop_hold)


        # Timer for progress updates
        self._update_timer = ui.timer(0.05, self._update_progress, active=False)

    def _start_hold(self, e=None):
        if self._triggered:
            return
        self._is_holding = True
        self._progress = 0
        self._update_timer.activate()
        # Reset visual arc
        self.circle.style(f'stroke-dashoffset: {self.circumference}; transition: none')

    def _stop_hold(self, e=None):
        self._is_holding = False
        self._update_timer.deactivate()
        self._progress = 0
        # Instant reset of arc with a quick easing
        self.circle.style(f'stroke-dashoffset: {self.circumference}; transition: stroke-dashoffset 0.2s ease-out')

    def _update_progress(self):
        if not self._is_holding:
            return
            
        self._progress += 0.05 # matches timer interval
        percent = min(self._progress / self.hold_time, 1.0)
        
        # Update arc (moving clockwise)
        offset = self.circumference * (1 - percent)
        self.circle.style(f'stroke-dashoffset: {offset}; transition: stroke-dashoffset 0.05s linear; stroke: {self.btn_color}; filter: brightness(1.4);')

        
        if percent >= 1.0:
            self._is_holding = False
            self._update_timer.deactivate()
            self._triggered = True
            if self.on_click_callback:
                self.on_click_callback()
            # Reset triggered state after a delay or upon releasing
            ui.timer(1.0, self._reset_trigger, once=True)

    def _reset_trigger(self):
        self._triggered = False
        self.circle.style(f'stroke-dashoffset: {self.circumference}; transition: stroke-dashoffset 0.3s ease-out')

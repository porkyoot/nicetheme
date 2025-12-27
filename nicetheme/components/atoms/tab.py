from nicegui import ui
from typing import Optional

class tab(ui.tab):
    def __init__(self, name: str, label: Optional[str] = None, icon: Optional[str] = None):
        # We pass name as both name and label to super if label is not provided, 
        # BUT we want to suppress the default label rendering if we are doing custom content.
        # However, ui.tab doesn't easily allow suppressing label if name is provided (it uses name as label if label is None).
        # We will pass label='' to suppress the default text and render our own.
        
        super().__init__(name, label='', icon=None) # We handle icon manually too
        
        # Inject styling if not already present (idempotent check ideally, or just relying on CSS class availability)
        # For now, we assume the styles are global or injected elsewhere, but for self-containment we could add them.
        # However, adding head html repeatedly is not ideal. 
        # We will assume the user (ThemeManager or global css) handles the CSS, 
        # OR we inject it once. Given the context (simple atoms), let's keep it clean.
        # But wait, looking at theme_config, we had specific styles.
        # Let's rely on the classes being present.
        
        with self:
            with ui.row().classes('items-center flex-nowrap gap-0 transition-all duration-300'):
                if icon:
                    ui.icon(icon, size='sm')
                
                # The label that reveals
                # If label is None, use name
                text = label if label is not None else name
                ui.label(text).classes('nt-tab-label ml-0')

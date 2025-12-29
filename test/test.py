
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from nicegui import ui
from nicetheme.core.manager import ThemeManager
from nicetheme.core.bridge import ThemeBridge
from nicetheme.core.registry import ThemeRegistry
from nicetheme.core.themes import Theme, Typography, Palette, Texture, Layout
from nicetheme.components.atoms.button import button, select_button
from nicetheme.components.atoms.select import select
from nicetheme.components.atoms.icon import palette_icon
from nicetheme.components.molecules.theme_config import theme_config

# Initialize Manager (internally creates its own registry and loads default.yaml)
manager = ThemeManager()
registry = manager._registry

# Initialize ThemeBridge to sync the theme to the UI
bridge = ThemeBridge(manager, registry)

# UI Showcase
# UI Showcase
with ui.column().classes('w-full items-center p-8 gap-8 min-h-screen'):
    
    ui.label('NiceTheme Atomic Elements').classes('text-4xl font-bold mb-8')

    # Theme Selector & Config
    with ui.card().classes('w-full max-w-6xl p-6'):
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('Theme Configuration').classes('text-2xl font-semibold')
            
            # Global Theme Selector
            theme_names = list(registry.themes.keys())
            theme_mapping = {name: name.replace('_', ' ').title() for name in theme_names}

            ui.select(
                theme_mapping, 
                value=manager.theme_name,
                on_change=lambda e: manager.select_theme(e.value)
            ).classes('w-64').props('rounded outlined dense')


        theme_config(manager=manager, registry=registry)

    # Typography
    with ui.card().classes('w-full max-w-6xl p-6'):
        ui.label('Typography').classes('text-2xl font-semibold mb-4')
        
        with ui.column().classes('gap-2'):
            ui.label('Headings').classes('text-xl font-bold mb-2 text-primary')
            ui.label('H1 Heading (text-4xl)').classes('text-4xl font-bold')
            ui.label('H2 Heading (text-3xl)').classes('text-3xl font-bold')
            ui.label('H3 Heading (text-2xl)').classes('text-2xl font-bold')
            
            ui.separator().classes('my-4')
            
            ui.label('Body Text').classes('text-xl font-bold mb-2 text-primary')
            ui.label('Standard Label: Lorem ipsum dolor sit amet, consectetur adipiscing elit.').classes('mb-2')
            ui.label('Small/Muted Text').classes('text-sm opacity-70')
            
            ui.markdown('**Markdown**: *Italics*, **Bold**, `Code`, [Links](#)')

    # Inputs & Controls
    with ui.card().classes('w-full max-w-6xl p-6'):
        ui.label('Inputs & Controls').classes('text-2xl font-semibold mb-4')
        
        with ui.grid(columns=3).classes('w-full gap-4 items-start'):
            ui.input(label='Text Input', placeholder='Type something...')
            ui.number(label='Number Input', value=42)
            # Using the custom select component
            select(['Option A', 'Option B', 'Option C'], label='Select', value='Option A')
            
            ui.input(label='Password', password=True)
            ui.textarea(label='Textarea', placeholder='Multi-line text').props('rows=1')
            select({'1': 'One', '2': 'Two'}, label='Mapped Select', value='1')

        ui.separator().classes('my-4')
        
        with ui.row().classes('w-full gap-12 items-start'):
            with ui.column().classes('gap-4'):
                ui.label('Toggles').classes('font-bold text-lg')
                ui.checkbox('Checkbox', value=True)
                ui.switch('Switch', value=True)
                ui.toggle(['On', 'Off'], value='On')
            
            with ui.column().classes('gap-4'):
                ui.label('Radios').classes('font-bold text-lg')
                ui.radio(['Option 1', 'Option 2', 'Option 3'], value='Option 1').props('inline')

        ui.separator().classes('my-4')

        with ui.column().classes('w-full gap-6'):
             ui.label('Sliders').classes('font-bold text-lg')
             ui.slider(min=0, max=100, value=50).props('label-always')
             ui.range(min=0, max=100, value={'min': 20, 'max': 80}).props('label-always')

        ui.separator().classes('my-4')

        with ui.row().classes('w-full gap-8 items-start'):
            ui.date(value='2023-01-01').props('flat bordered')
            ui.time(value='12:00').props('flat bordered')
            with ui.column().classes('gap-2'):
                ui.label('Color Picker')
                ui.color_picker(on_pick=lambda e: color_label.style(f'color: {e.color}'))
                color_label = ui.label('Pick a color!').classes('font-bold text-xl')

    # Buttons
    with ui.card().classes('w-full max-w-6xl p-6'):
        ui.label('Buttons').classes('text-2xl font-semibold mb-4')
        with ui.row().classes('w-full gap-4 items-center flex-wrap'):
            button('Primary', on_click=lambda: ui.notify('Primary'))
            button('Secondary', variant='secondary', on_click=lambda: ui.notify('Secondary'))
            button('Ghost', variant='ghost', on_click=lambda: ui.notify('Ghost'))
            button(icon='home', on_click=lambda: ui.notify('Icon'))
            button('Rotatable', icon='refresh', rotate_icon=True)
            ui.separator().classes('vertical')
            select_button('Select Btn', on_click=lambda: ui.notify('Select Btn'))

    # Layout & Containers
    with ui.card().classes('w-full max-w-6xl p-6'):
        ui.label('Layout & Containers').classes('text-2xl font-semibold mb-4')
        
        ui.label('Tabs').classes('font-bold mb-2')
        with ui.tabs().classes('w-full') as tabs:
            one = ui.tab('Tab One')
            two = ui.tab('Tab Two')
            three = ui.tab('Tab Three')
        with ui.tab_panels(tabs, value=one).classes('w-full p-4 border rounded'):
            with ui.tab_panel(one):
                ui.label('Content One')
            with ui.tab_panel(two):
                ui.label('Content Two')
            with ui.tab_panel(three):
                ui.label('Content Three')

        ui.separator().classes('my-4')

        ui.label('Expansion').classes('font-bold mb-2')
        with ui.expansion('Expansion Item', icon='expand_more').classes('w-full border rounded'):
            ui.label('Expanded content goes here...').classes('p-4')
            
        ui.separator().classes('my-4')
        
        ui.label('Splitter').classes('font-bold mb-2')
        with ui.splitter(value=30).classes('w-full h-32 border rounded') as splitter:
            with splitter.before:
                ui.label('Left').classes('p-4')
            with splitter.after:
                ui.label('Right').classes('p-4')

        ui.separator().classes('my-4')
        
        ui.label('Stepper').classes('font-bold mb-2')
        with ui.stepper().props('vertical').classes('w-full') as stepper:
            with ui.step('Step 1'):
                ui.label('Content 1')
                with ui.stepper_navigation():
                    ui.button('Next', on_click=stepper.next)
            with ui.step('Step 2'):
                ui.label('Content 2')
                with ui.stepper_navigation():
                    ui.button('Back', on_click=stepper.previous)
                    ui.button('Next', on_click=stepper.next)
            with ui.step('Step 3'):
                ui.label('Content 3')
                with ui.stepper_navigation():
                    ui.button('Back', on_click=stepper.previous)

    # Data Display
    with ui.card().classes('w-full max-w-6xl p-6'):
        ui.label('Data Display').classes('text-2xl font-semibold mb-4')
        
        with ui.row().classes('gap-4 items-center mb-6'):
            ui.avatar('face')
            ui.chip('Chip', icon='face', removable=True)
            ui.chip('Selected', icon='check').classes('bg-primary text-white')
            with ui.button(icon='notifications').classes('bg-white text-black'):
                ui.badge('5').props('floating').classes('bg-negative text-white')
        
        columns = [
            {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
            {'name': 'age', 'label': 'Age', 'field': 'age', 'align': 'left'},
            {'name': 'role', 'label': 'Role', 'field': 'role', 'align': 'left'},
        ]
        rows = [
            {'name': 'Alice', 'age': 30, 'role': 'Engineer'},
            {'name': 'Bob', 'age': 25, 'role': 'Designer'},
            {'name': 'Charlie', 'age': 35, 'role': 'Manager'},
        ]
        ui.table(columns=columns, rows=rows, row_key='name').classes('w-full')
        
        ui.separator().classes('my-6')
        
        with ui.row().classes('gap-12 items-center w-full'):
            with ui.column().classes('items-center'):
                ui.label('Circular').classes('mb-2')
                ui.circular_progress(value=0.7, show_value=True, size='60px')
            with ui.column().classes('flex-grow'):
                ui.label('Linear').classes('mb-2')
                ui.linear_progress(value=0.7, show_value=True)
            with ui.column().classes('items-center'):
                ui.label('Spinner').classes('mb-2')
                ui.spinner(size='lg')
        
        ui.separator().classes('my-6')
        
        ui.label('Tree').classes('font-bold mb-2')
        ui.tree([
            {'id': 'numbers', 'children': [{'id': '1'}, {'id': '2'}]},
            {'id': 'letters', 'children': [{'id': 'A'}, {'id': 'B'}]},
        ], label_key='id').expand()

    # Feedback & Interactive
    with ui.card().classes('w-full max-w-6xl p-6'):
        ui.label('Feedback & Interactive').classes('text-2xl font-semibold mb-4')
        with ui.row().classes('gap-4 items-center'):
            ui.button('Show Notification', on_click=lambda: ui.notify('Notification!', type='info'))
            
            with ui.dialog() as dialog, ui.card():
                ui.label('Dialog Content')
                ui.label('This is a simple dialog.')
                with ui.row().classes('w-full justify-end'):
                    ui.button('Close', on_click=dialog.close)
            
            ui.button('Open Dialog', on_click=dialog.open)
            
            with ui.button('Hover me'):
                ui.tooltip('This is a tooltip')

ui.run(port=8080, title='NiceTheme Showcase', show=False, reload=True)
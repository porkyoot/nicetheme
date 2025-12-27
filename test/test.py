from nicegui import ui

# Comparison with standard toggle
ui.label('Standard ui.toggle for comparison')
ui.toggle(options=['A', 'B', 'C'], value='A')

ui.run(port=8080, title='NiceTheme Test', show=False, reload=True)
# NiceTheme

A powerful theming engine for [NiceGUI](https://nicegui.io) that extends its capabilities with advanced theming pillars like Texture, Layout, and Typography, alongside standard color Palettes.

## Features

- **NiceGUI-Inspired API**: Clean, intuitive syntax inspired by NiceGUI
- **ThemeManager**: Translates Python `Theme` objects into NiceGUI/Quasar configuration and CSS variables
- **ThemeRegistry**: Dynamically loads theme components (Palettes, Textures, Layouts, Fonts) from YAML configuration files
- **Component-based Theming**: Mix and match different palettes, textures, and layouts to create unique themes
- **Font Management**: Automatically registers and serves local fonts

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Quick Start

```python
from nicegui import ui
from nicetheme import nt

with ui.page('/'):
    nt.button('Click me', variant='primary')
    nt.select(['Option A', 'Option B', 'Option C'])
    nt.slider(min=0, max=100, value=50)
    nt.toggle(['On', 'Off'])

ui.run()
```

## API Overview

NiceTheme provides a clean API through the `nt` module:

```python
from nicetheme import nt

# All components are accessible via nt.*
nt.button(...)
nt.select(...)
nt.icon(...)
nt.slider(...)
nt.tab(...)
nt.toggle(...)
nt.theme_config(...)
```

## Advanced Usage

### Theme Management

```python
from nicetheme import ThemeManager, ThemeRegistry

# Initialize theme system
manager = ThemeManager()
registry = ThemeRegistry()

# Select a theme
manager.select_theme('solarized')

# Set mode
manager.set_mode('dark')  # or 'light', 'auto'
```

### Direct Component Imports

```python
# Import specific components
from nicetheme.components.atoms import button, select
from nicetheme.core import ThemeManager, Theme, Palette
```

## Structure

- `nicetheme/nt.py`: Main API module (like NiceGUI's `ui`)
- `nicetheme/core/`: Core theme management classes
  - `manager.py`: `ThemeManager` class
  - `bridge.py`: `ThemeBridge` for CSS injection
  - `registry.py`: `ThemeRegistry` for loading themes
  - `themes.py`: Data classes for `Theme`, `Palette`, `Texture`, etc.
- `nicetheme/components/`: UI components
  - `atoms/`: Basic components (button, select, icon, etc.)
  - `molecules/`: Complex components (theme_config, etc.)
- `nicetheme/themes/`: Theme definitions (YAML) and assets
- `nicetheme/assets/`: CSS files

## Theme Configuration

Themes are defined in YAML files within the `themes` directory:

### Palette Example
**`themes/palettes/solarized.yaml`**
```yaml
primary: "#b58900"
secondary: "#cb4b16"
# ...
```

### Layout Example
**`themes/layouts/relaxed.yaml`**
```yaml
roundness: 8.0
density: 1.2
border: 1.0
```

### Texture Example
**`themes/textures/glossy.yaml`**
```yaml
shadow_intensity: 0.3
highlight_intensity: 0.5
opacity: 0.9
blur: 8
```

## Examples

See [test_api.py](test_api.py) for a complete example demonstrating the new API.

## License

MIT

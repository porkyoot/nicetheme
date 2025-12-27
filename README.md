# NiceTheme

A powerful theming engine for [NiceGUI](https://nicegui.io) that extends its capabilities with advanced theming pillars like Texture, Layout, and Typography, alongside standard color Palettes.

## Features

- **ThemeManager**: Translates Python `Theme` objects into NiceGUI/Quasar configuration and CSS variables.
- **ThemeRegistry**: Dynamically loads theme components (Palettes, Textures, Layouts, Fonts) from YAML configuration files.
- **Component-based Theming**: Mix and match different palettes, textures, and layouts to create unique themes.
- **Font Management**: Automatically registers and serves local fonts.

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Structure

- `nicetheme/core/themes.py`: Dataclass definitions for Palette, Texture, Layout, etc.
- `nicetheme/core/manager.py`: `ThemeManager` class that applies themes to the UI.
- `nicetheme/core/registry.py`: `ThemeRegistry` class that scans/loads themes from files.
- `nicetheme/themes/`: Default directory for theme definitions (YAML) and assets.

## Usage

### Using the Manager

```python
from nicegui import ui
from nicetheme.core.manager import ThemeManager
from nicetheme.core.themes import Theme, Palette, Texture, Layout, Typography

# Define or load your theme components
theme = Theme(...) 

# Apply the theme
manager = ThemeManager()
manager.apply(theme)

ui.run()
```

### Loading from Registry

```python
from nicetheme.core.registry import ThemeRegistry

registry = ThemeRegistry() # Scans nicetheme/themes by default

# Access loaded components
solarized_palette = registry.palettes.get('solarized')
```

## Configuration

Themes are defined in YAML files within the `themes` directory:

**`themes/palettes/solarized.yaml`**
```yaml
primary: "#b58900"
secondary: "#cb4b16"
# ...
```

**`themes/layouts/relaxed.yaml`**
```yaml
roundness: 8.0
density: 1.2
```

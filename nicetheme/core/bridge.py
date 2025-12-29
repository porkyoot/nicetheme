from nicegui import ui
from typing import List
import os
from .manager import ThemeManager
from .registry import ThemeRegistry
from .themes import Palette, Texture, Layout, Typography

class ThemeBridge:
    """
    THE BRIDGE: Handles synchronization between ThemeManager state 
    and the NiceGUI frontend (CSS variables, Quasar config).
    """
    def __init__(self, manager: ThemeManager, registry: ThemeRegistry):
        self.manager = manager
        self.registry = registry
        
        # Subscribe to changes automatically
        self.manager.bind(self.sync)
        
        # FOUC Prevention: Hide body until theme is ready
        self._inject_fouc_prevention()
        
        # Inject static resources
        self._inject_static_styles()
        self._inject_google_fonts()
        self._inject_local_fonts()
        
        # Inject browser color scheme detection
        self._inject_color_scheme_detection()
        
        # Inject persistence logic (localStorage)
        self._inject_persistence_logic()

        # Initial Variable Injection (SSR friendly)
        if self.manager.theme:
            palette = self.manager.get_active_palette()
            if palette:
                css_vars = self._generate_css_vars_dict(self.manager, palette)
                
                # Unwrap dict to css string
                css_lines = [f"{k}: {v};" for k, v in css_vars.items()]
                vars_block = "\n  ".join(css_lines)
                
                # Check mode
                mode = self.manager.get_effective_mode()
                if mode == 'dark':
                    ui.add_head_html(f"<style>body.body--dark {{ {vars_block} }}</style>")
                else:
                    ui.add_head_html(f"<style>:root {{ {vars_block} }}</style>")
                
                # Inject texture CSS
                self._inject_texture_css(self.manager.theme.texture)
        
        # Mark theme as ready - reveal body smoothly
        self._mark_theme_ready()

    def sync(self, manager: ThemeManager):
        """Called whenever the manager notifies of a change."""
        theme = manager.theme
        if not theme:
            return

        palette = manager.get_active_palette()
        if not palette:
            return

        # 1. Update Quasar/NiceGUI global colors
        ui.colors(
            primary=palette.resolve_color(palette.primary),
            secondary=palette.resolve_color(palette.secondary),
            positive=palette.resolve_color(palette.positive),
            negative=palette.resolve_color(palette.negative),
            warning=palette.resolve_color(palette.warning),
            info=palette.resolve_color(palette.info),
            accent=palette.resolve_color(palette.content[0]) if palette.content else palette.resolve_color(palette.primary),
            dark=palette.resolve_color('base03'),
        )

        # 2. Generate CSS Variables Dictionary
        css_vars = self._generate_css_vars_dict(manager, palette)
        
        # 3. Update CSS Variables & Body Class via JS (Dynamic & Fast)
        import json
        mode = manager.get_effective_mode()
        is_dark = mode == 'dark'
        
        js_cmd = f"""
        const vars = {json.dumps(css_vars)};
        Object.entries(vars).forEach(([k,v]) => document.documentElement.style.setProperty(k, v));
        
        // Toggle Body Classes
        if ({str(is_dark).lower()}) {{
            document.body.classList.add('body--dark');
            document.body.classList.remove('body--light');
            document.querySelector('#app').classList.add('q-dark'); // Standard Quasar
        }} else {{
            document.body.classList.remove('body--dark');
            document.body.classList.add('body--light');
            document.querySelector('#app').classList.remove('q-dark');
        }}

        // Persistence: Save current state to localStorage
        const prefs = {{
            mode: {json.dumps(manager.mode)},
            palette: {json.dumps(manager.active_palette_name)},
            texture: {json.dumps(theme.texture_name)},
            layout: {json.dumps(theme.layout_name)},
            typography: {{
                primary: {json.dumps(theme.typography.primary)},
                secondary: {json.dumps(theme.typography.secondary)},
                mono: {json.dumps(theme.typography.mono)},
                scale: {theme.typography.scale},
                title_case: {json.dumps(theme.typography.title_case)}
            }}
        }};
        
        // Add palette overrides
        const p_primary = {json.dumps(palette.primary)};
        const p_secondary = {json.dumps(palette.secondary)};
        prefs.palette_overrides = {{ primary: p_primary, secondary: p_secondary }};

        localStorage.setItem('nt_prefs_' + {json.dumps(manager.theme_name)}, JSON.stringify(prefs));
        """
        try:
            ui.run_javascript(js_cmd)
        except (AssertionError, RuntimeError):
            # No active client/loop (e.g. during startup), skip JS update
            pass
        
        # Update texture CSS dynamically
        if manager.theme and manager.theme.texture:
            self._update_texture_css_dynamic(manager.theme.texture)

    def _generate_css_vars_dict(self, manager: ThemeManager, palette: Palette) -> dict:
        """Generates a flat dictionary of CSS variables."""
        css_vars = {}
        
        # Helper for resolving colors
        def rc(val): return palette.resolve_color(val)
        
        # Helper to hex to rgb
        def hex_to_rgb(hex_code):
            hex_code = hex_code.lstrip('#')
            if len(hex_code) == 3: hex_code = ''.join([c*2 for c in hex_code])
            return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
            
        def to_rgb_str(val):
            try:
                c = rc(val)
                if c.startswith('#'):
                    h = hex_to_rgb(c)
                    return f"{h[0]}, {h[1]}, {h[2]}"
                return "0, 0, 0" # Fallback
            except:
                return "0, 0, 0"

        # 1. Palette Colors
        css_vars["--nt-primary"] = rc(palette.primary)
        css_vars["--nt-secondary"] = rc(palette.secondary)
        css_vars["--nt-positive"] = rc(palette.positive)
        css_vars["--nt-negative"] = rc(palette.negative)
        css_vars["--nt-warning"] = rc(palette.warning)
        css_vars["--nt-info"] = rc(palette.info)
        css_vars["--nt-inactive"] = rc(palette.inative)

        # Custom & Named Colors
        for name, color in palette.colors.items():
            css_vars[f"--nt-color-{name}"] = rc(color)
        
        # Ensure base colors exist
        if 'white' not in palette.colors:
            css_vars["--nt-color-white"] = "#ffffff"
        if 'black' not in palette.colors:
            css_vars["--nt-color-black"] = "#000000"

        # Greys
        for name, color in palette.greys.items():
            css_vars[f"--nt-color-{name}"] = rc(color)

        # 2. Surface (with Padding)
        if palette.surface:
            css_vars["--nt-surface-rgb"] = to_rgb_str(palette.surface[0])
            css_vars["--nt-surface-page"] = rc(palette.surface[0])
            
            # Pad up to 6 levels (0-5)
            last_surface = palette.surface[-1]
            for i in range(6):
                if i < len(palette.surface):
                    val = palette.surface[i]
                else:
                    val = last_surface
                css_vars[f"--nt-surface-{i}"] = rc(val)
        
        # 3. Content
        if palette.content:
            css_vars["--nt-content-rgb"] = to_rgb_str(palette.content[0])
            css_vars["--nt-content-accent"] = rc(palette.content[0])
            
            for i, cont in enumerate(palette.content):
                css_vars[f"--nt-content-{i}"] = rc(cont)

        # 4. Texture Colors
        css_vars["--nt-shadow-color"] = rc(palette.shadow)
        css_vars["--nt-shadow-rgb"] = to_rgb_str(palette.shadow)
        css_vars["--nt-highlight-color"] = rc(palette.highlight)
        css_vars["--nt-highlight-rgb"] = to_rgb_str(palette.highlight)
        css_vars["--nt-border-color"] = rc(palette.border)
        css_vars["--nt-border-rgb"] = to_rgb_str(palette.border)

        # 5. Theme Settings (Layout, Texture, Typography)
        if manager.theme:
            if manager.theme.layout:
                layout = manager.theme.layout
                css_vars["--nt-roundness"] = str(layout.roundness)
                css_vars["--nt-border-width"] = str(layout.border)
                css_vars["--nt-density"] = str(layout.density)
            
            if manager.theme.texture:
                texture = manager.theme.texture
                css_vars["--nt-shadow-intensity"] = str(texture.shadow_intensity)
                css_vars["--nt-highlight-intensity"] = str(texture.highlight_intensity)
                css_vars["--nt-opacity"] = str(texture.opacity)
                css_vars["--nt-blur"] = str(texture.blur)

            if manager.theme.typography:
                typo = manager.theme.typography
                css_vars["--nt-font-primary"] = f"'{typo.primary}'"
                css_vars["--nt-font-secondary"] = f"'{typo.secondary}'"
                css_vars["--nt-font-mono"] = f"'{typo.mono}'"
                css_vars["--nt-font-scale"] = str(typo.scale)
                
                transform_map = {
                     "lowercase": "lowercase",
                     "uppercase": "uppercase",
                     "titlecase": "capitalize",
                     "title_case": "capitalize",
                     "none": "none"
                }
                css_vars["--nt-text-transform-title"] = transform_map.get(typo.title_case, "none")
        
        return css_vars

    def _inject_static_styles(self):
        """Injects static CSS files."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(current_dir), 'assets')
        
        for css_file in ['icons.css', 'sliders.css', 'components.css', 'global_overrides.css']:
            path = os.path.join(assets_dir, css_file)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    ui.add_head_html(f"<style>{f.read()}</style>")

    def _inject_google_fonts(self):
        # A curated list of Google Fonts
        google_fonts = [
            "Roboto", "Open Sans", "Noto Sans JP", "Inter", "Lato", "Montserrat", 
            "Oswald", "Source Sans Pro", "Slabo 27px", "Raleway", "PT Sans", 
            "Merriweather", "Nunito Sans", "Prompt", "Work Sans", "Rubik",
            "Playfair Display", "Fira Sans", "Mukta", "Quicksand", "Karla",
            "Titillium Web", "Inconsolata", "Barlow", "Dosis", "Cabin",
            "Bitter", "Anton", "Oxygen", "Arvo", "Libre Baskerville", "Lobster",
            "Pacifico", "Shadows Into Light", "Dancing Script", "Bebas Neue",
            "Poppins", "Recursive", "Sniglet"
        ]
        google_fonts.sort()
        families = "&family=".join([f.replace(' ', '+') for f in google_fonts])
        ui.add_head_html(f'<link href="https://fonts.googleapis.com/css2?family={families}&display=swap" rel="stylesheet">')

    def _inject_local_fonts(self):
        """Generates @font-face rules for local fonts registered in the Registry."""
        if not self.registry or not self.registry.fonts:
            return

        css_rules = []
        for name, url in self.registry.fonts.items():
            rule = f"""
            @font-face {{
                font-family: '{name}';
                src: url('{url}');
            }}
            """
            css_rules.append(rule)
        
        if css_rules:
            ui.add_head_html(f"<style>{''.join(css_rules)}</style>")
    
    def _inject_color_scheme_detection(self):
        """Injects JavaScript to detect browser color scheme preference using prefers-color-scheme media query."""
        detection_script = """
        <script>
        (function() {
            // Detect color scheme preference using media query
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            function detectAndStoreColorScheme() {
                const isDark = mediaQuery.matches;
                const mode = isDark ? 'dark' : 'light';
                
                // Store in localStorage for persistence
                localStorage.setItem('nt_detected_color_scheme', mode);
                
                // Also store as a custom property on the document for easy access
                document.documentElement.setAttribute('data-detected-color-scheme', mode);
            }
            
            // Detect initial preference immediately
            detectAndStoreColorScheme();
            
            // Listen for changes (e.g., user changes system preference)
            if (mediaQuery.addEventListener) {
                mediaQuery.addEventListener('change', function() {
                    detectAndStoreColorScheme();
                    // Trigger a page refresh to apply the new theme
                    window.location.reload();
                });
            } else {
                // Fallback for older browsers
                mediaQuery.addListener(function() {
                    detectAndStoreColorScheme();
                    window.location.reload();
                });
            }
        })();
        </script>
        """
        ui.add_head_html(detection_script)
        
        # After detection script is loaded, read the detected value and set it
        # This will run on the server side during initialization
        read_detection_script = """
        const detectedMode = localStorage.getItem('nt_detected_color_scheme') || 
                           (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        return detectedMode;
        """
        
        # Try to read the detected mode and set it in the manager
        # This needs to be done after the client connects
        def set_initial_detected_mode():
            try:
                detected = ui.run_javascript(read_detection_script, timeout=1.0)
                if detected and detected in ['light', 'dark']:
                    self.manager.set_detected_mode(detected)
            except:
                # If we can't read it (e.g., during SSR), default to light
                self.manager.set_detected_mode('light')
        
        # Schedule this to run when a client connects
        ui.timer(0.1, set_initial_detected_mode, once=True)

    def _inject_persistence_logic(self):
        """Injects logic to read from localStorage on startup and apply to manager."""
        import json
        
        read_prefs_script = f"""
        return localStorage.getItem('nt_prefs_' + {json.dumps(self.manager.theme_name)});
        """
        
        async def load_persisted_prefs():
            try:
                prefs_json = await ui.run_javascript(read_prefs_script, timeout=1.0)
                if prefs_json:
                    prefs = json.loads(prefs_json)
                    # Use a specialized method in manager to apply all at once
                    self.manager.apply_preferences(prefs)
            except Exception:
                pass
        
        # Schedule to run once on client connection
        ui.timer(0.2, load_persisted_prefs, once=True)

    def _inject_texture_css(self, texture: Texture):
        """Generates and injects component-specific texture CSS on initial load."""
        css = self._generate_texture_css(texture)
        if css:
            ui.add_head_html(f'<style id="nt-texture-css">{css}</style>')
    
    def _update_texture_css_dynamic(self, texture: Texture):
        """Dynamically updates texture CSS via JavaScript."""
        css = self._generate_texture_css(texture)
        if css:
            # Escape for JavaScript string
            import json
            css_escaped = json.dumps(css)
            js_cmd = f"""
            let styleEl = document.getElementById('nt-texture-css');
            if (!styleEl) {{
                styleEl = document.createElement('style');
                styleEl.id = 'nt-texture-css';
                document.head.appendChild(styleEl);
            }}
            styleEl.textContent = {css_escaped};
            """
            try:
                ui.run_javascript(js_cmd)
            except (AssertionError, RuntimeError):
                pass
    
    def _generate_texture_css(self, texture: Texture) -> str:
        """Generates CSS rules from component-specific texture properties."""
        rules: List[str] = []
        
        # Component type to CSS selectors mapping
        selectors = {
            'button': '.q-btn:not(.q-btn--flat):not(.q-btn--outline)',
            'card': '.q-card, .nicegui-card',
            'progress': '.q-linear-progress, .q-circular-progress',
            'slider': '.q-slider, .palette-slider',
            'toggle': '.q-toggle, .q-checkbox, .q-radio, .q-btn-group',
            'chip': '.q-chip, .q-badge',
            'menu': '.q-menu, .q-tooltip, .q-notification'
        }
        
        # Generate rules for each component type
        for component, selector in selectors.items():
            css_props = getattr(texture, component, "")
            if css_props and css_props.strip():
                # Handle multiline YAML properties
                props_cleaned = css_props.strip().replace('\n', ' ')
                rules.append(f"{selector} {{ {props_cleaned} }}")
        
        return '\n'.join(rules)

    def _inject_fouc_prevention(self):
        """Injects CSS to prevent Flash of Unstyled Content (FOUC)."""
        fouc_css = """
        body {
            opacity: 0;
            transition: opacity 0.2s ease-in-out;
        }
        body.theme-ready {
            opacity: 1;
        }
        """
        ui.add_head_html(f"<style>{fouc_css}</style>")
    
    def _mark_theme_ready(self):
        """Marks the theme as ready by adding the theme-ready class to body."""
        ready_script = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.body.classList.add('theme-ready');
        });
        // Fallback in case DOMContentLoaded already fired
        if (document.readyState === 'loading') {
            // Still loading, listener will fire
        } else {
            // Already loaded
            document.body.classList.add('theme-ready');
        }
        </script>
        """
        ui.add_head_html(ready_script)


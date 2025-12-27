from nicegui import ui
from typing import Optional, Dict
from ...core.themes import Theme, Palette, Texture, Layout
import math

__all__ = ['palette_icon', 'texture_icon', 'theme_icon']

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class palette_icon(ui.element):
    """
    A custom SVG icon that displays a visual representation of a theme palette.
    Features two half-disks in the center (background and foreground) surrounded by 
    arcs of the 8 named colors.
    """
    def __init__(
        self, 
        palette: Palette,
        *, 
        size: str = "24px",
        circular: bool = True
    ):
        super().__init__('svg')
        
        # Extract colors from the palette (which now includes semantics)
        # Defaulting to light mode for icon representation
        background_color = palette.resolve_color(palette.surface[0])
        foreground_color = palette.resolve_color(palette.content[0])
        colors = palette.colors
        
        # Set SVG attributes
        self._props['viewBox'] = '0 0 24 24'
        self._props['xmlns'] = 'http://www.w3.org/2000/svg'
        self.classes('nt-theme-icon')
        self.style(f'width: {size}; height: {size};')
        
        if circular:
            self.classes('nt-theme-icon--circular')
        
        # Generate the SVG content
        self._generate_icon(background_color, foreground_color, colors)
    
    @staticmethod
    def _generate_content(bg_color: str, fg_color: str, colors: Dict[str, str]) -> str:
        """Generate the SVG content (paths) for the theme icon."""
        
        # Center point
        cx, cy = 12, 12
        
        # Radii
        outer_radius = 22  # Extend beyond viewport to fill corners (clipped by container)
        inner_radius = 6  # Smaller inner radius makes arcs thicker
        center_radius = inner_radius  # Make center fill to the arcs with no gap
        
        # Calculate arc segments (8 segments, 360/8 = 45 degrees each)
        segment_angle = 45
        
        svg_content = []
        
        i = 0
        # Draw the 8 colored arcs
        for color_name in colors:
            try:
                color = colors.get(color_name, '#888888')
            except AttributeError:
                # Debugging: colors might not be a dict
                # We don't have the palette name here easily, but we can see the type
                print(f"CRITICAL ERROR in palette_icon: colors is {type(colors)} not dict. Value: {repr(colors)}")
                color = '#888888'
            
            # Calculate start and end angles (in degrees, starting from top)
            start_angle = i * segment_angle - 90  # -90 to start from top
            end_angle = start_angle + segment_angle
            
            # Convert to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            # Calculate arc path points
            x1_outer = cx + outer_radius * math.cos(start_rad)
            y1_outer = cy + outer_radius * math.sin(start_rad)
            x2_outer = cx + outer_radius * math.cos(end_rad)
            y2_outer = cy + outer_radius * math.sin(end_rad)
            
            x1_inner = cx + inner_radius * math.cos(start_rad)
            y1_inner = cy + inner_radius * math.sin(start_rad)
            x2_inner = cx + inner_radius * math.cos(end_rad)
            y2_inner = cy + inner_radius * math.sin(end_rad)
            
            # Create arc path
            path_d = f"""
                M {x1_outer:.2f},{y1_outer:.2f}
                A {outer_radius},{outer_radius} 0 0 1 {x2_outer:.2f},{y2_outer:.2f}
                L {x2_inner:.2f},{y2_inner:.2f}
                A {inner_radius},{inner_radius} 0 0 0 {x1_inner:.2f},{y1_inner:.2f}
                Z
            """.strip()
            
            svg_content.append(f'<path d="{path_d}" fill="{color}" />')
            i += 1
        
        # Draw center background half-disk (left side)
        svg_content.append(f'''
            <path d="M {cx},{cy - center_radius} 
                     A {center_radius},{center_radius} 0 0 0 {cx},{cy + center_radius} 
                     L {cx},{cy} Z" 
                   fill="{bg_color}" />
        '''.strip())
        
        # Draw center foreground half-disk (right side)
        svg_content.append(f'''
            <path d="M {cx},{cy - center_radius} 
                     A {center_radius},{center_radius} 0 0 1 {cx},{cy + center_radius} 
                     L {cx},{cy} Z" 
                   fill="{fg_color}" />
        '''.strip())
        
        # Add a subtle center line
        svg_content.append(f'''
            <line x1="{cx}" y1="{cy - center_radius}" 
                  x2="{cx}" y2="{cy + center_radius}" 
                  stroke="rgba(255,255,255,0.2)" 
                  stroke-width="0.5" />
        '''.strip())
 
        return '\n'.join(svg_content)
 
    @staticmethod
    def to_html(palette: Palette, *, size: str = "24px", circular: bool = True) -> str:
        """Returns the full HTML (SVG) string for this component."""
        background_color = palette.resolve_color(palette.surface[0])
        foreground_color = palette.resolve_color(palette.content[0])
        colors = palette.colors
        
        content = palette_icon._generate_content(background_color, foreground_color, colors)
        
        style = f'width: {size}; height: {size};'
        circular_class = 'nt-theme-icon--circular' if circular else ''
            
        return f'<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="nt-theme-icon {circular_class}" style="{style}">{content}</svg>'
 
    def _generate_icon(self, bg_color: str, fg_color: str, colors: Dict[str, str]):
        """Generate the SVG elements for the theme icon."""
        self._props['innerHTML'] = self._generate_content(bg_color, fg_color, colors)


class texture_icon(ui.element):
    """
    A custom HTML/CSS icon that displays a visual representation of a texture.
    Features a circle styled like a card showing the texture's visual properties
    (opacity, shadows, glossy/flat effects).
    (Category: Texture)
    """
    def __init__(
        self, 
        texture: Texture,
        palette: Palette,
        layout: Layout,
        *, 
        size: str = "24px"
    ):
        super().__init__('div')
        
        # Apply base styling
        self.classes('nt-texture-icon')
        
        # Calculate shadow directly from texture intensity
        wrapper_style = f'width: {size}; height: {size};'
        
        # shadow_intensity is now just a float on Texture, check if > 0
        if texture.shadow_intensity > 0:
            # Get shadow color from texture -> from palette
            shadow_ref = palette.shadow
            shadow_hex = palette.resolve_color(shadow_ref)
            r, g, b = hex_to_rgb(shadow_hex)
            
            # Calculate actual shadow based on intensity
            si = texture.shadow_intensity
            
            # Calculate size factor for the shadow (base 24px)
            import re
            size_match = re.match(r'([0-9.]+)(.+)', size)
            size_val = 24.0
            if size_match:
                try: size_val = float(size_match.group(1))
                except: pass
            sf = size_val / 24.0

            # Use tight values scaled by icon size
            if si > 1.5:
                shadow_def = f'0 {10*sf:.1f}px {12*sf:.1f}px rgba({r}, {g}, {b}, {0.4 * si:.2f})'
            elif si > 1.0:
                shadow_def = f'0 {6*sf:.1f}px {8*sf:.1f}px rgba({r}, {g}, {b}, {0.35 * si:.2f})'
            elif si > 0.5:
                shadow_def = f'0 {3*sf:.1f}px {4*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            else:
                shadow_def = f'0 {1*sf:.1f}px {2*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            
            wrapper_style += f' filter: drop-shadow({shadow_def});'
        
        self.style(wrapper_style)
        
        # Create the circle element
        with self:
            circle = ui.element('div').classes('nt-texture-icon__circle')
            
            # Apply texture class (css property in Texture)
            if texture.css:
                 circle.classes(texture.css)
            
            # Apply opacity
            if texture.opacity < 1.0:
                # Create glassmorphism effect
                circle.classes('nt-glass')
                circle.style(f'background: rgba(128, 128, 128, {texture.opacity});')
            else:
                # Solid background
                circle.style('background: var(--nt-surface-page);')
            
            # Apply border and transitions
            # Apply shape-based border and roundness
            border_width_px = f"{max(1.0, float(texture.border_width) * 0.5)}px"
            
            # Roundness coming from Layout
            if layout.roundness == 0:
                border_radius = '0'
            elif layout.roundness >= 2.0:
                border_radius = '50%'
            else:
                radius_percent = (layout.roundness / 2.0) * 50
                border_radius = f'{radius_percent}%'

            circle.style(f'''
                border-width: {border_width_px};
                border-radius: {border_radius};
            ''')
            
            with circle:
                 # Apply highlight density if applicable
                if texture.highlight_intensity > 0:
                    # Pass intensity as var if needed, or inline style for specific gradient
                    ui.element('div').classes('nt-texture-icon__highlight').style(f'--nt-highlight-intensity: {0.1 * texture.highlight_intensity};')
            
            # Add hover effect
            circle.classes('nt-texture-icon__circle--interactive')

    @staticmethod
    def to_html(texture: Texture, palette: Palette, layout: Layout, *, size: str = "24px") -> str:
        """Returns the full HTML string for this component."""
        
        # Wrapper styles with shadow
        wrapper_style = f'width: {size}; height: {size};'
        
        # Calculate shadow directly from texture intensity  
        if texture.shadow_intensity > 0:
            shadow_ref = palette.shadow
            shadow_hex = palette.resolve_color(shadow_ref)
            r, g, b = hex_to_rgb(shadow_hex)
            si = texture.shadow_intensity

            # Calculate size factor for the shadow (base 24px)
            import re
            size_match = re.match(r'([0-9.]+)(.+)', size)
            size_val = 24.0
            if size_match:
                try: size_val = float(size_match.group(1))
                except: pass
            sf = size_val / 24.0

            # Use tight values scaled by icon size
            if si > 1.5:
                shadow_def = f'0 {10*sf:.1f}px {12*sf:.1f}px rgba({r}, {g}, {b}, {0.4 * si:.2f})'
            elif si > 1.0:
                shadow_def = f'0 {6*sf:.1f}px {8*sf:.1f}px rgba({r}, {g}, {b}, {0.35 * si:.2f})'
            elif si > 0.5:
                shadow_def = f'0 {3*sf:.1f}px {4*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            else:
                shadow_def = f'0 {1*sf:.1f}px {2*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            wrapper_style += f' filter: drop-shadow({shadow_def});'
        
        # Circle styles
        circle_style = ''
        circle_classes = 'nt-texture-icon__circle'
        
        # Opacity/Backdrop
        if texture.opacity < 1.0:
            circle_classes += ' nt-glass'
            circle_style += f'background: rgba(128, 128, 128, {texture.opacity});'
        else:
             circle_style += 'background: var(--nt-surface-page);'
             
        # Shape styling
        border_width_px = f"{max(1.0, float(texture.border_width) * 0.5)}px"
        
        if layout.roundness == 0:
            border_radius = '0'
        elif layout.roundness >= 2.0:
            border_radius = '50%'
        else:
            radius_percent = (layout.roundness / 2.0) * 50
            border_radius = f'{radius_percent}%'

        circle_style += f' border-width: {border_width_px}; border-radius: {border_radius};'
        
        # Clean up
        circle_style = circle_style.replace('\n', ' ').strip()
        
        # Gloss effect
        gloss_html = ""
        if texture.highlight_intensity > 0:
            # Using inline style for intensity var
             gloss_html = f'<div class="nt-texture-icon__highlight" style="--nt-highlight-intensity: {0.1 * texture.highlight_intensity};"></div>'

        # The circle div
        # Using texture.css if present
        css_cls = texture.css if texture.css else ""
        circle_html = f'<div class="nt-texture-icon__circle {css_cls}" style="{circle_style}">{gloss_html}</div>'
        
        return f'<div class="nt-texture-icon" style="{wrapper_style}">{circle_html}</div>'


class theme_icon(ui.element):
    """
    A comprehensive icon that displays a visual representation of a complete theme.
    Combines palette, texture, typography, and layout by composing visuals.
    """
    def __init__(
        self, 
        theme: Theme,
        *, 
        size: str = "24px"
    ):
        super().__init__('div')
        
        # Apply base styling
        self.classes('nt-theme-icon-wrapper')
        
        palette = theme.palette
        texture = theme.texture
        layout = theme.layout

        # Calculate shadow directly from texture intensity and apply to wrapper (like texture_icon)
        wrapper_style = f'width: {size}; height: {size};'
        if texture.shadow_intensity > 0:
            # Get shadow color from texture -> from palette
            shadow_ref = palette.shadow
            shadow_hex = palette.resolve_color(shadow_ref)
            r, g, b = hex_to_rgb(shadow_hex)
            
            # Calculate actual shadow based on intensity
            si = texture.shadow_intensity
            
            # Calculate size factor for the shadow (base 24px)
            import re
            size_match = re.match(r'([0-9.]+)(.+)', size)
            size_val = 24.0
            if size_match:
                try: size_val = float(size_match.group(1))
                except: pass
            sf = size_val / 24.0

            # Use tight values scaled by icon size
            if si > 1.5:
                shadow_def = f'0 {10*sf:.1f}px {12*sf:.1f}px rgba({r}, {g}, {b}, {0.4 * si:.2f})'
            elif si > 1.0:
                shadow_def = f'0 {6*sf:.1f}px {8*sf:.1f}px rgba({r}, {g}, {b}, {0.35 * si:.2f})'
            elif si > 0.5:
                shadow_def = f'0 {3*sf:.1f}px {4*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            else:
                shadow_def = f'0 {1*sf:.1f}px {2*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            
            wrapper_style += f' filter: drop-shadow({shadow_def});'
        
        self.style(wrapper_style)
        
        # Create a container with texture effects applied
        with self:
            # Apply texture-based effects to the container
            # Make the visible disk slightly smaller (85%) to match standard icon scale
            texture_container = ui.element('div').classes('nt-theme-icon__container')
            # Width/Height managed by class (85%), alignment by class
            
            # Apply texture opacity 
            if texture.opacity < 1.0:
                texture_container.style(f'opacity: {texture.opacity};')
            
            # Apply shape-based border and roundness (from Texture category)
            border_width_px = f"{max(1.0, float(texture.border_width) * 0.5)}px"  # Scaled for visual balance
            
            # Calculate border radius based on layout.roundness
            if layout.roundness == 0:
                border_radius = '0'
            elif layout.roundness >= 2.0:
                border_radius = '50%'  # Circle
            else:
                radius_percent = (layout.roundness / 2.0) * 50
                border_radius = f'{radius_percent}%'
            
            # The palette icon as the core visual
            with texture_container:
                container = ui.element('div').classes('nt-theme-icon__palette-container')
                container.style(f'''
                    border-radius: {border_radius};
                    border-width: {border_width_px};
                ''')
                
                with container:
                    # Reuse the palette_icon for color visualization
                    # Set to 100% so it fills the texture_container and reaches the corners
                    palette_icon(palette, size="100%", circular=False)

                    # Apply highlight density if applicable - moved here to be inside clipped container
                    if texture.highlight_intensity > 0:
                        ui.element('div').classes('nt-texture-icon__highlight').style(f'--nt-highlight-intensity: {0.1 * texture.highlight_intensity};')

    @staticmethod
    def to_html(
        theme: Theme,
        *, 
        size: str = "24px"
    ) -> str:
        """Returns the full HTML string for this component."""
        palette = theme.palette
        texture = theme.texture
        layout = theme.layout
        
        # Wrapper styles with shadow (match texture_icon behavior)
        wrapper_style = f'width: {size}; height: {size};'
        
        # Calculate shadow directly from texture intensity and apply to wrapper
        # Calculate shadow directly from texture intensity and apply to wrapper
        if texture.shadow_intensity > 0:
            shadow_ref = palette.shadow
            shadow_hex = palette.resolve_color(shadow_ref)
            r, g, b = hex_to_rgb(shadow_hex)
            si = texture.shadow_intensity

            # Calculate size factor for the shadow (base 24px)
            import re
            size_match = re.match(r'([0-9.]+)(.+)', size)
            size_val = 24.0
            if size_match:
                try: size_val = float(size_match.group(1))
                except: pass
            sf = size_val / 24.0

            # Use tight values scaled by icon size
            if si > 1.5:
                shadow_def = f'0 {10*sf:.1f}px {12*sf:.1f}px rgba({r}, {g}, {b}, {0.4 * si:.2f})'
            elif si > 1.0:
                shadow_def = f'0 {6*sf:.1f}px {8*sf:.1f}px rgba({r}, {g}, {b}, {0.35 * si:.2f})'
            elif si > 0.5:
                shadow_def = f'0 {3*sf:.1f}px {4*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            else:
                shadow_def = f'0 {1*sf:.1f}px {2*sf:.1f}px rgba({r}, {g}, {b}, {0.3 * si:.2f})'
            
            wrapper_style += f' filter: drop-shadow({shadow_def});'
        
        # Texture styling
        texture_style = ''
        if texture.opacity < 1.0:
            texture_style += f' opacity: {texture.opacity};'
            
        # Shape styling
        border_width_px = f"{max(1.0, float(texture.border_width) * 0.5)}px"
        
        if layout.roundness == 0:
            border_radius = '0'
        elif layout.roundness >= 2.0:
            border_radius = '50%'
        else:
            radius_percent = (layout.roundness / 2.0) * 50
            border_radius = f'{radius_percent}%'
            
        container_style = f'border-radius: {border_radius}; border-width: {border_width_px};'

        # Inner palette icon HTML (set to 100% to fill corners)
        inner_html = palette_icon.to_html(palette, size="100%", circular=False)
        
        # Gloss effect HTML if highlight_intensity is high
        gloss_html = ""
        if texture.highlight_intensity > 0:
             gloss_html = f'<div class="nt-texture-icon__highlight" style="--nt-highlight-intensity: {0.1 * texture.highlight_intensity};"></div>'

        # Inner Container (Palette Container)
        html_palette_container = f'<div class="nt-theme-icon__palette-container" style="{container_style}">{inner_html}{gloss_html}</div>'
        
        # Texture Container
        html_texture_container = f'<div class="nt-theme-icon__container" style="{texture_style}">{html_palette_container}</div>'
        
        # Outer Wrapper (wrapper_style already includes shadow)
        return f'<div class="nt-theme-icon-wrapper" style="{wrapper_style}">{html_texture_container}</div>'
"""
Premium Logo Design System - Creates stunning, designer-quality logos
Every logo is guaranteed to be visually impressive and professional
"""

import math
import svgwrite
import random
from typing import Dict, List, Tuple, Optional
from .logo_ai import BusinessAnalysis

class PremiumLogoEngine:
    """Advanced logo generator with guaranteed stunning results."""
    
    def __init__(self):
        pass

    def create_stunning_logo(self, business_name: str, business_analysis: BusinessAnalysis, 
                           palette: Dict, layout_style: str = "emblem") -> bytes:
        """Generate a guaranteed stunning, professional logo."""
        
        industry = business_analysis.industry
        colors = palette["colors"]
        
        # Ensure we have at least 2 colors
        if len(colors) < 2:
            colors = [colors[0], "#333333"] if colors else ["#0066cc", "#333333"]
        
        # Choose design based on industry for maximum impact
        if industry == 'tech':
            return self._create_tech_masterpiece(business_name, colors, layout_style)
        elif industry == 'healthcare':
            return self._create_healthcare_masterpiece(business_name, colors, layout_style)
        elif industry == 'finance':
            return self._create_finance_masterpiece(business_name, colors, layout_style)
        elif industry == 'food':
            return self._create_food_masterpiece(business_name, colors, layout_style)
        elif industry == 'creative':
            return self._create_creative_masterpiece(business_name, colors, layout_style)
        else:
            return self._create_business_masterpiece(business_name, colors, layout_style)

    def _create_tech_masterpiece(self, business_name: str, colors: List[str], layout_style: str) -> bytes:
        """Create an impressive tech logo with modern elements."""
        d = svgwrite.Drawing(size=(512, 512))
        d.add(d.rect(insert=(0,0), size=(512, 512), fill="#FFFFFF"))
        
        primary = colors[0]
        secondary = colors[1] if len(colors) > 1 else "#666666"
        
        if layout_style == "emblem":
            return self._tech_emblem_design(d, business_name, primary, secondary)
        else:
            return self._tech_horizontal_design(d, business_name, primary, secondary)

    def _tech_emblem_design(self, d, business_name: str, primary: str, secondary: str) -> bytes:
        """Tech emblem with interconnected network design."""
        center = (256, 200)
        
        # Create sophisticated hexagonal network
        hex_radius = 80
        node_positions = []
        
        # Central hexagon nodes
        for i in range(6):
            angle = i * math.pi / 3
            x = center[0] + hex_radius * math.cos(angle)
            y = center[1] + hex_radius * math.sin(angle)
            node_positions.append((x, y))
        
        # Add center node
        node_positions.append(center)
        
        # Create network connections with gradient effect
        for i in range(6):
            next_i = (i + 1) % 6
            # Outer ring connections
            d.add(d.line(start=node_positions[i], end=node_positions[next_i], 
                        stroke=primary, stroke_width=3, opacity=0.7))
            
            # Connections to center
            d.add(d.line(start=node_positions[i], end=center, 
                        stroke=secondary, stroke_width=2, opacity=0.5))
            
            # Create data flow animation effect with dashed lines
            mid_x = (node_positions[i][0] + node_positions[next_i][0]) / 2
            mid_y = (node_positions[i][1] + node_positions[next_i][1]) / 2
            d.add(d.line(start=node_positions[i], end=(mid_x, mid_y), 
                        stroke=primary, stroke_width=4, opacity=0.9,
                        stroke_dasharray="5,3"))
        
        # Create nodes with modern styling
        for i, pos in enumerate(node_positions[:-1]):  # Exclude center for special treatment
            # Outer glow effect
            d.add(d.circle(center=pos, r=12, fill=primary, opacity=0.3))
            # Main node
            d.add(d.circle(center=pos, r=8, fill=primary))
            # Inner highlight
            d.add(d.circle(center=pos, r=4, fill="#FFFFFF", opacity=0.8))
        
        # Special center node - larger and more prominent
        d.add(d.circle(center=center, r=18, fill=secondary, opacity=0.2))
        d.add(d.circle(center=center, r=14, fill=primary))
        d.add(d.circle(center=center, r=8, fill=secondary))
        d.add(d.circle(center=center, r=4, fill="#FFFFFF"))
        
        # Add circuit-like rectangular elements for tech feel
        rect_positions = [
            (center[0] - 40, center[1] - 15, 80, 8),
            (center[0] - 15, center[1] - 40, 8, 80)
        ]
        
        for x, y, width, height in rect_positions:
            d.add(d.rect(insert=(x, y), size=(width, height), 
                        fill=secondary, opacity=0.6, rx=2))
        
        # Modern business name with tech styling
        d.add(d.text(business_name.upper(), insert=(256, 320), text_anchor="middle",
                    font_family="Arial Black, sans-serif", font_size=28, font_weight="900",
                    fill=primary, letter_spacing="2px"))
        
        # Subtitle line for tech feel
        d.add(d.line(start=(180, 340), end=(332, 340), 
                    stroke=secondary, stroke_width=2, opacity=0.7))
        
        return d.tostring().encode("utf-8")

    def _tech_horizontal_design(self, d, business_name: str, primary: str, secondary: str) -> bytes:
        """Tech horizontal logo with symbol + text."""
        # Create dynamic tech symbol on left
        symbol_center = (140, 256)
        
        # Create interconnected diamond pattern
        diamond_size = 60
        diamonds = [
            (symbol_center[0], symbol_center[1] - 30),  # top
            (symbol_center[0] + 30, symbol_center[1]),  # right
            (symbol_center[0], symbol_center[1] + 30),  # bottom
            (symbol_center[0] - 30, symbol_center[1])   # left
        ]
        
        # Draw diamond network
        for i, diamond in enumerate(diamonds):
            next_diamond = diamonds[(i + 1) % 4]
            d.add(d.line(start=diamond, end=next_diamond, 
                        stroke=primary, stroke_width=4, opacity=0.8))
            
            # Add nodes at diamonds
            d.add(d.circle(center=diamond, r=8, fill=primary))
            d.add(d.circle(center=diamond, r=4, fill="#FFFFFF"))
        
        # Central processing unit
        d.add(d.rect(insert=(symbol_center[0]-15, symbol_center[1]-15), 
                    size=(30, 30), fill=secondary, rx=4))
        d.add(d.rect(insert=(symbol_center[0]-8, symbol_center[1]-8), 
                    size=(16, 16), fill=primary, rx=2))
        
        # Add data flow lines
        flow_lines = [
            ((symbol_center[0]-50, symbol_center[1]), (symbol_center[0]-30, symbol_center[1])),
            ((symbol_center[0]+30, symbol_center[1]), (symbol_center[0]+50, symbol_center[1])),
            ((symbol_center[0], symbol_center[1]-50), (symbol_center[0], symbol_center[1]-30)),
            ((symbol_center[0], symbol_center[1]+30), (symbol_center[0], symbol_center[1]+50))
        ]
        
        for start, end in flow_lines:
            d.add(d.line(start=start, end=end, 
                        stroke=secondary, stroke_width=3, opacity=0.6,
                        stroke_dasharray="8,4"))
        
        # Business name with modern styling
        text_x = 280
        d.add(d.text(business_name.upper(), insert=(text_x, 246), text_anchor="start",
                    font_family="Arial Black, sans-serif", font_size=36, font_weight="900",
                    fill=primary, letter_spacing="1px"))
        
        # Tech tagline or accent
        d.add(d.text("TECHNOLOGY", insert=(text_x, 275), text_anchor="start",
                    font_family="Arial, sans-serif", font_size=12, font_weight="300",
                    fill=secondary, letter_spacing="3px", opacity=0.8))
        
        return d.tostring().encode("utf-8")

    def _create_healthcare_masterpiece(self, business_name: str, colors: List[str], layout_style: str) -> bytes:
        """Create a stunning healthcare logo."""
        d = svgwrite.Drawing(size=(512, 512))
        d.add(d.rect(insert=(0,0), size=(512, 512), fill="#FFFFFF"))
        
        primary = colors[0]
        secondary = colors[1] if len(colors) > 1 else "#2E8B57"
        
        center = (256, 200)
        
        # Create sophisticated medical symbol
        # Protective circle with gradient effect
        d.add(d.circle(center=center, r=90, fill=primary, opacity=0.1))
        d.add(d.circle(center=center, r=80, fill="none", stroke=primary, stroke_width=2, opacity=0.3))
        d.add(d.circle(center=center, r=70, fill="none", stroke=secondary, stroke_width=1, opacity=0.5))
        
        # Modern medical cross
        cross_width = 50
        cross_height = 70
        bar_thickness = 16
        
        # Vertical bar with rounded ends
        d.add(d.rect(insert=(center[0] - bar_thickness//2, center[1] - cross_height//2),
                    size=(bar_thickness, cross_height), rx=8, fill=primary))
        
        # Horizontal bar with rounded ends
        d.add(d.rect(insert=(center[0] - cross_width//2, center[1] - bar_thickness//2),
                    size=(cross_width, bar_thickness), rx=8, fill=primary))
        
        # Add heart symbol integration
        heart_points = [
            (center[0] - 8, center[1] - 8),
            (center[0] - 4, center[1] - 12),
            (center[0], center[1] - 8),
            (center[0] + 4, center[1] - 12),
            (center[0] + 8, center[1] - 8),
            (center[0] + 4, center[1] - 4),
            (center[0], center[1] + 2),
            (center[0] - 4, center[1] - 4)
        ]
        d.add(d.polygon(points=heart_points, fill="#FFFFFF", opacity=0.9))
        
        # Add care hands around the symbol
        for i in range(4):
            angle = i * math.pi / 2
            hand_x = center[0] + 55 * math.cos(angle)
            hand_y = center[1] + 55 * math.sin(angle)
            
            # Hand curve
            if i % 2 == 0:
                path = f"M {hand_x-8},{hand_y-15} Q {hand_x},{hand_y-8} {hand_x+8},{hand_y-15} Q {hand_x},{hand_y-5} {hand_x-8},{hand_y-15}"
                d.add(d.path(d=path, fill=secondary, opacity=0.6))
        
        # Professional business name
        d.add(d.text(business_name, insert=(256, 320), text_anchor="middle",
                    font_family="Georgia, serif", font_size=32, font_weight="400",
                    fill=primary, letter_spacing="1px"))
        
        # Healthcare tagline
        d.add(d.text("HEALTHCARE", insert=(256, 345), text_anchor="middle",
                    font_family="Arial, sans-serif", font_size=14, font_weight="300",
                    fill=secondary, letter_spacing="2px", opacity=0.8))
        
        return d.tostring().encode("utf-8")

    def _create_finance_masterpiece(self, business_name: str, colors: List[str], layout_style: str) -> bytes:
        """Create a powerful finance logo."""
        d = svgwrite.Drawing(size=(512, 512))
        d.add(d.rect(insert=(0,0), size=(512, 512), fill="#FFFFFF"))
        
        primary = colors[0]
        secondary = colors[1] if len(colors) > 1 else "#1B4D72"
        
        center = (256, 200)
        
        # Create premium diamond shape
        diamond_size = 70
        diamond_points = [
            (center[0], center[1] - diamond_size),      # top
            (center[0] + diamond_size, center[1]),      # right
            (center[0], center[1] + diamond_size),      # bottom
            (center[0] - diamond_size, center[1])       # left
        ]
        
        # Diamond with gradient layers
        d.add(d.polygon(points=diamond_points, fill=primary, opacity=0.9))
        
        # Inner diamond for depth
        inner_diamond = [(x + (center[0] - x) * 0.4, y + (center[1] - y) * 0.4) for x, y in diamond_points]
        d.add(d.polygon(points=inner_diamond, fill=secondary, opacity=0.8))
        
        # Central premium element
        d.add(d.circle(center=center, r=20, fill="#FFFFFF"))
        d.add(d.circle(center=center, r=15, fill=primary))
        
        # Growth arrows integrated into design
        arrow_paths = [
            # Upward arrows from diamond corners
            f"M {center[0]-35},{center[1]+35} L {center[0]-25},{center[1]+25} L {center[0]-30},{center[1]+20} L {center[0]-35},{center[1]+25} L {center[0]-25},{center[1]+25}",
            f"M {center[0]+35},{center[1]+35} L {center[0]+45},{center[1]+25} L {center[0]+40},{center[1]+20} L {center[0]+35},{center[1]+25} L {center[0]+45},{center[1]+25}",
        ]
        
        for path in arrow_paths:
            d.add(d.path(d=path, fill=secondary, opacity=0.7))
        
        # Premium border elements
        border_radius = 120
        for i in range(8):
            angle = i * math.pi / 4
            x1 = center[0] + border_radius * math.cos(angle)
            y1 = center[1] + border_radius * math.sin(angle)
            x2 = center[0] + (border_radius - 15) * math.cos(angle)
            y2 = center[1] + (border_radius - 15) * math.sin(angle)
            
            d.add(d.line(start=(x1, y1), end=(x2, y2), 
                        stroke=primary, stroke_width=3, opacity=0.4))
        
        # Elegant business name
        d.add(d.text(business_name.upper(), insert=(256, 320), text_anchor="middle",
                    font_family="Times New Roman, serif", font_size=30, font_weight="bold",
                    fill=primary, letter_spacing="2px"))
        
        # Finance tagline
        d.add(d.text("FINANCIAL SERVICES", insert=(256, 345), text_anchor="middle",
                    font_family="Arial, sans-serif", font_size=12, font_weight="400",
                    fill=secondary, letter_spacing="1.5px", opacity=0.8))
        
        return d.tostring().encode("utf-8")

    def _create_food_masterpiece(self, business_name: str, colors: List[str], layout_style: str) -> bytes:
        """Create an appetizing food logo."""
        d = svgwrite.Drawing(size=(512, 512))
        d.add(d.rect(insert=(0,0), size=(512, 512), fill="#FFFFFF"))
        
        primary = colors[0]
        secondary = colors[1] if len(colors) > 1 else "#8B4513"
        
        center = (256, 200)
        
        # Create artistic chef's hat or food symbol
        if layout_style == "emblem":
            # Chef's hat design
            hat_base = center[1] + 40
            hat_top = center[1] - 50
            
            # Hat body
            d.add(d.ellipse(center=(center[0], hat_base), r=(50, 15), fill=primary))
            d.add(d.rect(insert=(center[0]-50, hat_base-60), size=(100, 60), fill=primary))
            
            # Hat top (puffy)
            puff_centers = [
                (center[0]-30, hat_top+10),
                (center[0], hat_top),
                (center[0]+30, hat_top+10)
            ]
            
            for puff_center in puff_centers:
                d.add(d.circle(center=puff_center, r=25, fill=primary, opacity=0.9))
            
            # Add decorative food elements
            fork_x = center[0] - 80
            knife_x = center[0] + 80
            
            # Fork
            fork_lines = [
                (fork_x-6, center[1]-20, fork_x-6, center[1]+30),
                (fork_x-2, center[1]-20, fork_x-2, center[1]+30),
                (fork_x+2, center[1]-20, fork_x+2, center[1]+30),
                (fork_x+6, center[1]-20, fork_x+6, center[1]+30),
                (fork_x-8, center[1]+30, fork_x+8, center[1]+30)
            ]
            
            for x1, y1, x2, y2 in fork_lines:
                d.add(d.line(start=(x1, y1), end=(x2, y2), 
                            stroke=secondary, stroke_width=3))
            
            # Knife
            d.add(d.rect(insert=(knife_x-2, center[1]-20), size=(4, 50), fill=secondary))
            d.add(d.polygon(points=[(knife_x-8, center[1]-20), (knife_x+8, center[1]-20), 
                                   (knife_x, center[1]-35)], fill=secondary))
        
        else:
            # Organic leaf/natural design
            leaf_path = f"M {center[0]-40},{center[1]} Q {center[0]-20},{center[1]-40} {center[0]},{center[1]-20} Q {center[0]+20},{center[1]-40} {center[0]+40},{center[1]} Q {center[0]+20},{center[1]+20} {center[0]},{center[1]+10} Q {center[0]-20},{center[1]+20} {center[0]-40},{center[1]}"
            d.add(d.path(d=leaf_path, fill=primary, opacity=0.8))
            
            # Leaf veins
            vein_paths = [
                f"M {center[0]-20},{center[1]-10} Q {center[0]},{center[1]} {center[0]+20},{center[1]+10}",
                f"M {center[0]-10},{center[1]-15} Q {center[0]},{center[1]-5} {center[0]+10},{center[1]+5}",
            ]
            
            for vein in vein_paths:
                d.add(d.path(d=vein, stroke=secondary, stroke_width=2, 
                            fill="none", opacity=0.7))
        
        # Warm, inviting business name
        d.add(d.text(business_name, insert=(256, 320), text_anchor="middle",
                    font_family="Georgia, serif", font_size=30, font_weight="400",
                    fill=primary, letter_spacing="0.5px", font_style="italic"))
        
        # Food tagline
        d.add(d.text("CULINARY EXCELLENCE", insert=(256, 345), text_anchor="middle",
                    font_family="Arial, sans-serif", font_size=12, font_weight="300",
                    fill=secondary, letter_spacing="1px", opacity=0.8))
        
        return d.tostring().encode("utf-8")

    def _create_creative_masterpiece(self, business_name: str, colors: List[str], layout_style: str) -> bytes:
        """Create an artistic creative logo."""
        d = svgwrite.Drawing(size=(512, 512))
        d.add(d.rect(insert=(0,0), size=(512, 512), fill="#FFFFFF"))
        
        primary = colors[0]
        secondary = colors[1] if len(colors) > 1 else "#FF6B35"
        accent = colors[2] if len(colors) > 2 else "#F7931E"
        
        center = (256, 200)
        
        # Create dynamic paint splash effect
        splash_elements = [
            # Main splash center
            (center, 40, primary, 1.0),
            # Secondary splashes
            ((center[0]-60, center[1]-30), 25, secondary, 0.8),
            ((center[0]+70, center[1]+20), 30, accent, 0.7),
            ((center[0]-20, center[1]+50), 20, primary, 0.6),
            ((center[0]+40, center[1]-40), 22, secondary, 0.9)
        ]
        
        for (splash_center, radius, color, opacity) in splash_elements:
            # Main splash
            d.add(d.circle(center=splash_center, r=radius, fill=color, opacity=opacity))
            
            # Add paint drips
            for i in range(3):
                angle = random.uniform(0, 2 * math.pi)
                drip_length = random.uniform(15, 25)
                drip_x = splash_center[0] + (radius + 5) * math.cos(angle)
                drip_y = splash_center[1] + (radius + 5) * math.sin(angle)
                drip_end_x = drip_x + drip_length * math.cos(angle + math.pi/2)
                drip_end_y = drip_y + drip_length * math.sin(angle + math.pi/2)
                
                d.add(d.line(start=(drip_x, drip_y), end=(drip_end_x, drip_end_y),
                            stroke=color, stroke_width=4, opacity=opacity*0.7,
                            stroke_linecap="round"))
        
        # Add artistic brush strokes
        brush_strokes = [
            f"M {center[0]-100},{center[1]-60} Q {center[0]-50},{center[1]-80} {center[0]},{center[1]-70} Q {center[0]+50},{center[1]-60} {center[0]+100},{center[1]-40}",
            f"M {center[0]-80},{center[1]+60} Q {center[0]-20},{center[1]+80} {center[0]+30},{center[1]+70} Q {center[0]+80},{center[1]+60} {center[0]+120},{center[1]+50}"
        ]
        
        for i, stroke in enumerate(brush_strokes):
            stroke_color = [secondary, accent][i]
            d.add(d.path(d=stroke, stroke=stroke_color, stroke_width=6, 
                        fill="none", opacity=0.6, stroke_linecap="round"))
        
        # Central creative element - stylized palette
        palette_center = center
        d.add(d.ellipse(center=palette_center, r=(35, 25), fill="#FFFFFF", 
                       stroke=primary, stroke_width=3))
        
        # Color dots on palette
        color_positions = [
            (palette_center[0]-15, palette_center[1]-5),
            (palette_center[0], palette_center[1]-8),
            (palette_center[0]+15, palette_center[1]-5),
            (palette_center[0]-8, palette_center[1]+8),
            (palette_center[0]+8, palette_center[1]+8)
        ]
        
        colors_list = [primary, secondary, accent, primary, secondary]
        for i, pos in enumerate(color_positions):
            d.add(d.circle(center=pos, r=4, fill=colors_list[i]))
        
        # Creative business name
        d.add(d.text(business_name.upper(), insert=(256, 320), text_anchor="middle",
                    font_family="Impact, Arial Black, sans-serif", font_size=32, font_weight="900",
                    fill=primary, letter_spacing="2px"))
        
        # Creative tagline
        d.add(d.text("CREATIVE STUDIO", insert=(256, 345), text_anchor="middle",
                    font_family="Arial, sans-serif", font_size=14, font_weight="300",
                    fill=secondary, letter_spacing="2px", opacity=0.8))
        
        return d.tostring().encode("utf-8")

    def _create_business_masterpiece(self, business_name: str, colors: List[str], layout_style: str) -> bytes:
        """Create a sophisticated business logo."""
        d = svgwrite.Drawing(size=(512, 512))
        d.add(d.rect(insert=(0,0), size=(512, 512), fill="#FFFFFF"))
        
        primary = colors[0]
        secondary = colors[1] if len(colors) > 1 else "#34495E"
        
        center = (256, 200)
        
        # Create professional geometric pattern
        # Interlocking circles representing unity/partnership
        circle1_center = (center[0] - 25, center[1])
        circle2_center = (center[0] + 25, center[1])
        
        # Background circles for depth
        d.add(d.circle(center=circle1_center, r=50, fill=primary, opacity=0.2))
        d.add(d.circle(center=circle2_center, r=50, fill=secondary, opacity=0.2))
        
        # Main circles
        d.add(d.circle(center=circle1_center, r=40, fill="none", 
                      stroke=primary, stroke_width=6))
        d.add(d.circle(center=circle2_center, r=40, fill="none", 
                      stroke=secondary, stroke_width=6))
        
        # Intersection highlight
        d.add(d.circle(center=center, r=15, fill=primary, opacity=0.8))
        d.add(d.circle(center=center, r=8, fill="#FFFFFF"))
        
        # Add professional corner elements
        corner_elements = [
            (170, 130), (342, 130), (170, 270), (342, 270)
        ]
        
        for x, y in corner_elements:
            d.add(d.rect(insert=(x-8, y-8), size=(16, 16), fill=secondary, 
                        opacity=0.3, rx=2))
            d.add(d.rect(insert=(x-4, y-4), size=(8, 8), fill=primary, 
                        opacity=0.6, rx=1))
        
        # Professional business name
        d.add(d.text(business_name.upper(), insert=(256, 320), text_anchor="middle",
                    font_family="Arial, sans-serif", font_size=28, font_weight="600",
                    fill=primary, letter_spacing="1.5px"))
        
        # Business tagline
        d.add(d.text("PROFESSIONAL SERVICES", insert=(256, 345), text_anchor="middle",
                    font_family="Arial, sans-serif", font_size=12, font_weight="300",
                    fill=secondary, letter_spacing="1px", opacity=0.8))
        
        return d.tostring().encode("utf-8")


# Global instance
premium_engine = PremiumLogoEngine()
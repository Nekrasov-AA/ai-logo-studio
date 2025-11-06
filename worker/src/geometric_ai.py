"""
Geometric AI for creating meaningful logo shapes
Based on business analysis and style preferences
"""
import math
import svgwrite
from typing import Dict, List, Tuple, Optional
from .logo_ai import logo_ai

class GeometricAI:
    def __init__(self):
        """Initialize geometric AI with shape archetypes"""
        
        # Shape psychological meanings
        self.shape_psychology = {
            'circle': {'trust': 0.9, 'unity': 0.9, 'completeness': 0.8, 'friendly': 0.8},
            'square': {'stability': 0.9, 'reliability': 0.8, 'professionalism': 0.8, 'structure': 0.9},
            'triangle': {'innovation': 0.8, 'direction': 0.9, 'energy': 0.8, 'growth': 0.7},
            'hexagon': {'efficiency': 0.8, 'nature': 0.7, 'technology': 0.7, 'precision': 0.8},
            'organic': {'creativity': 0.9, 'nature': 0.9, 'flexibility': 0.8, 'human': 0.7}
        }
        
        # Industry shape preferences
        self.industry_shapes = {
            'tech': ['hexagon', 'triangle', 'square'],
            'healthcare': ['circle', 'organic', 'square'],
            'finance': ['square', 'triangle', 'circle'],
            'food': ['circle', 'organic', 'triangle'],
            'retail': ['circle', 'square', 'triangle'],
            'consulting': ['triangle', 'square', 'circle'],
            'creative': ['organic', 'triangle', 'circle'],
            'other': ['circle', 'square', 'triangle']
        }
    
    def select_optimal_shapes(self, business_analysis: Dict) -> List[str]:
        """Select optimal shapes based on business analysis"""
        preferences = business_analysis.get('preferences', {})
        industry = preferences.get('industry', 'other')
        
        # Get industry preferences
        preferred_shapes = self.industry_shapes.get(industry, ['circle', 'square', 'triangle'])
        
        # Adjust based on trust and innovation requirements
        trust_level = business_analysis.get('trustworthiness_need', 0.5)
        innovation_level = business_analysis.get('innovation_level', 0.5)
        
        shape_scores = {}
        for shape in preferred_shapes:
            score = 0.5  # Base score
            
            if shape in self.shape_psychology:
                psych = self.shape_psychology[shape]
                
                # Trust factor
                if trust_level > 0.7:
                    score += psych.get('trust', 0) * 0.3
                    score += psych.get('reliability', 0) * 0.2
                
                # Innovation factor
                if innovation_level > 0.6:
                    score += psych.get('innovation', 0) * 0.3
                    score += psych.get('energy', 0) * 0.2
                
                # Professional factor
                score += psych.get('professionalism', 0.5) * 0.2
            
            shape_scores[shape] = score
        
        # Sort by score and return top shapes
        sorted_shapes = sorted(shape_scores.items(), key=lambda x: x[1], reverse=True)
        return [shape for shape, score in sorted_shapes[:3]]
    
    def create_geometric_logo(self, business_type: str, palette: Dict, 
                            business_analysis: Dict, layout_style: str = "emblem") -> bytes:
        """Create AI-driven geometric logo"""
        
        optimal_shapes = self.select_optimal_shapes(business_analysis)
        primary_shape = optimal_shapes[0] if optimal_shapes else 'circle'
        
        complexity = business_analysis.get('complexity_score', 0.5)
        
        if layout_style == "emblem":
            return self._create_emblem_logo(business_type, palette, primary_shape, complexity)
        elif layout_style == "wordmark":
            return self._create_wordmark_logo(business_type, palette, primary_shape, complexity)
        else:
            return self._create_symbol_text_logo(business_type, palette, primary_shape, complexity)
    
    def _create_emblem_logo(self, business_type: str, palette: Dict, 
                          shape: str, complexity: float, size: int = 512) -> bytes:
        """Create an emblem-style logo with AI-driven geometry"""
        d = svgwrite.Drawing(size=(size, size))
        d.add(d.rect(insert=(0,0), size=(size,size), fill="#FFFFFF"))
        
        colors = palette["colors"]
        center = (size/2, size/2)
        
        # Create main shape based on AI analysis
        if shape == 'circle':
            self._add_circle_emblem(d, center, colors, complexity, size)
        elif shape == 'square':
            self._add_square_emblem(d, center, colors, complexity, size)
        elif shape == 'triangle':
            self._add_triangle_emblem(d, center, colors, complexity, size)
        elif shape == 'hexagon':
            self._add_hexagon_emblem(d, center, colors, complexity, size)
        else:  # organic
            self._add_organic_emblem(d, center, colors, complexity, size)
        
        # Add text
        initials = self._extract_initials(business_type)
        self._add_centered_text(d, initials, center, colors, size)
        
        # Add business name below
        self._add_business_name(d, business_type, colors, size)
        
        return d.tostring().encode("utf-8")
    
    def _create_wordmark_logo(self, business_type: str, palette: Dict, 
                            shape: str, complexity: float, size: int = 512) -> bytes:
        """Create a wordmark logo with geometric elements"""
        d = svgwrite.Drawing(size=(size, size))
        d.add(d.rect(insert=(0,0), size=(size,size), fill="#FFFFFF"))
        
        colors = palette["colors"]
        
        # Create stylized text with geometric accents
        self._add_stylized_wordmark(d, business_type, colors, shape, complexity, size)
        
        return d.tostring().encode("utf-8")
    
    def _create_symbol_text_logo(self, business_type: str, palette: Dict, 
                               shape: str, complexity: float, size: int = 512) -> bytes:
        """Create symbol + text combination logo"""
        d = svgwrite.Drawing(size=(size, size))
        d.add(d.rect(insert=(0,0), size=(size,size), fill="#FFFFFF"))
        
        colors = palette["colors"]
        
        # Symbol on left, text on right
        symbol_center = (size * 0.25, size * 0.5)
        text_x = size * 0.45
        
        # Create geometric symbol
        self._add_geometric_symbol(d, symbol_center, colors, shape, complexity, size * 0.3)
        
        # Add text
        self._add_horizontal_text(d, business_type, text_x, size * 0.5, colors, size)
        
        return d.tostring().encode("utf-8")
    
    # Geometric shape implementations
    def _add_circle_emblem(self, d, center, colors, complexity, size):
        """Add AI-enhanced circle emblem"""
        radius = size * 0.18
        
        if complexity > 0.6:
            # Multiple concentric circles
            d.add(d.circle(center=center, r=radius * 1.1, fill=colors[1], opacity=0.3))
        
        d.add(d.circle(center=center, r=radius, fill=colors[0]))
        
        if complexity > 0.4:
            # Inner accent circle
            d.add(d.circle(center=center, r=radius * 0.6, fill=colors[1], opacity=0.7))
    
    def _add_square_emblem(self, d, center, colors, complexity, size):
        """Add AI-enhanced square emblem"""
        side = size * 0.32
        x = center[0] - side/2
        y = center[1] - side/2
        
        # Rounded corners based on complexity
        corner_radius = size * (0.02 + complexity * 0.03)
        
        if complexity > 0.5:
            # Shadow/background square
            d.add(d.rect(insert=(x + size*0.01, y + size*0.01), 
                        size=(side, side), rx=corner_radius, 
                        fill=colors[1], opacity=0.3))
        
        d.add(d.rect(insert=(x, y), size=(side, side), 
                    rx=corner_radius, fill=colors[0]))
    
    def _add_triangle_emblem(self, d, center, colors, complexity, size):
        """Add AI-enhanced triangle emblem"""
        radius = size * 0.18
        points = []
        
        # Equilateral triangle
        for i in range(3):
            angle = (i * 2 * math.pi / 3) - math.pi/2  # Start from top
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        
        if complexity > 0.5:
            # Background triangle (slightly larger)
            bg_points = []
            bg_radius = radius * 1.1
            for i in range(3):
                angle = (i * 2 * math.pi / 3) - math.pi/2
                x = center[0] + bg_radius * math.cos(angle)
                y = center[1] + bg_radius * math.sin(angle)
                bg_points.append((x, y))
            
            d.add(d.polygon(points=bg_points, fill=colors[1], opacity=0.3))
        
        d.add(d.polygon(points=points, fill=colors[0]))
    
    def _add_hexagon_emblem(self, d, center, colors, complexity, size):
        """Add AI-enhanced hexagon emblem"""
        radius = size * 0.18
        points = []
        
        # Regular hexagon
        for i in range(6):
            angle = i * math.pi / 3
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        
        d.add(d.polygon(points=points, fill=colors[0]))
        
        if complexity > 0.4:
            # Inner hexagon accent
            inner_points = []
            inner_radius = radius * 0.6
            for i in range(6):
                angle = i * math.pi / 3
                x = center[0] + inner_radius * math.cos(angle)
                y = center[1] + inner_radius * math.sin(angle)
                inner_points.append((x, y))
            
            d.add(d.polygon(points=inner_points, fill=colors[1], opacity=0.7))
    
    def _add_organic_emblem(self, d, center, colors, complexity, size):
        """Add AI-enhanced organic shape emblem"""
        # Create organic shape using curved paths
        radius = size * 0.16
        
        # Create smooth organic shape with bezier curves
        path_data = f"M {center[0] - radius} {center[1]}"
        
        # Add smooth curves to create organic feel
        control_points = [
            (center[0] - radius*0.5, center[1] - radius*0.8),
            (center[0] + radius*0.5, center[1] - radius*0.8),
            (center[0] + radius, center[1]),
            (center[0] + radius*0.5, center[1] + radius*0.8),
            (center[0] - radius*0.5, center[1] + radius*0.8)
        ]
        
        for i, (x, y) in enumerate(control_points):
            if i == 0:
                path_data += f" C {x} {y}"
            else:
                path_data += f" {x} {y}"
        
        path_data += " Z"
        
        d.add(d.path(d=path_data, fill=colors[0]))
    
    # Text helper methods
    def _extract_initials(self, business_type: str) -> str:
        """Extract meaningful initials from business name"""
        words = [w.strip() for w in business_type.split() if w.strip()]
        if not words:
            return "AI"
        if len(words) == 1:
            return words[0][:2].upper()
        return "".join(w[0] for w in words[:3]).upper()
    
    def _add_centered_text(self, d, text: str, center, colors, size):
        """Add centered text to logo"""
        font_size = size * (0.12 if len(text) <= 2 else 0.08)
        d.add(d.text(text,
                    insert=(center[0], center[1] + font_size*0.3),
                    text_anchor="middle",
                    font_size=font_size,
                    font_family="Arial, sans-serif",
                    font_weight="bold",
                    fill="#FFFFFF"))
    
    def _add_business_name(self, d, business_type: str, colors, size):
        """Add business name below emblem"""
        d.add(d.text(business_type.title(),
                    insert=(size/2, size*0.8),
                    text_anchor="middle",
                    font_size=size*0.06,
                    font_family="Arial, sans-serif",
                    font_weight="500",
                    fill=colors[3] if len(colors) > 3 else "#333333"))
    
    def _add_stylized_wordmark(self, d, business_type: str, colors, shape: str, complexity: float, size):
        """Create stylized wordmark with geometric elements"""
        font_size = size * 0.12
        y_pos = size * 0.5
        
        # Add geometric accent based on primary shape
        if shape == 'circle':
            accent_r = size * 0.03
            d.add(d.circle(center=(size*0.15, y_pos - font_size*0.2), 
                          r=accent_r, fill=colors[0]))
        
        # Main text
        d.add(d.text(business_type.title(),
                    insert=(size*0.25, y_pos),
                    font_size=font_size,
                    font_family="Arial, sans-serif",
                    font_weight="bold",
                    fill=colors[0]))
    
    def _add_geometric_symbol(self, d, center, colors, shape: str, complexity: float, symbol_size: float):
        """Add geometric symbol"""
        if shape == 'circle':
            d.add(d.circle(center=center, r=symbol_size*0.3, fill=colors[0]))
        elif shape == 'square':
            side = symbol_size * 0.5
            x, y = center[0] - side/2, center[1] - side/2
            d.add(d.rect(insert=(x, y), size=(side, side), 
                        rx=symbol_size*0.05, fill=colors[0]))
        # Add other shapes as needed
    
    def _add_horizontal_text(self, d, business_type: str, x: float, y: float, colors, size):
        """Add horizontal text for symbol+text layout"""
        d.add(d.text(business_type.title(),
                    insert=(x, y),
                    font_size=size*0.08,
                    font_family="Arial, sans-serif",
                    font_weight="600",
                    fill=colors[0]))

# Global geometric AI instance
geometric_ai = GeometricAI()
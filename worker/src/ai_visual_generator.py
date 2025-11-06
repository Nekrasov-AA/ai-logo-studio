"""
Advanced SVG Generator powered by AI Analysis
Creates unique, sophisticated logos based on AI-driven concepts
"""

import math
import svgwrite
import random
import hashlib
from typing import Dict, List, Tuple, Optional
from .hybrid_ai import hybrid_ai

class AIVisualGenerator:
    """Advanced SVG generator that creates unique designs from AI concepts."""
    
    def __init__(self):
        self.golden_ratio = 1.618
        self.design_cache = {}
        
    async def create_ai_powered_logo(self, business_name: str, business_type: str, 
                                   description: str, palette: Dict, 
                                   layout_style: str = "emblem") -> bytes:
        """Generate unique logo based on AI analysis."""
        
        # Get AI brand analysis
        ai_analysis = await hybrid_ai.analyze_brand_with_ai(
            business_name, business_type, description
        )
        
        # Create unique design based on analysis
        design_seed = self._create_design_seed(business_name, ai_analysis)
        
        # Generate SVG based on AI concepts
        return self._generate_concept_based_svg(
            business_name, ai_analysis, palette, layout_style, design_seed
        )
    
    def _create_design_seed(self, business_name: str, ai_analysis: Dict) -> str:
        """Create unique design seed for consistent variation."""
        seed_data = f"{business_name}_{ai_analysis.get('industry_classification', 'other')}_"
        seed_data += "_".join(ai_analysis.get('brand_personality', []))
        return hashlib.md5(seed_data.encode()).hexdigest()[:8]
    
    def _generate_concept_based_svg(self, business_name: str, ai_analysis: Dict, 
                                   palette: Dict, layout_style: str, design_seed: str) -> bytes:
        """Generate SVG based on AI concepts and analysis."""
        
        d = svgwrite.Drawing(size=(512, 512))
        d.add(d.rect(insert=(0,0), size=(512, 512), fill="#FFFFFF"))
        
        # Extract AI analysis
        industry = ai_analysis.get('industry_classification', 'other')
        personality = ai_analysis.get('brand_personality', ['professional'])
        metaphors = ai_analysis.get('visual_metaphors', ['professional symbol'])
        color_info = ai_analysis.get('color_psychology', {})
        concepts = ai_analysis.get('logo_concepts', [])
        
        colors = palette.get("colors", ["#0066cc", "#666666"])
        primary = colors[0]
        secondary = colors[1] if len(colors) > 1 else "#666666"
        accent = colors[2] if len(colors) > 2 else primary
        
        # Use design seed for consistent randomization
        random.seed(design_seed)
        
        # Select concept based on AI analysis
        if concepts and len(concepts) > 0:
            selected_concept = concepts[0]
            return self._render_specific_concept(d, business_name, selected_concept, 
                                               primary, secondary, accent, personality)
        
        # Fallback to metaphor-based generation
        primary_metaphor = metaphors[0] if metaphors else "professional symbol"
        
        if industry == 'tech':
            return self._create_ai_tech_logo(d, business_name, primary_metaphor, 
                                           primary, secondary, accent, personality, design_seed)
        elif industry == 'healthcare':
            return self._create_ai_healthcare_logo(d, business_name, primary_metaphor,
                                                 primary, secondary, accent, personality, design_seed)
        elif industry == 'finance':
            return self._create_ai_finance_logo(d, business_name, primary_metaphor,
                                              primary, secondary, accent, personality, design_seed)
        elif industry == 'creative':
            return self._create_ai_creative_logo(d, business_name, primary_metaphor,
                                               primary, secondary, accent, personality, design_seed)
        elif industry == 'food':
            return self._create_ai_food_logo(d, business_name, primary_metaphor,
                                           primary, secondary, accent, personality, design_seed)
        else:
            return self._create_ai_business_logo(d, business_name, primary_metaphor,
                                               primary, secondary, accent, personality, design_seed)
    
    def _render_specific_concept(self, d, business_name: str, concept: Dict,
                               primary: str, secondary: str, accent: str, 
                               personality: List[str]) -> bytes:
        """Render logo based on specific AI concept."""
        
        center = (256, 200)
        concept_desc = concept.get('visual_description', '').lower()
        
        # Parse concept description for visual elements
        if 'network' in concept_desc or 'connected' in concept_desc:
            self._add_network_elements(d, center, primary, secondary, personality)
        elif 'flow' in concept_desc or 'dynamic' in concept_desc:
            self._add_flow_elements(d, center, primary, secondary, personality)
        elif 'geometric' in concept_desc:
            self._add_geometric_elements(d, center, primary, secondary, personality)
        elif 'organic' in concept_desc or 'natural' in concept_desc:
            self._add_organic_elements(d, center, primary, secondary, personality)
        else:
            # Default sophisticated design
            self._add_premium_elements(d, center, primary, secondary, personality)
        
        # Add business name with appropriate styling
        self._add_styled_text(d, business_name, primary, personality)
        
        return d.tostring().encode("utf-8")
    
    def _create_ai_tech_logo(self, d, business_name: str, metaphor: str,
                           primary: str, secondary: str, accent: str,
                           personality: List[str], seed: str) -> bytes:
        """Create AI-powered tech logo with unique variations."""
        
        center = (256, 200)
        
        # Seed-based variations
        variation = int(seed[:2], 16) % 4
        
        if variation == 0:
            # Neural network style
            self._create_neural_network(d, center, primary, secondary, personality)
        elif variation == 1:
            # Data matrix style  
            self._create_data_matrix(d, center, primary, secondary, personality)
        elif variation == 2:
            # Quantum grid style
            self._create_quantum_grid(d, center, primary, secondary, personality)
        else:
            # Circuit board style
            self._create_circuit_board(d, center, primary, secondary, personality)
        
        self._add_styled_text(d, business_name, primary, personality)
        return d.tostring().encode("utf-8")
    
    def _create_neural_network(self, d, center: Tuple[int, int], 
                             primary: str, secondary: str, personality: List[str]):
        """Create sophisticated neural network visualization."""
        
        # Multiple layers with different node counts
        layers = [
            (center[0] - 100, [center[1] - 60, center[1], center[1] + 60]),  # Input layer - 3 nodes
            (center[0] - 30, [center[1] - 80, center[1] - 25, center[1] + 25, center[1] + 80]),  # Hidden - 4 nodes
            (center[0] + 30, [center[1] - 40, center[1], center[1] + 40]),   # Hidden - 3 nodes
            (center[0] + 100, [center[1] - 20, center[1] + 20])             # Output - 2 nodes
        ]
        
        # Draw connections with varying weights (thickness)
        for layer_idx in range(len(layers) - 1):
            current_layer = layers[layer_idx]
            next_layer = layers[layer_idx + 1]
            
            for current_y in current_layer[1]:
                for next_y in next_layer[1]:
                    # Connection strength based on position
                    weight = 1 + abs(current_y - next_y) / 50
                    opacity = max(0.3, 1.0 - weight / 5)
                    
                    d.add(d.line(
                        start=(current_layer[0], current_y),
                        end=(next_layer[0], next_y),
                        stroke=secondary, stroke_width=int(weight), opacity=opacity
                    ))
        
        # Draw nodes with activation levels
        for layer_idx, (x, y_positions) in enumerate(layers):
            for y_pos in y_positions:
                # Node size based on layer importance
                node_size = 12 if layer_idx in [0, -1] else 8
                
                # Outer glow
                d.add(d.circle(center=(x, y_pos), r=node_size + 4, 
                              fill=primary, opacity=0.3))
                # Main node
                d.add(d.circle(center=(x, y_pos), r=node_size, 
                              fill=primary))
                # Inner activation
                d.add(d.circle(center=(x, y_pos), r=node_size - 4, 
                              fill=secondary, opacity=0.8))
                # Core
                d.add(d.circle(center=(x, y_pos), r=node_size - 8, 
                              fill="#FFFFFF"))
    
    def _create_data_matrix(self, d, center: Tuple[int, int],
                          primary: str, secondary: str, personality: List[str]):
        """Create dynamic data matrix visualization."""
        
        # Grid of data points with flowing animation suggestion
        grid_size = 8
        cell_size = 16
        start_x = center[0] - (grid_size * cell_size) // 2
        start_y = center[1] - (grid_size * cell_size) // 2
        
        for row in range(grid_size):
            for col in range(grid_size):
                x = start_x + col * cell_size
                y = start_y + row * cell_size
                
                # Create data flow effect
                flow_intensity = abs(row - col) / grid_size
                opacity = 0.3 + flow_intensity * 0.7
                
                # Different shapes for data points
                if (row + col) % 3 == 0:
                    d.add(d.circle(center=(x, y), r=4, 
                                  fill=primary, opacity=opacity))
                elif (row + col) % 3 == 1:
                    d.add(d.rect(insert=(x-3, y-3), size=(6, 6), 
                                fill=secondary, opacity=opacity, rx=1))
                else:
                    # Diamond shape
                    points = [(x, y-4), (x+4, y), (x, y+4), (x-4, y)]
                    d.add(d.polygon(points=points, fill=primary, opacity=opacity))
        
        # Add data flow lines
        for i in range(3):
            flow_y = center[1] - 30 + i * 30
            d.add(d.line(
                start=(start_x - 20, flow_y),
                end=(start_x + grid_size * cell_size + 20, flow_y),
                stroke=secondary, stroke_width=2, opacity=0.6,
                stroke_dasharray=f"{8 + i * 2},{4 + i}"
            ))
    
    def _create_quantum_grid(self, d, center: Tuple[int, int],
                           primary: str, secondary: str, personality: List[str]):
        """Create quantum-inspired grid pattern."""
        
        # Hexagonal quantum grid
        hex_radius = 25
        rows, cols = 4, 5
        
        for row in range(rows):
            for col in range(cols):
                # Hexagonal grid offset
                offset_x = (col - cols//2) * hex_radius * 1.5
                offset_y = (row - rows//2) * hex_radius * math.sqrt(3)/2
                if row % 2:
                    offset_x += hex_radius * 0.75
                
                hex_center = (center[0] + offset_x, center[1] + offset_y)
                
                # Quantum state visualization
                state_intensity = (row * cols + col) / (rows * cols)
                
                # Hexagon outline
                hex_points = []
                for i in range(6):
                    angle = i * math.pi / 3
                    x = hex_center[0] + hex_radius * 0.8 * math.cos(angle)
                    y = hex_center[1] + hex_radius * 0.8 * math.sin(angle)
                    hex_points.append((x, y))
                
                d.add(d.polygon(points=hex_points, fill="none", 
                               stroke=primary, stroke_width=2, 
                               opacity=0.4 + state_intensity * 0.6))
                
                # Quantum particle at center
                particle_size = 3 + state_intensity * 5
                d.add(d.circle(center=hex_center, r=particle_size,
                              fill=secondary, opacity=0.8))
                
                # Energy field
                d.add(d.circle(center=hex_center, r=particle_size * 2,
                              fill=primary, opacity=0.2))
    
    def _create_circuit_board(self, d, center: Tuple[int, int],
                            primary: str, secondary: str, personality: List[str]):
        """Create sophisticated circuit board pattern."""
        
        # Main circuit paths
        paths = [
            f"M {center[0]-80},{center[1]-40} L {center[0]-40},{center[1]-40} L {center[0]-40},{center[1]} L {center[0]},{center[1]} L {center[0]},{center[1]+40} L {center[0]+40},{center[1]+40} L {center[0]+80},{center[1]+40}",
            f"M {center[0]-80},{center[1]+20} L {center[0]-20},{center[1]+20} L {center[0]-20},{center[1]-20} L {center[0]+20},{center[1]-20} L {center[0]+20},{center[1]+60} L {center[0]+80},{center[1]+60}",
            f"M {center[0]-60},{center[1]-60} L {center[0]-60},{center[1]-20} L {center[0]+40},{center[1]-20} L {center[0]+40},{center[1]+20} L {center[0]+80},{center[1]+20}"
        ]
        
        # Draw circuit paths
        for i, path in enumerate(paths):
            d.add(d.path(d=path, stroke=primary, stroke_width=3, 
                        fill="none", opacity=0.7 + i * 0.1))
        
        # Add electronic components
        component_positions = [
            (center[0]-60, center[1]-40, 'resistor'),
            (center[0], center[1], 'chip'),
            (center[0]+40, center[1]+40, 'capacitor'),
            (center[0]-20, center[1]+20, 'diode'),
            (center[0]+20, center[1]-20, 'transistor')
        ]
        
        for x, y, component_type in component_positions:
            if component_type == 'chip':
                # Main processor chip
                d.add(d.rect(insert=(x-15, y-10), size=(30, 20), 
                            fill=secondary, rx=2))
                d.add(d.rect(insert=(x-10, y-5), size=(20, 10), 
                            fill=primary, rx=1))
                # Chip pins
                for pin in range(4):
                    pin_x = x - 15 + pin * 10
                    d.add(d.rect(insert=(pin_x, y-12), size=(2, 4), 
                                fill=secondary))
                    d.add(d.rect(insert=(pin_x, y+8), size=(2, 4), 
                                fill=secondary))
            else:
                # Generic component
                d.add(d.circle(center=(x, y), r=6, fill=primary))
                d.add(d.circle(center=(x, y), r=3, fill=secondary))
    
    def _add_network_elements(self, d, center: Tuple[int, int],
                            primary: str, secondary: str, personality: List[str]):
        """Add network-style elements."""
        # Similar to neural network but more interconnected
        self._create_neural_network(d, center, primary, secondary, personality)
    
    def _add_flow_elements(self, d, center: Tuple[int, int],
                         primary: str, secondary: str, personality: List[str]):
        """Add dynamic flow elements."""
        # Flowing curves and streams
        flow_paths = [
            f"M {center[0]-100},{center[1]-30} Q {center[0]-50},{center[1]-60} {center[0]},{center[1]-30} Q {center[0]+50},{center[1]} {center[0]+100},{center[1]-30}",
            f"M {center[0]-100},{center[1]+10} Q {center[0]-30},{center[1]+40} {center[0]+20},{center[1]+10} Q {center[0]+70},{center[1]-20} {center[0]+100},{center[1]+10}",
            f"M {center[0]-80},{center[1]+50} Q {center[0]},{center[1]+20} {center[0]+80},{center[1]+50}"
        ]
        
        for i, path in enumerate(flow_paths):
            d.add(d.path(d=path, stroke=primary, stroke_width=4-i, 
                        fill="none", opacity=0.8-i*0.2))
        
        # Flow particles
        particle_positions = [
            (center[0]-60, center[1]-45), (center[0]-20, center[1]-35), (center[0]+40, center[1]-25),
            (center[0]-40, center[1]+25), (center[0]+20, center[1]+5), (center[0]+60, center[1]+15),
            (center[0]-20, center[1]+35), (center[0]+20, center[1]+45)
        ]
        
        for i, (x, y) in enumerate(particle_positions):
            size = 3 + (i % 3)
            d.add(d.circle(center=(x, y), r=size, fill=secondary, opacity=0.7))
    
    def _add_geometric_elements(self, d, center: Tuple[int, int],
                              primary: str, secondary: str, personality: List[str]):
        """Add geometric design elements."""
        # Sacred geometry inspired
        
        # Golden ratio spiral approximation
        phi = self.golden_ratio
        spiral_points = []
        
        for i in range(20):
            angle = i * 0.5
            radius = 10 * (phi ** (angle / 5))
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            spiral_points.append((x, y))
        
        # Draw spiral path
        if len(spiral_points) > 1:
            path_d = f"M {spiral_points[0][0]},{spiral_points[0][1]}"
            for point in spiral_points[1:]:
                path_d += f" L {point[0]},{point[1]}"
            
            d.add(d.path(d=path_d, stroke=primary, stroke_width=3, 
                        fill="none", opacity=0.7))
        
        # Geometric shapes at key points
        shapes = [
            (center[0]-40, center[1]-40, 'triangle'),
            (center[0]+40, center[1]-40, 'square'),
            (center[0], center[1]+50, 'pentagon')
        ]
        
        for x, y, shape in shapes:
            if shape == 'triangle':
                points = [(x, y-15), (x+13, y+10), (x-13, y+10)]
                d.add(d.polygon(points=points, fill=secondary, opacity=0.6))
            elif shape == 'square':
                d.add(d.rect(insert=(x-10, y-10), size=(20, 20), 
                            fill=primary, opacity=0.6, rx=2))
            elif shape == 'pentagon':
                points = []
                for i in range(5):
                    angle = i * 2 * math.pi / 5 - math.pi/2
                    px = x + 12 * math.cos(angle)
                    py = y + 12 * math.sin(angle)
                    points.append((px, py))
                d.add(d.polygon(points=points, fill=secondary, opacity=0.6))
    
    def _add_organic_elements(self, d, center: Tuple[int, int],
                            primary: str, secondary: str, personality: List[str]):
        """Add organic, natural elements."""
        # Leaf/plant inspired design
        
        # Main organic shape (leaf)
        leaf_path = f"M {center[0]-50},{center[1]} Q {center[0]-30},{center[1]-40} {center[0]},{center[1]-20} Q {center[0]+30},{center[1]-40} {center[0]+50},{center[1]} Q {center[0]+30},{center[1]+40} {center[0]},{center[1]+20} Q {center[0]-30},{center[1]+40} {center[0]-50},{center[1]}"
        d.add(d.path(d=leaf_path, fill=primary, opacity=0.7))
        
        # Leaf veins
        vein_paths = [
            f"M {center[0]-25},{center[1]-10} Q {center[0]},{center[1]} {center[0]+25},{center[1]+10}",
            f"M {center[0]-15},{center[1]-20} Q {center[0]},{center[1]-10} {center[0]+15},{center[1]}",
            f"M {center[0]-15},{center[1]+20} Q {center[0]},{center[1]+10} {center[0]+15},{center[1]}"
        ]
        
        for vein in vein_paths:
            d.add(d.path(d=vein, stroke=secondary, stroke_width=2, 
                        fill="none", opacity=0.8))
        
        # Organic dots/berries
        berry_positions = [
            (center[0]-60, center[1]-30), (center[0]+60, center[1]-30),
            (center[0]-60, center[1]+30), (center[0]+60, center[1]+30)
        ]
        
        for x, y in berry_positions:
            d.add(d.circle(center=(x, y), r=6, fill=secondary, opacity=0.6))
            d.add(d.circle(center=(x, y), r=3, fill=primary, opacity=0.8))
    
    def _add_premium_elements(self, d, center: Tuple[int, int],
                            primary: str, secondary: str, personality: List[str]):
        """Add premium design elements."""
        # Sophisticated interlocking shapes
        
        # Diamond framework
        diamond_size = 60
        diamond_points = [
            (center[0], center[1] - diamond_size),
            (center[0] + diamond_size, center[1]),
            (center[0], center[1] + diamond_size),
            (center[0] - diamond_size, center[1])
        ]
        
        d.add(d.polygon(points=diamond_points, fill="none", 
                       stroke=primary, stroke_width=3, opacity=0.7))
        
        # Inner circle
        d.add(d.circle(center=center, r=diamond_size*0.6, fill="none",
                      stroke=secondary, stroke_width=2, opacity=0.8))
        
        # Central premium element
        d.add(d.circle(center=center, r=20, fill=primary))
        d.add(d.circle(center=center, r=12, fill=secondary, opacity=0.8))
        d.add(d.circle(center=center, r=6, fill="#FFFFFF"))
        
        # Corner accents
        accent_positions = [
            (center[0]-diamond_size*0.7, center[1]-diamond_size*0.7),
            (center[0]+diamond_size*0.7, center[1]-diamond_size*0.7),
            (center[0]-diamond_size*0.7, center[1]+diamond_size*0.7),
            (center[0]+diamond_size*0.7, center[1]+diamond_size*0.7)
        ]
        
        for x, y in accent_positions:
            d.add(d.rect(insert=(x-4, y-4), size=(8, 8), 
                        fill=secondary, opacity=0.5, rx=2))
    
    def _add_styled_text(self, d, business_name: str, primary: str, 
                        personality: List[str]):
        """Add professionally styled business name."""
        
        # Determine font style based on personality
        if 'playful' in personality:
            font_family = "Arial Black, sans-serif"
            font_weight = "900"
            letter_spacing = "1px"
        elif 'elegant' in personality or 'premium' in personality:
            font_family = "Times New Roman, serif"
            font_weight = "400"
            letter_spacing = "2px"
        elif 'innovative' in personality or 'bold' in personality:
            font_family = "Arial, sans-serif"
            font_weight = "700"
            letter_spacing = "1.5px"
        else:
            font_family = "Arial, sans-serif"
            font_weight = "500"
            letter_spacing = "1px"
        
        # Business name
        d.add(d.text(business_name.upper(), insert=(256, 320), text_anchor="middle",
                    font_family=font_family, font_size=28, font_weight=font_weight,
                    fill=primary, letter_spacing=letter_spacing))
        
        # Add decorative line if elegant
        if 'elegant' in personality or 'premium' in personality:
            line_length = len(business_name) * 8
            d.add(d.line(start=(256 - line_length//2, 340), 
                        end=(256 + line_length//2, 340),
                        stroke=primary, stroke_width=1, opacity=0.6))
    
    def _create_ai_food_logo(self, d, business_name: str, metaphor: str,
                           primary: str, secondary: str, accent: str,
                           personality: List[str], seed: str) -> bytes:
        """Create AI-powered food industry logo."""
        
        center = (256, 200)
        
        # Food-related organic elements
        # Main organic shape (fruit/leaf)
        organic_path = f"M {center[0]-60},{center[1]} Q {center[0]-40},{center[1]-50} {center[0]},{center[1]-30} Q {center[0]+40},{center[1]-50} {center[0]+60},{center[1]} Q {center[0]+40},{center[1]+50} {center[0]},{center[1]+30} Q {center[0]-40},{center[1]+50} {center[0]-60},{center[1]}"
        d.add(d.path(d=organic_path, fill=primary, opacity=0.8))
        
        # Add food elements
        berry_positions = [
            (center[0]-30, center[1]-20), (center[0]+30, center[1]-20),
            (center[0]-20, center[1]+15), (center[0]+20, center[1]+15)
        ]
        
        for x, y in berry_positions:
            d.add(d.circle(center=(x, y), r=8, fill=secondary, opacity=0.7))
            d.add(d.circle(center=(x, y), r=4, fill=accent))
        
        self._add_styled_text(d, business_name, primary, personality)
        return d.tostring().encode("utf-8")
    
    def _create_ai_business_logo(self, d, business_name: str, metaphor: str,
                               primary: str, secondary: str, accent: str,
                               personality: List[str], seed: str) -> bytes:
        """Create AI-powered general business logo."""
        
        center = (256, 200)
        
        # Professional business elements
        # Main diamond/hexagon shape
        shape_points = []
        sides = 6  # Hexagon for versatility
        
        for i in range(sides):
            angle = i * 2 * math.pi / sides
            x = center[0] + 50 * math.cos(angle)
            y = center[1] + 50 * math.sin(angle)
            shape_points.append((x, y))
        
        d.add(d.polygon(points=shape_points, fill="none", 
                       stroke=primary, stroke_width=4, opacity=0.8))
        
        # Inner elements based on personality
        if 'innovative' in personality:
            # Tech-inspired center
            d.add(d.circle(center=center, r=25, fill=secondary, opacity=0.6))
            d.add(d.circle(center=center, r=15, fill=primary))
            d.add(d.circle(center=center, r=8, fill="#FFFFFF"))
        else:
            # Classic business center
            d.add(d.rect(insert=(center[0]-20, center[1]-20), size=(40, 40),
                        fill=secondary, opacity=0.7, rx=5))
            d.add(d.rect(insert=(center[0]-12, center[1]-12), size=(24, 24),
                        fill=primary, rx=3))
        
        # Corner accents
        accent_positions = [
            (center[0]-35, center[1]-35), (center[0]+35, center[1]-35),
            (center[0]-35, center[1]+35), (center[0]+35, center[1]+35)
        ]
        
        for x, y in accent_positions:
            d.add(d.circle(center=(x, y), r=6, fill=accent, opacity=0.6))
        
        self._add_styled_text(d, business_name, primary, personality)
        return d.tostring().encode("utf-8")


# Global instance  
ai_visual_generator = AIVisualGenerator()
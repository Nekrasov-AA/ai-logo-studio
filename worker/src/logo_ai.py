"""
Rule-based AI logo analysis and generation system.
Uses semantic keyword matching, color theory, and business analysis.
"""

import json
import re
import logging
import random
import hashlib
import math
import colorsys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BusinessAnalysis:
    """Business analysis results from AI processing."""
    industry: str
    keywords: List[str]
    complexity: float
    style_preferences: List[str]
    target_audience: str
    brand_personality: List[str]
    recommended_colors: List[Tuple[int, int, int]]


class LogoAI:
    """Rule-based AI logo analysis and generation system."""
    
    def __init__(self):
        """Initialize AI components."""
        # Use rule-based AI for better reliability and faster startup
        logger.info("Logo AI initialized with rule-based semantic analysis")
        
        # Industry keyword mappings for semantic analysis
        self.industry_keywords = {
            'tech': ['technology', 'software', 'digital', 'innovation', 'ai', 'data', 'cloud', 'app', 'platform', 'system'],
            'healthcare': ['medical', 'health', 'care', 'wellness', 'hospital', 'doctor', 'therapy', 'clinic', 'pharmacy'],
            'finance': ['bank', 'investment', 'money', 'financial', 'insurance', 'trading', 'loan', 'credit', 'payment'],
            'food': ['restaurant', 'food', 'kitchen', 'cooking', 'cafe', 'bakery', 'catering', 'dining', 'chef', 'cuisine'],
            'retail': ['store', 'shop', 'fashion', 'clothing', 'boutique', 'market', 'sales', 'merchandise', 'brand'],
            'consulting': ['consulting', 'advisory', 'strategy', 'management', 'business', 'expertise', 'professional'],
            'creative': ['design', 'creative', 'art', 'studio', 'agency', 'photography', 'media', 'marketing', 'advertising'],
            'education': ['school', 'education', 'learning', 'training', 'academy', 'course', 'university', 'teaching'],
            'other': ['company', 'business', 'service', 'professional', 'enterprise', 'organization', 'group']
        }
        
        # Style characteristics mapping
        self.style_keywords = {
            'modern': ['modern', 'contemporary', 'sleek', 'minimal', 'clean', 'simple', 'futuristic'],
            'classic': ['classic', 'traditional', 'elegant', 'timeless', 'sophisticated', 'premium', 'luxury'],
            'playful': ['fun', 'playful', 'friendly', 'colorful', 'creative', 'energetic', 'vibrant'],
            'bold': ['bold', 'strong', 'powerful', 'dynamic', 'confident', 'striking', 'impressive'],
            'minimalist': ['minimal', 'simple', 'clean', 'pure', 'basic', 'essential', 'streamlined'],
            'vintage': ['vintage', 'retro', 'classic', 'nostalgic', 'antique', 'heritage', 'historic']
        }
        
        # Color psychology mapping
        self.color_psychology = {
            'trust': [(0, 100, 200), (50, 150, 250)],      # Blues
            'energy': [(255, 100, 0), (255, 150, 50)],     # Oranges
            'nature': [(50, 150, 50), (100, 200, 100)],    # Greens
            'luxury': [(100, 50, 150), (150, 100, 200)],   # Purples
            'passion': [(200, 50, 50), (255, 100, 100)],   # Reds
            'stability': [(100, 70, 50), (150, 120, 80)],  # Browns
            'innovation': [(0, 200, 200), (50, 250, 250)], # Cyans
            'warmth': [(255, 200, 0), (255, 220, 50)]      # Yellows
        }
        
        # Industry color preferences
        self.industry_colors = {
            'tech': ['trust', 'innovation'],
            'healthcare': ['trust', 'nature', 'stability'],
            'finance': ['trust', 'stability', 'luxury'],
            'food': ['warmth', 'energy', 'nature'],
            'retail': ['energy', 'passion', 'warmth'],
            'consulting': ['trust', 'stability', 'luxury'],
            'creative': ['passion', 'energy', 'innovation'],
            'education': ['trust', 'nature', 'warmth'],
            'other': ['trust', 'stability']
        }

    def analyze_business(self, business_name: str, business_type: str, preferences: Dict) -> BusinessAnalysis:
        """Analyze business characteristics using rule-based AI."""
        try:
            # Extract keywords from business name and description
            keywords = self._extract_keywords(business_name, business_type, preferences.get('description', ''))
            
            # Determine industry based on keywords
            industry = self._classify_industry(keywords, business_type)
            
            # Calculate optimal complexity
            complexity = self._calculate_complexity(industry, preferences)
            
            # Determine style preferences
            style_preferences = self._analyze_style_preferences(keywords, industry, preferences)
            
            # Analyze target audience
            target_audience = self._analyze_target_audience(industry, preferences)
            
            # Determine brand personality
            brand_personality = self._analyze_brand_personality(keywords, style_preferences)
            
            # Generate color recommendations
            recommended_colors = self._generate_color_palette(industry, style_preferences)
            
            return BusinessAnalysis(
                industry=industry,
                keywords=keywords,
                complexity=complexity,
                style_preferences=style_preferences,
                target_audience=target_audience,
                brand_personality=brand_personality,
                recommended_colors=recommended_colors
            )
        except Exception as e:
            logger.error(f"Error in business analysis: {e}")
            # Return basic analysis as fallback
            return BusinessAnalysis(
                industry='other',
                keywords=[business_name.lower()],
                complexity=0.5,
                style_preferences=['modern'],
                target_audience='general',
                brand_personality=['professional'],
                recommended_colors=[(0, 100, 200), (100, 100, 100)]
            )

    def _extract_keywords(self, business_name: str, business_type: str, description: str) -> List[str]:
        """Extract meaningful keywords from business information."""
        text = f"{business_name} {business_type} {description}".lower()
        
        # Remove special characters and split
        words = re.findall(r'\b\w{3,}\b', text)
        
        # Filter out common words
        stopwords = {
            'the', 'and', 'for', 'are', 'with', 'they', 'this', 'that', 'from', 'have', 
            'company', 'business', 'service', 'services', 'inc', 'ltd', 'llc'
        }
        keywords = [word for word in words if word not in stopwords]
        
        # Return unique keywords, limited to top 10
        return list(dict.fromkeys(keywords))[:10]

    def _classify_industry(self, keywords: List[str], business_type: str) -> str:
        """Classify business industry based on keywords."""
        # Check business type first
        business_type_lower = business_type.lower()
        for industry, industry_keywords in self.industry_keywords.items():
            if any(keyword in business_type_lower for keyword in industry_keywords):
                return industry
        
        # Check extracted keywords
        industry_scores = {}
        for industry, industry_keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in industry_keywords)
            if score > 0:
                industry_scores[industry] = score
        
        # Return industry with highest score, default to 'other'
        return max(industry_scores.items(), key=lambda x: x[1])[0] if industry_scores else 'other'

    def _calculate_complexity(self, industry: str, preferences: Dict) -> float:
        """Calculate optimal logo complexity (0.0 = simple, 1.0 = complex)."""
        base_complexity = 0.5
        
        # Industry-based adjustments
        industry_complexity = {
            'tech': 0.3,        # Clean and simple
            'finance': 0.4,     # Professional, not too complex
            'healthcare': 0.5,  # Balanced
            'consulting': 0.3,  # Minimal and professional
            'creative': 0.7,    # More artistic freedom
            'food': 0.6,        # Can be more playful
            'retail': 0.6,      # Engaging but not overwhelming
            'education': 0.5,   # Balanced and approachable
            'other': 0.5
        }
        
        complexity = industry_complexity.get(industry, base_complexity)
        
        # Adjust based on preferences
        style = preferences.get('style', 'modern')
        if style in ['minimalist', 'modern']:
            complexity *= 0.7
        elif style in ['vintage', 'classic']:
            complexity *= 1.2
        elif style in ['playful', 'creative']:
            complexity *= 1.3
        
        return max(0.2, min(0.9, complexity))

    def _analyze_style_preferences(self, keywords: List[str], industry: str, preferences: Dict) -> List[str]:
        """Analyze preferred design styles."""
        styles = []
        
        # Check explicit style preference
        explicit_style = preferences.get('style')
        if explicit_style and explicit_style in self.style_keywords:
            styles.append(explicit_style)
        
        # Analyze keywords for style indicators
        for style, style_keywords in self.style_keywords.items():
            if any(keyword in style_keywords for keyword in keywords):
                if style not in styles:
                    styles.append(style)
        
        # Industry default styles
        industry_defaults = {
            'tech': ['modern', 'minimalist'],
            'finance': ['classic', 'modern'],
            'healthcare': ['modern', 'classic'],
            'food': ['playful', 'vintage'],
            'retail': ['bold', 'modern'],
            'consulting': ['classic', 'modern'],
            'creative': ['playful', 'bold'],
            'education': ['friendly', 'modern'],
            'other': ['modern']
        }
        
        # Add industry defaults if no styles detected
        if not styles:
            styles = industry_defaults.get(industry, ['modern'])
        
        return styles[:3]  # Limit to top 3 styles

    def _analyze_target_audience(self, industry: str, preferences: Dict) -> str:
        """Analyze target audience characteristics."""
        # Check for explicit target audience in preferences
        if 'target_audience' in preferences:
            return preferences['target_audience']
        
        # Industry-based audience mapping
        audience_mapping = {
            'tech': 'professionals_and_businesses',
            'finance': 'professionals_and_investors',
            'healthcare': 'patients_and_families',
            'food': 'food_lovers_and_families',
            'retail': 'consumers_and_shoppers',
            'consulting': 'business_executives',
            'creative': 'creative_professionals',
            'education': 'students_and_educators',
            'other': 'general_public'
        }
        
        return audience_mapping.get(industry, 'general_public')

    def _analyze_brand_personality(self, keywords: List[str], style_preferences: List[str]) -> List[str]:
        """Determine brand personality traits."""
        personality_traits = []
        
        # Map styles to personality traits
        style_personality = {
            'modern': ['innovative', 'efficient'],
            'classic': ['trustworthy', 'established'],
            'playful': ['friendly', 'approachable'],
            'bold': ['confident', 'dynamic'],
            'minimalist': ['clean', 'focused'],
            'vintage': ['authentic', 'experienced']
        }
        
        for style in style_preferences:
            traits = style_personality.get(style, [])
            personality_traits.extend(traits)
        
        # Remove duplicates and limit
        return list(dict.fromkeys(personality_traits))[:4]

    def _generate_color_palette(self, industry: str, style_preferences: List[str]) -> List[Tuple[int, int, int]]:
        """Generate AI-recommended color palette."""
        colors = []
        
        # Get industry-preferred color emotions
        color_emotions = self.industry_colors.get(industry, ['trust', 'stability'])
        
        # Generate colors based on emotions
        for emotion in color_emotions[:2]:  # Primary and secondary colors
            emotion_colors = self.color_psychology.get(emotion, [(100, 100, 100)])
            colors.extend(emotion_colors[:1])  # One color per emotion
        
        # Add complementary colors based on style
        if 'playful' in style_preferences:
            colors.append((255, 200, 50))  # Bright yellow
        elif 'classic' in style_preferences:
            colors.append((50, 50, 50))    # Dark gray
        elif 'modern' in style_preferences:
            colors.append((200, 200, 200)) # Light gray
        
        # Ensure we have at least 2 colors
        while len(colors) < 2:
            colors.append((100, 100, 100))  # Default gray
        
        return colors[:4]  # Maximum 4 colors

    def generate_ai_palettes(self, analysis: BusinessAnalysis) -> List[Dict]:
        """Generate multiple AI-optimized color palettes."""
        palettes = []
        
        try:
            # Primary palette from analysis
            primary_palette = {
                'name': f'{analysis.industry.title()} Professional',
                'colors': [self._rgb_to_hex(color) for color in analysis.recommended_colors[:3]],
                'reasoning': f'Optimized for {analysis.industry} industry with {", ".join(analysis.style_preferences)} style'
            }
            palettes.append(primary_palette)
            
            # Alternative palette - warmer tones
            warm_colors = [(200, 100, 50), (255, 150, 100), (100, 150, 200)]
            warm_palette = {
                'name': 'Warm & Approachable',
                'colors': [self._rgb_to_hex(color) for color in warm_colors],
                'reasoning': 'Warm colors for friendly brand personality'
            }
            palettes.append(warm_palette)
            
            # Alternative palette - cool tones
            cool_colors = [(50, 150, 200), (100, 200, 150), (150, 100, 200)]
            cool_palette = {
                'name': 'Cool & Professional',
                'colors': [self._rgb_to_hex(color) for color in cool_colors],
                'reasoning': 'Cool colors for professional and trustworthy appearance'
            }
            palettes.append(cool_palette)
            
            # Monochromatic palette
            base_color = analysis.recommended_colors[0] if analysis.recommended_colors else (100, 150, 200)
            mono_colors = self._generate_monochromatic_palette(base_color)
            mono_palette = {
                'name': 'Monochromatic Elegance',
                'colors': [self._rgb_to_hex(color) for color in mono_colors],
                'reasoning': 'Sophisticated single-hue palette with tonal variations'
            }
            palettes.append(mono_palette)
            
        except Exception as e:
            logger.error(f"Error generating palettes: {e}")
            # Fallback palette
            fallback_palette = {
                'name': 'Classic Blue',
                'colors': ['#0066CC', '#4D9EE8', '#B3D9FF'],
                'reasoning': 'Reliable and professional color scheme'
            }
            palettes.append(fallback_palette)
        
        return palettes

    def _generate_monochromatic_palette(self, base_rgb: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Generate monochromatic color variations."""
        r, g, b = base_rgb
        h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        
        variations = []
        # Create lighter and darker versions
        for v_factor in [0.8, 1.0, 1.2]:  # Darker, original, lighter
            new_v = max(0.0, min(1.0, v * v_factor))
            new_r, new_g, new_b = colorsys.hsv_to_rgb(h, s, new_v)
            variations.append((int(new_r * 255), int(new_g * 255), int(new_b * 255)))
        
        return variations

    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color."""
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"


# Global instance
logo_ai = LogoAI()
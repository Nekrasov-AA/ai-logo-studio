"""
Hybrid AI Logo System - LLM Analysis + Programmatic SVG Generation
Uses Claude/OpenAI for creative analysis and concept generation
"""

import json
import random
import hashlib
from typing import Dict, List, Optional, Tuple
import os
import asyncio

# Try to import OpenAI client (if available)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[HybridAI] OpenAI not available, using fallback")

class HybridLogoAI:
    """Advanced AI system combining LLM analysis with programmatic generation."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_llm = OPENAI_AVAILABLE and self.openai_api_key
        
        if self.use_llm:
            try:
                import openai
                # Use simple initialization without extra parameters
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                print("[HybridAI] ✅ LLM integration active")
            except Exception as e:
                print(f"[HybridAI] ⚠️ LLM init failed: {e}")
                self.use_llm = False
                self.client = None
        else:
            print("[HybridAI] 📝 Using enhanced rule-based analysis")
        
        # Visual concept database for programmatic generation
        self.concept_database = {
            'tech': {
                'symbols': ['neural_network', 'circuit_board', 'data_flow', 'digital_matrix', 'quantum_grid'],
                'shapes': ['hexagonal', 'geometric_nodes', 'interconnected', 'layered_circuits', 'holographic'],
                'color_moods': ['electric_blue', 'cyber_purple', 'digital_green', 'future_silver', 'neon_accents']
            },
            'healthcare': {
                'symbols': ['healing_hands', 'life_cross', 'heartbeat_wave', 'protective_shield', 'care_embrace'],
                'shapes': ['organic_curves', 'protective_circles', 'flowing_forms', 'balanced_symmetry', 'gentle_arcs'],
                'color_moods': ['trust_blue', 'nature_green', 'calm_teal', 'warm_coral', 'pure_white']
            },
            'finance': {
                'symbols': ['growth_arrow', 'stability_foundation', 'wealth_crown', 'secure_vault', 'golden_ratio'],
                'shapes': ['diamond_precision', 'ascending_bars', 'solid_foundations', 'premium_geometry', 'elegant_curves'],
                'color_moods': ['luxury_gold', 'trust_navy', 'premium_silver', 'royal_purple', 'success_green']
            },
            'creative': {
                'symbols': ['artistic_burst', 'creative_spark', 'imagination_swirl', 'design_palette', 'inspiration_ray'],
                'shapes': ['dynamic_splash', 'organic_flow', 'expressive_curves', 'vibrant_explosion', 'artistic_chaos'],
                'color_moods': ['vibrant_rainbow', 'artistic_spectrum', 'creative_energy', 'passionate_reds', 'inspiring_yellows']
            },
            'food': {
                'symbols': ['culinary_flame', 'organic_leaf', 'chef_artistry', 'harvest_abundance', 'taste_celebration'],
                'shapes': ['organic_natural', 'appetizing_curves', 'warming_circles', 'rustic_charm', 'fresh_vitality'],
                'color_moods': ['appetizing_orange', 'fresh_green', 'warm_brown', 'golden_harvest', 'spice_red']
            }
        }

    async def analyze_brand_with_ai(self, business_name: str, business_type: str, description: str) -> Dict:
        """Use LLM to deeply analyze brand and generate creative concepts."""
        
        if self.use_llm:
            return await self._llm_brand_analysis(business_name, business_type, description)
        else:
            return self._enhanced_rule_analysis(business_name, business_type, description)

    async def _llm_brand_analysis(self, business_name: str, business_type: str, description: str) -> Dict:
        """Advanced LLM-powered brand analysis."""
        
        prompt = f"""
You are a world-class brand strategist and logo designer. Analyze this business and create a comprehensive design brief:

Business Name: {business_name}
Business Type: {business_type}
Description: {description}

Provide a JSON response with:

1. "industry_classification": specific industry (tech, healthcare, finance, creative, food, retail, consulting, education, other)

2. "brand_personality": 3-5 key personality traits (innovative, trustworthy, premium, playful, professional, etc.)

3. "visual_metaphors": 3-4 symbolic concepts that could represent this brand visually

4. "design_direction": specific visual style recommendations

5. "color_psychology": recommended color emotions with reasoning

6. "uniqueness_factors": what makes this brand special/different

7. "target_perception": how the brand should be perceived

8. "logo_concepts": 3 specific logo concept ideas with detailed descriptions

Respond ONLY with valid JSON, no other text.
        """

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                analysis = json.loads(analysis_text)
                print(f"[HybridAI] 🧠 LLM analysis successful for {business_name}")
                return analysis
            except json.JSONDecodeError:
                print(f"[HybridAI] ⚠️ JSON parse error, using fallback")
                return self._enhanced_rule_analysis(business_name, business_type, description)
                
        except Exception as e:
            print(f"[HybridAI] ❌ LLM error: {e}")
            return self._enhanced_rule_analysis(business_name, business_type, description)

    def _enhanced_rule_analysis(self, business_name: str, business_type: str, description: str) -> Dict:
        """Enhanced rule-based analysis as fallback."""
        
        # Analyze industry
        text = f"{business_name} {business_type} {description}".lower()
        
        industry_keywords = {
            'tech': ['tech', 'software', 'ai', 'digital', 'data', 'innovation', 'platform', 'solution', 'system', 'neural', 'machine', 'algorithm'],
            'healthcare': ['health', 'medical', 'care', 'hospital', 'clinic', 'wellness', 'therapy', 'medicine', 'doctor', 'patient'],
            'finance': ['finance', 'investment', 'bank', 'financial', 'money', 'capital', 'wealth', 'trading', 'insurance'],
            'creative': ['creative', 'design', 'art', 'studio', 'agency', 'media', 'brand', 'advertising', 'marketing'],
            'food': ['food', 'restaurant', 'kitchen', 'cooking', 'chef', 'culinary', 'dining', 'cafe', 'bakery', 'cuisine']
        }
        
        # Determine industry
        industry_scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                industry_scores[industry] = score
        
        industry = max(industry_scores.items(), key=lambda x: x[1])[0] if industry_scores else 'other'
        
        # Generate comprehensive analysis
        analysis = {
            "industry_classification": industry,
            "brand_personality": self._determine_personality(text, industry),
            "visual_metaphors": self._generate_metaphors(business_name, business_type, industry),
            "design_direction": self._suggest_design_direction(industry, text),
            "color_psychology": self._advanced_color_analysis(industry, text),
            "uniqueness_factors": self._find_unique_elements(business_name, business_type),
            "target_perception": self._determine_perception(industry, business_name),
            "logo_concepts": self._generate_concepts(business_name, industry, text)
        }
        
        print(f"[HybridAI] 📊 Enhanced rule analysis complete for {business_name}")
        return analysis

    def _determine_personality(self, text: str, industry: str) -> List[str]:
        """Determine brand personality traits."""
        
        personality_indicators = {
            'innovative': ['innovation', 'cutting-edge', 'advanced', 'future', 'next-gen'],
            'trustworthy': ['trust', 'reliable', 'secure', 'professional', 'established'],
            'premium': ['premium', 'luxury', 'excellence', 'elite', 'exclusive'],
            'playful': ['fun', 'creative', 'vibrant', 'energetic', 'dynamic'],
            'caring': ['care', 'support', 'help', 'compassionate', 'nurturing'],
            'bold': ['bold', 'powerful', 'strong', 'confident', 'impactful'],
            'elegant': ['elegant', 'sophisticated', 'refined', 'graceful', 'stylish']
        }
        
        # Industry defaults
        industry_personalities = {
            'tech': ['innovative', 'trustworthy', 'bold'],
            'healthcare': ['trustworthy', 'caring', 'professional'],
            'finance': ['trustworthy', 'premium', 'professional'],
            'creative': ['playful', 'innovative', 'bold'],
            'food': ['caring', 'premium', 'warm']
        }
        
        traits = []
        
        # Check for indicators in text
        for trait, indicators in personality_indicators.items():
            if any(indicator in text for indicator in indicators):
                traits.append(trait)
        
        # Add industry defaults if not enough found
        if len(traits) < 3:
            defaults = industry_personalities.get(industry, ['professional', 'trustworthy'])
            for trait in defaults:
                if trait not in traits:
                    traits.append(trait)
                    if len(traits) >= 4:
                        break
        
        return traits[:4]

    def _generate_metaphors(self, business_name: str, business_type: str, industry: str) -> List[str]:
        """Generate visual metaphors for the brand."""
        
        metaphor_database = {
            'tech': ['interconnected networks', 'digital transformation', 'data streams', 'neural pathways'],
            'healthcare': ['healing hands', 'protective shield', 'life energy', 'caring embrace'],
            'finance': ['growth trajectory', 'solid foundation', 'golden opportunity', 'secure vault'],
            'creative': ['burst of inspiration', 'artistic palette', 'creative spark', 'imagination flow'],
            'food': ['harvest abundance', 'culinary artistry', 'taste journey', 'nourishing warmth']
        }
        
        base_metaphors = metaphor_database.get(industry, ['professional symbol', 'brand identity', 'business growth'])
        
        # Add name-specific metaphors
        name_words = business_name.lower().split()
        custom_metaphors = []
        
        for word in name_words:
            if 'flow' in word:
                custom_metaphors.append('dynamic flow')
            elif 'star' in word:
                custom_metaphors.append('guiding star')
            elif 'green' in word:
                custom_metaphors.append('sustainable growth')
            elif 'gold' in word:
                custom_metaphors.append('premium excellence')
        
        return (custom_metaphors + base_metaphors)[:4]

    def _suggest_design_direction(self, industry: str, text: str) -> str:
        """Suggest specific design direction."""
        
        directions = {
            'tech': "Modern geometric design with interconnected elements suggesting innovation and connectivity",
            'healthcare': "Organic, flowing design with protective and caring elements, emphasizing trust and wellness", 
            'finance': "Premium, stable design with upward movement suggesting growth and reliability",
            'creative': "Dynamic, expressive design with artistic elements showing creativity and inspiration",
            'food': "Organic, appetizing design with natural elements suggesting freshness and quality"
        }
        
        base_direction = directions.get(industry, "Clean, professional design with balanced proportions")
        
        # Modify based on text content
        if 'luxury' in text or 'premium' in text:
            base_direction += " with luxury finishing touches"
        elif 'modern' in text or 'contemporary' in text:
            base_direction += " with contemporary minimalist elements"
        elif 'traditional' in text or 'classic' in text:
            base_direction += " with timeless, classic styling"
        
        return base_direction

    def _advanced_color_analysis(self, industry: str, text: str) -> Dict:
        """Advanced color psychology analysis."""
        
        industry_colors = {
            'tech': {
                'primary': 'electric_blue',
                'reasoning': 'Conveys innovation, trust, and digital sophistication',
                'palette': ['#0066FF', '#00CCFF', '#4A90E2']
            },
            'healthcare': {
                'primary': 'healing_green', 
                'reasoning': 'Represents health, growth, and natural healing',
                'palette': ['#2E8B57', '#20B2AA', '#66CDAA']
            },
            'finance': {
                'primary': 'trust_navy',
                'reasoning': 'Establishes trust, stability, and professional authority', 
                'palette': ['#1B365D', '#2E5D8B', '#4682B4']
            },
            'creative': {
                'primary': 'vibrant_spectrum',
                'reasoning': 'Expresses creativity, energy, and artistic passion',
                'palette': ['#FF6B35', '#F7931E', '#FFD23F']
            },
            'food': {
                'primary': 'appetizing_warmth',
                'reasoning': 'Stimulates appetite and conveys warmth and comfort',
                'palette': ['#FF8C42', '#FFA726', '#8BC34A']
            }
        }
        
        return industry_colors.get(industry, {
            'primary': 'professional_blue',
            'reasoning': 'Conveys professionalism and trustworthiness',
            'palette': ['#2C3E50', '#3498DB', '#95A5A6']
        })

    def _find_unique_elements(self, business_name: str, business_type: str) -> List[str]:
        """Identify unique elements of the brand."""
        
        unique_elements = []
        
        # Analyze business name
        name_lower = business_name.lower()
        if any(word in name_lower for word in ['flow', 'stream', 'wave']):
            unique_elements.append("Dynamic flow imagery")
        if any(word in name_lower for word in ['green', 'eco', 'sustain']):
            unique_elements.append("Environmental consciousness")  
        if any(word in name_lower for word in ['gold', 'premium', 'elite']):
            unique_elements.append("Premium positioning")
        if any(word in name_lower for word in ['smart', 'ai', 'neural']):
            unique_elements.append("AI/Intelligence focus")
        
        # Default unique elements
        if not unique_elements:
            unique_elements = [
                "Distinctive brand identity",
                "Professional market presence", 
                "Customer-focused approach"
            ]
        
        return unique_elements[:3]

    def _determine_perception(self, industry: str, business_name: str) -> str:
        """Determine target brand perception."""
        
        perceptions = {
            'tech': "Cutting-edge technology leader and innovation partner",
            'healthcare': "Trusted healthcare provider focused on patient wellbeing",
            'finance': "Reliable financial partner for growth and prosperity", 
            'creative': "Inspiring creative partner bringing visions to life",
            'food': "Quality culinary destination creating memorable experiences"
        }
        
        base_perception = perceptions.get(industry, "Professional service provider delivering excellence")
        
        # Customize based on name
        if 'studio' in business_name.lower():
            base_perception = base_perception.replace('provider', 'studio')
        elif 'solutions' in business_name.lower():
            base_perception = base_perception.replace('provider', 'solutions partner')
            
        return base_perception

    def _generate_concepts(self, business_name: str, industry: str, text: str) -> List[Dict]:
        """Generate specific logo concept ideas."""
        
        concepts = []
        
        # Get industry-specific concepts
        if industry in self.concept_database:
            db = self.concept_database[industry]
            
            for i in range(3):
                concept = {
                    "concept_name": f"{business_name} {['Primary', 'Alternative', 'Creative'][i]} Concept",
                    "visual_description": f"Features {random.choice(db['symbols'])} with {random.choice(db['shapes'])} styling and {random.choice(db['color_moods'])} color scheme",
                    "symbolism": f"Represents {random.choice(['innovation', 'trust', 'growth', 'excellence', 'connection'])} and {random.choice(['reliability', 'creativity', 'professionalism', 'care', 'strength'])}",
                    "layout": random.choice(['emblem', 'horizontal', 'stacked', 'icon-text'])
                }
                concepts.append(concept)
        
        return concepts


# Global instance
hybrid_ai = HybridLogoAI()
"""
Advanced Prompt Engineering for AI Logo Generation
Sophisticated prompt creation and optimization system
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .base_provider import LogoGenerationRequest, GenerationStyle

logger = logging.getLogger(__name__)


class PromptOptimizationLevel(Enum):
    """Prompt optimization levels."""
    BASIC = "basic"
    ADVANCED = "advanced"
    PREMIUM = "premium"


@dataclass
class IndustryProfile:
    """Industry-specific design profile."""
    keywords: List[str]
    visual_metaphors: List[str]
    color_psychology: Dict[str, str]
    typography_style: str
    design_principles: List[str]
    avoid_elements: List[str] = field(default_factory=list)
    

@dataclass
class StyleProfile:
    """Style-specific design profile."""
    visual_characteristics: List[str]
    composition_rules: List[str]
    color_treatment: str
    typography_weight: str
    element_density: str
    negative_prompts: List[str] = field(default_factory=list)


@dataclass 
class PromptComponents:
    """Structured components of a generated prompt."""
    base_description: str
    industry_context: str
    style_modifiers: List[str]
    visual_elements: List[str]
    color_specifications: List[str]
    composition_rules: List[str]
    quality_requirements: List[str]
    technical_specifications: List[str]
    negative_prompts: List[str] = field(default_factory=list)
    
    def to_prompt(self, max_length: int = 1000) -> str:
        """Convert components to final prompt string."""
        
        # Combine all positive elements
        positive_parts = [
            self.base_description,
            self.industry_context,
            ", ".join(self.style_modifiers),
            ", ".join(self.visual_elements),
            ", ".join(self.color_specifications),
            ", ".join(self.composition_rules),
            ", ".join(self.quality_requirements),
            ", ".join(self.technical_specifications)
        ]
        
        prompt = ", ".join(filter(None, positive_parts))
        
        # Truncate if too long
        if len(prompt) > max_length:
            prompt = prompt[:max_length].rsplit(',', 1)[0]
        
        return prompt.strip()
    
    def get_negative_prompt(self) -> str:
        """Get negative prompt string."""
        return ", ".join(self.negative_prompts)


class PromptEngineer:
    """Advanced prompt engineering system for logo generation."""
    
    def __init__(self):
        """Initialize prompt engineering system."""
        
        # Industry profiles with comprehensive design guidance
        self.industry_profiles = {
            "technology": IndustryProfile(
                keywords=["innovation", "digital", "connectivity", "data", "network", "AI", "automation"],
                visual_metaphors=["neural networks", "circuit patterns", "data flow", "quantum dots", "binary code aesthetics"],
                color_psychology={
                    "primary": "electric blue, cyber purple, digital green",
                    "secondary": "silver, white, neon accents",
                    "avoid": "earth tones, organic colors, muted pastels"
                },
                typography_style="geometric sans-serif, futuristic, clean lines",
                design_principles=["minimalism", "geometric precision", "high contrast", "scalable vectors"],
                avoid_elements=["organic shapes", "hand-drawn elements", "vintage textures"]
            ),
            
            "healthcare": IndustryProfile(
                keywords=["care", "wellness", "healing", "life", "protection", "trust", "medical"],
                visual_metaphors=["healing hands", "protective shield", "life tree", "heartbeat rhythm", "caring embrace"],
                color_psychology={
                    "primary": "medical blue, healing green, trust navy",
                    "secondary": "pure white, soft gray, warm coral",
                    "avoid": "aggressive reds, dark colors, neon colors"
                },
                typography_style="trustworthy serif, clean sans-serif, professional",
                design_principles=["trustworthiness", "accessibility", "calming presence", "professional authority"],
                avoid_elements=["aggressive shapes", "dark imagery", "complex patterns"]
            ),
            
            "finance": IndustryProfile(
                keywords=["growth", "stability", "prosperity", "security", "investment", "wealth", "trust"],
                visual_metaphors=["upward arrow", "solid foundation", "golden ratio", "growth charts", "stability pillars"],
                color_psychology={
                    "primary": "trust blue, prosperity green, premium gold",
                    "secondary": "charcoal gray, silver, deep navy",
                    "avoid": "bright neon, childish colors, unstable hues"
                },
                typography_style="authoritative serif, professional sans-serif, premium weight",
                design_principles=["authority", "stability", "premium quality", "timeless design"],
                avoid_elements=["playful elements", "casual styling", "trendy effects"]
            ),
            
            "food": IndustryProfile(
                keywords=["fresh", "organic", "quality", "taste", "nourishment", "culinary", "artisan"],
                visual_metaphors=["harvest abundance", "chef's artistry", "fresh ingredients", "culinary flame", "taste celebration"],
                color_psychology={
                    "primary": "appetizing orange, fresh green, warm brown",
                    "secondary": "golden yellow, cream, rustic red",
                    "avoid": "artificial colors, cold blues, medical whites"
                },
                typography_style="warm serif, handcrafted sans-serif, organic curves",
                design_principles=["appetite appeal", "organic feel", "warmth", "quality craftsmanship"],
                avoid_elements=["sterile design", "cold imagery", "industrial elements"]
            ),
            
            "creative": IndustryProfile(
                keywords=["inspiration", "imagination", "artistic", "innovative", "expression", "vision", "creativity"],
                visual_metaphors=["burst of inspiration", "artistic palette", "creative spark", "imagination flow", "vision lens"],
                color_psychology={
                    "primary": "vibrant spectrum, artistic purple, creative orange",
                    "secondary": "energetic yellow, passionate red, inspiring blue",
                    "avoid": "corporate gray, conservative colors, muted tones"
                },
                typography_style="expressive display, artistic script, creative sans-serif",
                design_principles=["creative expression", "visual impact", "artistic flair", "unique personality"],
                avoid_elements=["conservative design", "corporate styling", "generic elements"]
            ),
            
            "retail": IndustryProfile(
                keywords=["lifestyle", "fashion", "quality", "brand", "shopping", "consumer", "trend"],
                visual_metaphors=["shopping experience", "lifestyle enhancement", "brand identity", "consumer choice", "retail therapy"],
                color_psychology={
                    "primary": "brand pink, shopping blue, lifestyle purple",
                    "secondary": "trendy coral, modern mint, classic black",
                    "avoid": "industrial colors, medical tones, corporate gray"
                },
                typography_style="trendy sans-serif, fashion-forward, lifestyle casual",
                design_principles=["brand recognition", "consumer appeal", "trendy aesthetics", "lifestyle integration"],
                avoid_elements=["industrial design", "medical imagery", "corporate formality"]
            ),
            
            "education": IndustryProfile(
                keywords=["learning", "knowledge", "growth", "development", "wisdom", "academic", "enlightenment"],
                visual_metaphors=["tree of knowledge", "learning pathway", "academic achievement", "wisdom light", "growth journey"],
                color_psychology={
                    "primary": "academic blue, knowledge green, wisdom purple",
                    "secondary": "scholarly brown, learning orange, achievement gold",
                    "avoid": "childish colors, commercial tones, aggressive reds"
                },
                typography_style="academic serif, scholarly sans-serif, educational clarity",
                design_principles=["educational clarity", "intellectual appeal", "academic authority", "learning accessibility"],
                avoid_elements=["commercial imagery", "aggressive design", "childish elements"]
            ),
            
            "consulting": IndustryProfile(
                keywords=["expertise", "strategy", "solutions", "professional", "advisory", "guidance", "excellence"],
                visual_metaphors=["strategic compass", "solution framework", "expert guidance", "professional excellence", "advisory wisdom"],
                color_psychology={
                    "primary": "professional blue, expert gray, strategic navy",
                    "secondary": "consultant silver, advisory white, excellence gold",
                    "avoid": "casual colors, playful tones, unprofessional hues"
                },
                typography_style="professional serif, authoritative sans-serif, executive weight",
                design_principles=["professional authority", "strategic clarity", "expert positioning", "solution focus"],
                avoid_elements=["casual design", "playful elements", "unprofessional styling"]
            )
        }
        
        # Style profiles with detailed characteristics
        self.style_profiles = {
            GenerationStyle.MINIMALIST: StyleProfile(
                visual_characteristics=["clean lines", "negative space", "geometric simplicity", "essential elements only"],
                composition_rules=["asymmetric balance", "generous white space", "single focal point", "reduced color palette"],
                color_treatment="monochromatic or duotone, high contrast",
                typography_weight="light to medium, geometric sans-serif",
                element_density="sparse, breathing room between elements",
                negative_prompts=["cluttered", "ornate", "decorative", "busy", "complex details"]
            ),
            
            GenerationStyle.MODERN: StyleProfile(
                visual_characteristics=["contemporary design", "sleek aesthetics", "gradient effects", "sophisticated styling"],
                composition_rules=["dynamic balance", "layered hierarchy", "modern proportions", "tech-inspired layout"],
                color_treatment="gradient overlays, modern color schemes, digital aesthetics",
                typography_weight="medium to bold, contemporary sans-serif",
                element_density="balanced, structured spacing",
                negative_prompts=["vintage", "retro", "outdated", "traditional", "old-fashioned"]
            ),
            
            GenerationStyle.CLASSIC: StyleProfile(
                visual_characteristics=["timeless elegance", "traditional proportions", "refined details", "established aesthetics"],
                composition_rules=["symmetric balance", "classical proportions", "hierarchical structure", "traditional layout"],
                color_treatment="classic color combinations, sophisticated palettes, traditional harmony",
                typography_weight="medium, serif or classic sans-serif",
                element_density="well-structured, traditional spacing",
                negative_prompts=["trendy", "flashy", "experimental", "unconventional", "modern tech"]
            ),
            
            GenerationStyle.PLAYFUL: StyleProfile(
                visual_characteristics=["dynamic energy", "fun elements", "vibrant colors", "creative shapes"],
                composition_rules=["asymmetric energy", "playful balance", "dynamic movement", "creative arrangement"],
                color_treatment="bright colors, energetic combinations, fun palettes",
                typography_weight="varied weights, expressive fonts, creative typography",
                element_density="energetic, varied spacing for dynamic feel",
                negative_prompts=["serious", "corporate", "formal", "conservative", "restrained"]
            ),
            
            GenerationStyle.BOLD: StyleProfile(
                visual_characteristics=["strong presence", "impactful design", "confident styling", "powerful aesthetics"],
                composition_rules=["dominant focal point", "strong hierarchy", "commanding presence", "impactful layout"],
                color_treatment="high contrast, bold color choices, striking combinations",
                typography_weight="bold to heavy, impactful fonts",
                element_density="focused, strong visual weight",
                negative_prompts=["subtle", "delicate", "weak", "timid", "understated"]
            ),
            
            GenerationStyle.ELEGANT: StyleProfile(
                visual_characteristics=["sophisticated refinement", "luxury aesthetics", "graceful design", "premium quality"],
                composition_rules=["refined balance", "elegant proportions", "sophisticated hierarchy", "luxury layout"],
                color_treatment="sophisticated palettes, luxury colors, refined combinations",
                typography_weight="refined, premium serif or elegant sans-serif",
                element_density="spacious, luxury breathing room",
                negative_prompts=["cheap", "casual", "rough", "unrefined", "basic"]
            ),
            
            GenerationStyle.TECH: StyleProfile(
                visual_characteristics=["digital aesthetics", "futuristic design", "high-tech styling", "innovation focus"],
                composition_rules=["grid-based layout", "digital hierarchy", "tech-inspired balance", "systematic arrangement"],
                color_treatment="digital color schemes, neon accents, tech palettes",
                typography_weight="geometric, tech-inspired fonts, digital styling",
                element_density="systematic, grid-based spacing",
                negative_prompts=["organic", "natural", "hand-drawn", "rustic", "traditional"]
            ),
            
            GenerationStyle.ORGANIC: StyleProfile(
                visual_characteristics=["natural forms", "flowing shapes", "eco-friendly design", "sustainable aesthetics"],
                composition_rules=["natural balance", "organic flow", "environmental harmony", "sustainable layout"],
                color_treatment="earth tones, natural palettes, eco-friendly colors",
                typography_weight="natural, organic fonts, sustainable styling",
                element_density="natural spacing, organic breathing room",
                negative_prompts=["artificial", "synthetic", "industrial", "mechanical", "digital"]
            )
        }
        
        # Common negative prompts to avoid in logo design
        self.universal_negative_prompts = [
            "blurry", "low quality", "pixelated", "distorted", "watermark", 
            "text artifacts", "messy", "amateur", "unprofessional",
            "photorealistic", "3d render", "realistic lighting", "shadows",
            "cluttered background", "noisy", "grainy", "compressed"
        ]
    
    def create_advanced_prompt(self, request: LogoGenerationRequest, 
                             optimization_level: PromptOptimizationLevel = PromptOptimizationLevel.ADVANCED) -> PromptComponents:
        """Create advanced, optimized prompt for logo generation."""
        
        # Get industry profile
        industry_profile = self.industry_profiles.get(
            request.industry.lower(),
            self._create_generic_industry_profile(request.industry)
        )
        
        # Get style profile
        style_profile = self.style_profiles.get(
            request.style,
            self.style_profiles[GenerationStyle.MODERN]
        )
        
        # Build prompt components
        components = PromptComponents(
            base_description=self._create_base_description(request),
            industry_context=self._create_industry_context(request, industry_profile),
            style_modifiers=self._create_style_modifiers(request, style_profile),
            visual_elements=self._create_visual_elements(request, industry_profile, style_profile),
            color_specifications=self._create_color_specifications(request, industry_profile),
            composition_rules=self._create_composition_rules(request, style_profile),
            quality_requirements=self._create_quality_requirements(optimization_level),
            technical_specifications=self._create_technical_specifications(request),
            negative_prompts=self._create_negative_prompts(industry_profile, style_profile)
        )
        
        return components
    
    def _create_base_description(self, request: LogoGenerationRequest) -> str:
        """Create base description for the logo."""
        
        base_parts = [
            "professional logo design",
            f"for '{request.business_name}'",
            f"a {request.business_type} business"
        ]
        
        if request.description:
            # Clean and integrate business description
            cleaned_desc = re.sub(r'[^\w\s-]', '', request.description)
            if len(cleaned_desc.strip()) > 0:
                base_parts.append(f"specializing in {cleaned_desc}")
        
        return ", ".join(base_parts)
    
    def _create_industry_context(self, request: LogoGenerationRequest, 
                               industry_profile: IndustryProfile) -> str:
        """Create industry-specific context."""
        
        context_parts = []
        
        # Add key industry keywords
        if industry_profile.keywords:
            context_parts.append(f"embodying {', '.join(industry_profile.keywords[:3])}")
        
        # Add visual metaphors
        if industry_profile.visual_metaphors:
            primary_metaphor = industry_profile.visual_metaphors[0]
            context_parts.append(f"inspired by {primary_metaphor}")
        
        # Add design principles
        if industry_profile.design_principles:
            context_parts.append(f"following {', '.join(industry_profile.design_principles[:2])} principles")
        
        return ", ".join(context_parts)
    
    def _create_style_modifiers(self, request: LogoGenerationRequest, 
                              style_profile: StyleProfile) -> List[str]:
        """Create style-specific modifiers."""
        
        modifiers = []
        
        # Add visual characteristics
        modifiers.extend(style_profile.visual_characteristics[:3])
        
        # Add typography guidance
        modifiers.append(style_profile.typography_weight)
        
        # Add element density guidance  
        modifiers.append(style_profile.element_density)
        
        # Brand personality integration
        if request.brand_personality:
            personality_modifiers = {
                "innovative": "cutting-edge design",
                "trustworthy": "reliable visual foundation",
                "premium": "luxury finishing touches",
                "playful": "dynamic energy",
                "professional": "business-appropriate styling",
                "caring": "warm, approachable design",
                "bold": "strong visual impact"
            }
            
            for trait in request.brand_personality[:2]:  # Limit to 2 traits
                if trait in personality_modifiers:
                    modifiers.append(personality_modifiers[trait])
        
        return modifiers
    
    def _create_visual_elements(self, request: LogoGenerationRequest, 
                              industry_profile: IndustryProfile,
                              style_profile: StyleProfile) -> List[str]:
        """Create visual element specifications."""
        
        elements = []
        
        # Layout-specific elements
        layout_elements = {
            "horizontal": "horizontal layout with symbol beside text",
            "vertical": "stacked vertical layout with symbol above text",
            "icon_only": "symbolic icon without text",
            "balanced": "harmoniously balanced composition"
        }
        
        layout_element = layout_elements.get(request.preferred_layout, "balanced composition")
        elements.append(layout_element)
        
        # Text inclusion guidance
        if request.include_text and request.preferred_layout != "icon_only":
            elements.append(f"incorporating text '{request.business_name}'")
            elements.append("readable typography integration")
        else:
            elements.append("symbolic design without text")
            elements.append("recognizable icon representation")
        
        # Industry-specific visual elements
        if industry_profile.visual_metaphors:
            secondary_metaphor = industry_profile.visual_metaphors[1] if len(industry_profile.visual_metaphors) > 1 else industry_profile.visual_metaphors[0]
            elements.append(f"subtle {secondary_metaphor} influence")
        
        # Style-specific composition
        if style_profile.composition_rules:
            elements.append(style_profile.composition_rules[0])
        
        return elements
    
    def _create_color_specifications(self, request: LogoGenerationRequest,
                                   industry_profile: IndustryProfile) -> List[str]:
        """Create color specifications."""
        
        color_specs = []
        
        # User color preferences (highest priority)
        if request.color_preferences:
            color_specs.append(f"using colors: {', '.join(request.color_preferences)}")
        elif industry_profile.color_psychology.get("primary"):
            # Industry-recommended colors
            color_specs.append(f"color palette: {industry_profile.color_psychology['primary']}")
        
        # Color avoidance
        avoid_colors = []
        if request.avoid_colors:
            avoid_colors.extend(request.avoid_colors)
        if industry_profile.color_psychology.get("avoid"):
            avoid_colors.append(industry_profile.color_psychology["avoid"])
        
        if avoid_colors:
            color_specs.append(f"avoiding: {', '.join(avoid_colors)}")
        
        # Color treatment guidance
        if not request.color_preferences:  # Only add if no specific colors requested
            color_specs.append("professional color harmony")
            color_specs.append("brand-appropriate color psychology")
        
        return color_specs
    
    def _create_composition_rules(self, request: LogoGenerationRequest,
                                style_profile: StyleProfile) -> List[str]:
        """Create composition and layout rules."""
        
        rules = []
        
        # Style-specific composition rules
        if style_profile.composition_rules:
            rules.extend(style_profile.composition_rules[:2])
        
        # Universal composition guidelines
        rules.extend([
            "scalable vector design",
            "appropriate visual hierarchy",
            "balanced proportions"
        ])
        
        # Target audience considerations
        audience_rules = {
            "professionals": "corporate-appropriate composition",
            "consumers": "consumer-friendly layout",
            "businesses": "B2B professional styling",
            "creative": "artistic composition freedom",
            "general": "universally appealing layout"
        }
        
        audience = request.target_audience.lower()
        for key, rule in audience_rules.items():
            if key in audience:
                rules.append(rule)
                break
        
        return rules
    
    def _create_quality_requirements(self, optimization_level: PromptOptimizationLevel) -> List[str]:
        """Create quality requirements based on optimization level."""
        
        base_quality = [
            "high-quality design",
            "professional execution",
            "clean vector artwork"
        ]
        
        if optimization_level == PromptOptimizationLevel.PREMIUM:
            return base_quality + [
                "premium design quality",
                "exceptional attention to detail",
                "masterpiece-level execution",
                "award-worthy design standards"
            ]
        elif optimization_level == PromptOptimizationLevel.ADVANCED:
            return base_quality + [
                "advanced design techniques", 
                "sophisticated visual treatment",
                "professional design standards"
            ]
        else:  # BASIC
            return base_quality
    
    def _create_technical_specifications(self, request: LogoGenerationRequest) -> List[str]:
        """Create technical specifications."""
        
        specs = [
            "white background",
            "high contrast for readability",
            "suitable for branding applications",
            "SVG-ready vector design"
        ]
        
        # Format-specific requirements
        if request.format.value == "png":
            specs.append("crisp PNG output")
        elif request.format.value == "svg":
            specs.append("clean SVG paths")
        
        # Size considerations
        try:
            width, height = map(int, request.size.split('x'))
            if min(width, height) >= 1024:
                specs.append("high-resolution detail")
            else:
                specs.append("optimized for smaller sizes")
        except ValueError:
            pass  # Skip if size parsing fails
        
        return specs
    
    def _create_negative_prompts(self, industry_profile: IndustryProfile,
                               style_profile: StyleProfile) -> List[str]:
        """Create comprehensive negative prompts."""
        
        negative_prompts = []
        
        # Universal negatives
        negative_prompts.extend(self.universal_negative_prompts)
        
        # Industry-specific negatives
        if industry_profile.avoid_elements:
            negative_prompts.extend(industry_profile.avoid_elements)
        
        # Style-specific negatives
        if style_profile.negative_prompts:
            negative_prompts.extend(style_profile.negative_prompts)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(negative_prompts))
    
    def _create_generic_industry_profile(self, industry: str) -> IndustryProfile:
        """Create a generic industry profile for unknown industries."""
        
        return IndustryProfile(
            keywords=["professional", "quality", "service", "business"],
            visual_metaphors=["professional symbol", "business identity", "brand representation"],
            color_psychology={
                "primary": "professional blue, business gray, trustworthy navy",
                "secondary": "clean white, neutral gray",
                "avoid": "unprofessional colors, overly bright neon"
            },
            typography_style="professional sans-serif, business-appropriate",
            design_principles=["professionalism", "clarity", "business appeal"],
            avoid_elements=["unprofessional elements", "overly casual design"]
        )
    
    def optimize_for_provider(self, components: PromptComponents, 
                            provider_name: str) -> PromptComponents:
        """Optimize prompt components for specific AI provider."""
        
        if provider_name == "openai":
            return self._optimize_for_openai(components)
        elif provider_name == "stability":
            return self._optimize_for_stability(components)
        else:
            return components
    
    def _optimize_for_openai(self, components: PromptComponents) -> PromptComponents:
        """Optimize prompt for OpenAI DALL-E."""
        
        # DALL-E responds well to descriptive, natural language
        # Add more descriptive elements
        if "professional logo" in components.base_description:
            components.base_description = components.base_description.replace(
                "professional logo", "professionally designed corporate logo"
            )
        
        # Add quality emphases that work well with DALL-E
        components.quality_requirements.extend([
            "vector-style illustration",
            "commercial design quality",
            "brand-ready artwork"
        ])
        
        return components
    
    def _optimize_for_stability(self, components: PromptComponents) -> PromptComponents:
        """Optimize prompt for Stability AI."""
        
        # Stable Diffusion works well with specific artistic terms
        # Add artistic style descriptors
        components.style_modifiers.extend([
            "vector art style",
            "digital illustration",
            "graphic design artwork"
        ])
        
        # Enhance technical specifications for SD
        components.technical_specifications.extend([
            "clean digital art",
            "logo design artwork",
            "vector illustration style"
        ])
        
        return components


# Global instance
prompt_engineer = PromptEngineer()
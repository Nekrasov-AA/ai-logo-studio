"""
OpenAI Provider for DALL-E 3 Logo Generation
Advanced AI logo generation using OpenAI's DALL-E 3 model
"""

import asyncio
import logging
import time
import base64
import io
from typing import Dict, List, Optional, Any
import os

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base_provider import (
    BaseAIProvider, 
    AIGenerationResult, 
    AIProviderError, 
    LogoGenerationRequest,
    ProviderCapabilities,
    GenerationStyle,
    ImageFormat
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI DALL-E 3 provider for logo generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("openai", api_key or os.getenv("OPENAI_API_KEY"))
        self.client: Optional[AsyncOpenAI] = None
        self.model = "dall-e-3"
        
        # Style to prompt mapping for better results
        self.style_prompts = {
            GenerationStyle.MINIMALIST: "clean, minimal, simple geometric shapes, negative space, pure design",
            GenerationStyle.MODERN: "contemporary, sleek, modern typography, gradient effects, sophisticated",
            GenerationStyle.CLASSIC: "timeless, elegant, traditional, serif typography, established brand feel",
            GenerationStyle.PLAYFUL: "fun, colorful, dynamic, creative, energetic, friendly",
            GenerationStyle.BOLD: "strong, impactful, powerful, confident, striking design",
            GenerationStyle.ELEGANT: "sophisticated, refined, luxury, premium, graceful",
            GenerationStyle.TECH: "digital, innovative, futuristic, high-tech, cutting-edge",
            GenerationStyle.ORGANIC: "natural, flowing, organic shapes, eco-friendly, sustainable"
        }
        
        # Industry-specific enhancements
        self.industry_enhancements = {
            "technology": "digital, innovation, connectivity, neural networks, data flow",
            "healthcare": "medical, care, wellness, healing, trust, life",
            "finance": "stability, growth, prosperity, security, investment, premium",
            "food": "fresh, organic, appetizing, culinary, nourishment, quality",
            "retail": "shopping, fashion, lifestyle, consumer, brand, commerce",
            "education": "knowledge, learning, growth, development, academic, wisdom",
            "consulting": "professional, expertise, strategy, solutions, business",
            "creative": "artistic, inspiration, creativity, design, imagination, vision"
        }
        
    async def initialize(self) -> bool:
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI package not available. Install with: pip install openai")
            return False
            
        if not self.api_key:
            logger.error("OpenAI API key not provided")
            return False
            
        try:
            self.client = AsyncOpenAI(api_key=self.api_key)
            
            # Test connection with a simple API call
            models = await self.client.models.list()
            logger.info(f"OpenAI client initialized successfully. Available models: {len(models.data)}")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Get OpenAI DALL-E 3 capabilities."""
        return ProviderCapabilities(
            max_image_size=(1792, 1792),  # DALL-E 3 max size
            supported_formats=[ImageFormat.PNG],  # DALL-E 3 outputs PNG
            supports_style_control=True,
            supports_color_control=True,
            supports_text_in_image=True,
            supports_batch_generation=False,  # DALL-E 3 doesn't support batch
            max_batch_size=1,
            rate_limit_per_minute=50,  # Conservative estimate
            estimated_cost_per_image=0.04  # $0.04 per image for standard quality
        )
    
    async def generate_logo(self, request: LogoGenerationRequest) -> AIGenerationResult:
        """Generate a single logo using DALL-E 3."""
        await self._enforce_rate_limit()
        self._validate_request(request)
        
        if not self.client:
            raise AIProviderError("Client not initialized", self.provider_name)
        
        start_time = time.time()
        
        try:
            # Create optimized prompt
            prompt = await self._create_optimized_prompt(request)
            
            logger.info(f"Generating logo with DALL-E 3. Prompt: {prompt[:100]}...")
            
            # Generate image
            response = await self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self._map_size_to_dalle(request.size),
                quality="standard",  # or "hd" for higher quality
                n=1,
                response_format="b64_json"  # Get base64 encoded image
            )
            
            generation_time = time.time() - start_time
            
            # Extract image data
            image_data = base64.b64decode(response.data[0].b64_json)
            
            # Parse size
            width, height = map(int, request.size.split('x'))
            
            result = AIGenerationResult(
                image_data=image_data,
                format=ImageFormat.PNG,
                size=(width, height),
                provider=self.provider_name,
                model_used=self.model,
                generation_time=generation_time,
                prompt_used=prompt,
                metadata={
                    "revised_prompt": response.data[0].revised_prompt,
                    "quality": "standard",
                    "openai_response": {
                        "created": response.created,
                        "data_length": len(response.data)
                    }
                },
                confidence_score=0.85,  # DALL-E 3 generally produces high quality
                cost_tokens=1  # Approximate cost unit
            )
            
            logger.info(f"Successfully generated logo in {generation_time:.2f}s")
            return result
            
        except openai.RateLimitError as e:
            raise AIProviderError(f"Rate limit exceeded: {e}", self.provider_name, "RATE_LIMIT")
        except openai.APIError as e:
            raise AIProviderError(f"OpenAI API error: {e}", self.provider_name, "API_ERROR")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {e}", self.provider_name, "UNKNOWN_ERROR")
    
    async def generate_multiple_logos(self, request: LogoGenerationRequest, count: int = 3) -> List[AIGenerationResult]:
        """Generate multiple logo variations by calling generate_logo multiple times."""
        if count > 5:
            count = 5  # Reasonable limit
            
        logos = []
        base_prompt_parts = await self._get_base_prompt_parts(request)
        
        # Generate variations with different style emphases
        variations = [
            "primary design with balanced composition",
            "alternative layout with different proportions", 
            "creative variation with unique visual elements"
        ]
        
        for i in range(count):
            try:
                # Create request variation
                variation_request = LogoGenerationRequest(
                    business_name=request.business_name,
                    business_type=request.business_type,
                    industry=request.industry,
                    description=request.description,
                    style=request.style,
                    color_preferences=request.color_preferences,
                    avoid_colors=request.avoid_colors,
                    include_text=request.include_text,
                    preferred_layout=request.preferred_layout,
                    brand_personality=request.brand_personality,
                    target_audience=request.target_audience,
                    additional_requirements=f"{request.additional_requirements} {variations[i % len(variations)]}",
                    size=request.size,
                    format=request.format
                )
                
                logo = await self.generate_logo(variation_request)
                logo.metadata["variation_index"] = i
                logos.append(logo)
                
                # Small delay between requests to be respectful
                if i < count - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.warning(f"Failed to generate variation {i+1}: {e}")
                continue
        
        return logos
    
    async def _create_optimized_prompt(self, request: LogoGenerationRequest) -> str:
        """Create an optimized prompt for DALL-E 3 logo generation."""
        prompt_parts = await self._get_base_prompt_parts(request)
        
        # Combine all parts
        prompt = " ".join(filter(None, [
            f"Professional logo design for '{request.business_name}'",
            prompt_parts["business_context"],
            prompt_parts["style_guidance"],
            prompt_parts["visual_elements"],
            prompt_parts["color_guidance"],
            prompt_parts["layout_guidance"],
            prompt_parts["quality_requirements"],
            prompt_parts["technical_specs"]
        ]))
        
        # Ensure prompt isn't too long (DALL-E 3 has limits)
        if len(prompt) > 1000:
            prompt = prompt[:1000]
            
        return prompt
    
    async def _get_base_prompt_parts(self, request: LogoGenerationRequest) -> Dict[str, str]:
        """Get structured prompt parts for logo generation."""
        
        # Business context
        business_context = f"a {request.business_type} business"
        if request.description:
            business_context += f", {request.description}"
            
        # Industry enhancement
        industry_enhancement = self.industry_enhancements.get(
            request.industry.lower(), ""
        )
        
        # Style guidance
        style_guidance = self.style_prompts.get(request.style, "modern professional design")
        
        # Visual elements based on brand personality
        visual_elements = []
        personality_map = {
            "innovative": "cutting-edge geometric elements",
            "trustworthy": "stable, reliable visual foundation", 
            "premium": "luxury finishing touches and elegant details",
            "playful": "dynamic, energetic visual elements",
            "professional": "clean, business-appropriate design",
            "caring": "warm, approachable visual language",
            "bold": "strong, impactful visual presence"
        }
        
        for trait in request.brand_personality:
            if trait in personality_map:
                visual_elements.append(personality_map[trait])
        
        visual_elements_text = ", ".join(visual_elements) if visual_elements else "professional design elements"
        
        # Color guidance
        color_guidance = ""
        if request.color_preferences:
            color_guidance = f"using colors: {', '.join(request.color_preferences)}"
        if request.avoid_colors:
            avoid_text = f"avoiding colors: {', '.join(request.avoid_colors)}"
            color_guidance = f"{color_guidance}, {avoid_text}" if color_guidance else avoid_text
        
        # Layout guidance
        layout_guidance = ""
        if request.preferred_layout == "horizontal":
            layout_guidance = "horizontal layout with text beside symbol"
        elif request.preferred_layout == "vertical": 
            layout_guidance = "stacked vertical layout with symbol above text"
        elif request.preferred_layout == "icon_only":
            layout_guidance = "icon-only design without text"
        else:
            layout_guidance = "balanced composition with harmonious proportions"
        
        # Include text guidance
        text_guidance = ""
        if request.include_text and request.preferred_layout != "icon_only":
            text_guidance = f"include the text '{request.business_name}'"
        elif not request.include_text or request.preferred_layout == "icon_only":
            text_guidance = "symbolic design without text"
            
        # Quality requirements
        quality_requirements = "vector-style, scalable design, clean lines, professional quality"
        
        # Technical specifications
        technical_specs = "white background, high contrast, suitable for branding, SVG-ready design"
        if industry_enhancement:
            technical_specs += f", {industry_enhancement}"
        
        return {
            "business_context": business_context,
            "style_guidance": style_guidance,
            "visual_elements": visual_elements_text,
            "color_guidance": color_guidance,
            "layout_guidance": layout_guidance,
            "text_guidance": text_guidance,
            "quality_requirements": quality_requirements,
            "technical_specs": technical_specs
        }
    
    def _map_size_to_dalle(self, size: str) -> str:
        """Map requested size to DALL-E 3 supported sizes."""
        # DALL-E 3 supports: 1024x1024, 1152x896, 1344x768, 1792x1024, 1024x1792
        
        try:
            width, height = map(int, size.split('x'))
            
            # For square requests, use 1024x1024
            if abs(width - height) <= 100:
                return "1024x1024"
            
            # For landscape requests
            if width > height:
                if width >= 1792:
                    return "1792x1024"
                elif width >= 1344:
                    return "1344x768"
                else:
                    return "1152x896"
            
            # For portrait requests
            else:
                return "1024x1792"
                
        except ValueError:
            # Default fallback
            return "1024x1024"
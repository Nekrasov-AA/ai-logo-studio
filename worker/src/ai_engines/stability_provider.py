"""
Stability AI Provider for Stable Diffusion Logo Generation
Alternative AI provider using Stability AI's Stable Diffusion models
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
import os
import aiohttp

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


class StabilityProvider(BaseAIProvider):
    """Stability AI Stable Diffusion provider for logo generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("stability", api_key or os.getenv("STABILITY_API_KEY"))
        self.base_url = "https://api.stability.ai/v1"
        self.engine = "stable-diffusion-xl-1024-v1-0"  # Default engine
        
        # Style prompts optimized for Stable Diffusion
        self.style_prompts = {
            GenerationStyle.MINIMALIST: "minimalist logo, clean design, simple geometric shapes, negative space, vector art style",
            GenerationStyle.MODERN: "modern logo design, contemporary, sleek typography, gradient colors, professional",
            GenerationStyle.CLASSIC: "classic logo design, timeless, elegant typography, traditional, established brand",
            GenerationStyle.PLAYFUL: "playful logo, fun design, colorful, dynamic shapes, creative, friendly",
            GenerationStyle.BOLD: "bold logo design, strong typography, impactful, confident, striking",
            GenerationStyle.ELEGANT: "elegant logo, sophisticated design, luxury brand, premium, refined",
            GenerationStyle.TECH: "technology logo, digital design, futuristic, high-tech, innovation",
            GenerationStyle.ORGANIC: "organic logo design, natural shapes, eco-friendly, flowing, sustainable"
        }
        
        # Negative prompts to avoid unwanted elements
        self.negative_prompts = [
            "blurry", "low quality", "pixelated", "distorted", "watermark", 
            "text artifacts", "messy", "cluttered", "amateur", "unprofessional",
            "photo realistic", "3d render", "shadows", "realistic lighting"
        ]
        
        # Industry-specific style enhancements
        self.industry_styles = {
            "technology": "digital, circuit patterns, connectivity, data visualization, neural networks",
            "healthcare": "medical symbols, care, wellness, healing, trust, life symbols",
            "finance": "growth charts, stability symbols, prosperity, security, investment icons",
            "food": "culinary symbols, organic shapes, fresh ingredients, appetite appeal",
            "retail": "shopping symbols, lifestyle, consumer appeal, brand recognition",
            "education": "learning symbols, knowledge, growth, development, academic",
            "consulting": "professional symbols, expertise, strategy, business solutions",
            "creative": "artistic elements, inspiration symbols, creativity, design innovation"
        }
        
    async def initialize(self) -> bool:
        """Initialize Stability AI client."""
        if not self.api_key:
            logger.error("Stability AI API key not provided")
            return False
            
        try:
            # Test API connection
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                }
                
                async with session.get(f"{self.base_url}/engines/list", headers=headers) as response:
                    if response.status == 200:
                        engines_data = await response.json()
                        logger.info(f"Stability AI initialized successfully. Available engines: {len(engines_data)}")
                        self.is_initialized = True
                        return True
                    else:
                        logger.error(f"Stability AI API test failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to initialize Stability AI client: {e}")
            return False
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Get Stability AI capabilities."""
        return ProviderCapabilities(
            max_image_size=(1536, 1536),  # SDXL max recommended size
            supported_formats=[ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.WEBP],
            supports_style_control=True,
            supports_color_control=True,
            supports_text_in_image=True,
            supports_batch_generation=True,
            max_batch_size=4,
            rate_limit_per_minute=150,  # More generous than OpenAI
            estimated_cost_per_image=0.02  # Generally cheaper than DALL-E
        )
    
    async def generate_logo(self, request: LogoGenerationRequest) -> AIGenerationResult:
        """Generate a single logo using Stable Diffusion."""
        await self._enforce_rate_limit()
        self._validate_request(request)
        
        start_time = time.time()
        
        try:
            # Create optimized prompt
            prompt = await self._create_optimized_prompt(request)
            negative_prompt = ", ".join(self.negative_prompts)
            
            # Parse size
            width, height = map(int, request.size.split('x'))
            
            logger.info(f"Generating logo with Stability AI. Engine: {self.engine}")
            
            # Prepare request data
            data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    },
                    {
                        "text": negative_prompt,
                        "weight": -1.0
                    }
                ],
                "cfg_scale": 7.5,  # How strictly to follow the prompt
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30,  # Quality vs speed trade-off
                "seed": 0,  # Random seed
                "style_preset": self._get_style_preset(request.style)
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                url = f"{self.base_url}/generation/{self.engine}/text-to-image"
                
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise AIProviderError(
                            f"Stability AI API error: {response.status} - {error_text}",
                            self.provider_name,
                            f"HTTP_{response.status}"
                        )
                    
                    response_data = await response.json()
            
            generation_time = time.time() - start_time
            
            # Extract image data (Stability AI returns base64)
            import base64
            artifacts = response_data.get("artifacts", [])
            if not artifacts:
                raise AIProviderError("No image generated", self.provider_name, "NO_ARTIFACTS")
            
            image_data = base64.b64decode(artifacts[0]["base64"])
            
            result = AIGenerationResult(
                image_data=image_data,
                format=ImageFormat.PNG,  # Stability AI default
                size=(width, height),
                provider=self.provider_name,
                model_used=self.engine,
                generation_time=generation_time,
                prompt_used=prompt,
                metadata={
                    "negative_prompt": negative_prompt,
                    "cfg_scale": data["cfg_scale"],
                    "steps": data["steps"],
                    "seed": artifacts[0].get("seed", 0),
                    "style_preset": data.get("style_preset"),
                    "stability_response": {
                        "artifacts_count": len(artifacts),
                        "finish_reason": artifacts[0].get("finishReason")
                    }
                },
                confidence_score=0.80,  # Stable Diffusion produces good quality
                cost_tokens=1
            )
            
            logger.info(f"Successfully generated logo in {generation_time:.2f}s")
            return result
            
        except aiohttp.ClientError as e:
            raise AIProviderError(f"Network error: {e}", self.provider_name, "NETWORK_ERROR")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {e}", self.provider_name, "UNKNOWN_ERROR")
    
    async def generate_multiple_logos(self, request: LogoGenerationRequest, count: int = 3) -> List[AIGenerationResult]:
        """Generate multiple logo variations using batch generation."""
        if count > self.get_capabilities().max_batch_size:
            # Fall back to sequential generation for larger batches
            return await self._generate_sequential(request, count)
        
        await self._enforce_rate_limit()
        self._validate_request(request)
        
        start_time = time.time()
        
        try:
            prompt = await self._create_optimized_prompt(request)
            negative_prompt = ", ".join(self.negative_prompts)
            
            width, height = map(int, request.size.split('x'))
            
            # Batch generation request
            data = {
                "text_prompts": [
                    {"text": prompt, "weight": 1.0},
                    {"text": negative_prompt, "weight": -1.0}
                ],
                "cfg_scale": 7.5,
                "height": height,
                "width": width,
                "samples": count,  # Generate multiple samples
                "steps": 30,
                "seed": 0,
                "style_preset": self._get_style_preset(request.style)
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                url = f"{self.base_url}/generation/{self.engine}/text-to-image"
                
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise AIProviderError(
                            f"Stability AI batch error: {response.status} - {error_text}",
                            self.provider_name,
                            f"HTTP_{response.status}"
                        )
                    
                    response_data = await response.json()
            
            generation_time = time.time() - start_time
            
            # Process all artifacts
            import base64
            artifacts = response_data.get("artifacts", [])
            results = []
            
            for i, artifact in enumerate(artifacts):
                image_data = base64.b64decode(artifact["base64"])
                
                result = AIGenerationResult(
                    image_data=image_data,
                    format=ImageFormat.PNG,
                    size=(width, height),
                    provider=self.provider_name,
                    model_used=self.engine,
                    generation_time=generation_time / len(artifacts),  # Divide time among results
                    prompt_used=prompt,
                    metadata={
                        "negative_prompt": negative_prompt,
                        "batch_index": i,
                        "seed": artifact.get("seed", 0),
                        "finish_reason": artifact.get("finishReason")
                    },
                    confidence_score=0.80,
                    cost_tokens=1
                )
                results.append(result)
            
            logger.info(f"Successfully generated {len(results)} logos in {generation_time:.2f}s")
            return results
            
        except Exception as e:
            logger.warning(f"Batch generation failed: {e}, falling back to sequential")
            return await self._generate_sequential(request, count)
    
    async def _generate_sequential(self, request: LogoGenerationRequest, count: int) -> List[AIGenerationResult]:
        """Generate multiple logos sequentially."""
        results = []
        
        for i in range(count):
            try:
                # Add variation to the prompt
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
                    additional_requirements=f"{request.additional_requirements} variation {i+1}",
                    size=request.size,
                    format=request.format
                )
                
                result = await self.generate_logo(variation_request)
                result.metadata["sequential_index"] = i
                results.append(result)
                
                # Small delay between requests
                if i < count - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.warning(f"Failed to generate sequential variation {i+1}: {e}")
                continue
                
        return results
    
    async def _create_optimized_prompt(self, request: LogoGenerationRequest) -> str:
        """Create an optimized prompt for Stable Diffusion."""
        
        prompt_parts = []
        
        # Base description
        prompt_parts.append(f"professional logo design for '{request.business_name}'")
        prompt_parts.append(f"a {request.business_type} business")
        
        # Style guidance
        style_prompt = self.style_prompts.get(request.style, "professional logo design")
        prompt_parts.append(style_prompt)
        
        # Industry enhancement
        industry_style = self.industry_styles.get(request.industry.lower(), "")
        if industry_style:
            prompt_parts.append(industry_style)
        
        # Color preferences
        if request.color_preferences:
            prompt_parts.append(f"colors: {', '.join(request.color_preferences)}")
        
        # Brand personality
        if request.brand_personality:
            personality_text = ", ".join(request.brand_personality)
            prompt_parts.append(f"brand personality: {personality_text}")
        
        # Layout preferences
        if request.preferred_layout == "horizontal":
            prompt_parts.append("horizontal layout")
        elif request.preferred_layout == "vertical":
            prompt_parts.append("vertical stacked layout")
        elif request.preferred_layout == "icon_only":
            prompt_parts.append("icon only, no text")
        
        # Text inclusion
        if request.include_text and request.preferred_layout != "icon_only":
            prompt_parts.append(f"include text '{request.business_name}'")
        else:
            prompt_parts.append("symbol only, no text")
        
        # Quality modifiers
        prompt_parts.extend([
            "vector art style",
            "clean design", 
            "professional quality",
            "white background",
            "high contrast",
            "scalable"
        ])
        
        # Additional requirements
        if request.additional_requirements:
            prompt_parts.append(request.additional_requirements)
        
        return ", ".join(filter(None, prompt_parts))
    
    def _get_style_preset(self, style: GenerationStyle) -> Optional[str]:
        """Map generation style to Stability AI style preset."""
        
        style_presets = {
            GenerationStyle.MINIMALIST: "digital-art",
            GenerationStyle.MODERN: "digital-art", 
            GenerationStyle.CLASSIC: "enhance",
            GenerationStyle.PLAYFUL: "comic-book",
            GenerationStyle.BOLD: "digital-art",
            GenerationStyle.ELEGANT: "enhance",
            GenerationStyle.TECH: "digital-art",
            GenerationStyle.ORGANIC: "enhance"
        }
        
        return style_presets.get(style, "digital-art")
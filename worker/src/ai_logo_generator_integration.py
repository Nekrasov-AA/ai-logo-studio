"""
AI-Powered Logo Generation Integration
Main integration module that combines all AI components for logo generation
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
import os

from .ai_engines import (
    AIProviderManager,
    ProviderConfig,
    ProviderPriority,
    OpenAIProvider,
    StabilityProvider,
    PromptEngineer,
    ImageProcessor,
    LogoGenerationRequest,
    GenerationStyle,
    ImageFormat,
    AIGenerationResult,
    ProcessingOptions,
    PromptOptimizationLevel
)

logger = logging.getLogger(__name__)


class AILogoGenerator:
    """
    Complete AI-powered logo generation system.
    Integrates multiple AI providers, prompt engineering, and image processing.
    """
    
    def __init__(self):
        """Initialize AI logo generator."""
        self.provider_manager = AIProviderManager()
        self.prompt_engineer = PromptEngineer()
        self.image_processor = ImageProcessor()
        self.is_initialized = False
        
        # Configuration
        self.default_provider_configs = self._create_default_provider_configs()
        
    def _create_default_provider_configs(self) -> Dict[str, ProviderConfig]:
        """Create default provider configurations."""
        
        configs = {}
        
        # OpenAI DALL-E 3 (Premium)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            configs["openai"] = ProviderConfig(
                provider_class=OpenAIProvider,
                priority=ProviderPriority.HIGH,
                api_key=openai_key,
                enabled=True,
                max_retries=2,
                timeout_seconds=90.0,
                cost_weight=2.0,  # More expensive
                quality_weight=1.0  # Highest quality
            )
        
        # Stability AI (Alternative)
        stability_key = os.getenv("STABILITY_API_KEY")
        if stability_key:
            configs["stability"] = ProviderConfig(
                provider_class=StabilityProvider,
                priority=ProviderPriority.MEDIUM,
                api_key=stability_key,
                enabled=True,
                max_retries=3,
                timeout_seconds=120.0,
                cost_weight=1.0,  # Cheaper
                quality_weight=0.9  # Good quality
            )
        
        return configs
    
    async def initialize(self, custom_configs: Optional[Dict[str, ProviderConfig]] = None) -> bool:
        """
        Initialize the AI logo generator.
        
        Args:
            custom_configs: Optional custom provider configurations
            
        Returns:
            bool: True if initialization successful
        """
        
        logger.info("Initializing AI Logo Generator...")
        
        try:
            # Use custom configs or defaults
            configs = custom_configs or self.default_provider_configs
            
            if not configs:
                logger.warning("No AI provider configurations available. Check API keys.")
                return False
            
            # Initialize provider manager
            success = await self.provider_manager.initialize(configs)
            
            if not success:
                logger.error("Failed to initialize AI providers")
                return False
            
            # Check image processor availability
            if not self.image_processor.is_available:
                logger.warning("Image processor not fully available. Some features may be limited.")
            
            self.is_initialized = True
            
            # Log available providers
            available_providers = [
                name for name, provider in self.provider_manager.providers.items()
                if provider.is_available()
            ]
            
            logger.info(f"AI Logo Generator initialized successfully with providers: {available_providers}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Logo Generator: {e}")
            return False
    
    async def generate_logo_variants(self, 
                                   business_name: str,
                                   business_type: str,
                                   industry: str,
                                   description: str = "",
                                   style: GenerationStyle = GenerationStyle.MODERN,
                                   color_preferences: List[str] = None,
                                   brand_personality: List[str] = None,
                                   target_audience: str = "general",
                                   count: int = 3,
                                   preferred_providers: List[str] = None,
                                   processing_options: Optional[ProcessingOptions] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple AI-powered logo variants.
        
        Args:
            business_name: Name of the business
            business_type: Type of business (e.g., "Technology Company")
            industry: Industry category (e.g., "technology")
            description: Business description
            style: Logo generation style
            color_preferences: Preferred colors
            brand_personality: Brand personality traits
            target_audience: Target audience
            count: Number of variants to generate
            preferred_providers: Preferred AI providers to use
            processing_options: Image processing options
            
        Returns:
            List of logo variant dictionaries with metadata
        """
        
        if not self.is_initialized:
            raise RuntimeError("AI Logo Generator not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        logger.info(f"Generating {count} AI logo variants for '{business_name}' ({industry})")
        
        try:
            # Create generation request
            request = LogoGenerationRequest(
                business_name=business_name,
                business_type=business_type,
                industry=industry,
                description=description,
                style=style,
                color_preferences=color_preferences or [],
                brand_personality=brand_personality or [],
                target_audience=target_audience,
                include_text=True,
                preferred_layout="balanced"
            )
            
            # Generate AI images
            ai_results = await self.provider_manager.generate_multiple_logos(
                request=request,
                count=count,
                distribute_across_providers=True
            )
            
            if not ai_results:
                raise RuntimeError("No AI results generated")
            
            # Process images if processor available
            if self.image_processor.is_available and processing_options is not None:
                logger.info("Post-processing AI-generated images...")
                
                processed_results = await self.image_processor.process_multiple_results(
                    ai_results, processing_options
                )
            else:
                processed_results = None
            
            # Create final variant packages
            variants = []
            
            for i, ai_result in enumerate(ai_results):
                processed_result = processed_results[i] if processed_results else None
                
                variant = await self._create_variant_package(
                    ai_result=ai_result,
                    processed_result=processed_result,
                    request=request,
                    variant_index=i
                )
                
                variants.append(variant)
            
            generation_time = time.time() - start_time
            
            logger.info(f"Successfully generated {len(variants)} AI logo variants in {generation_time:.2f}s")
            
            return variants
            
        except Exception as e:
            logger.error(f"Failed to generate logo variants: {e}")
            raise
    
    async def generate_single_logo(self,
                                 business_name: str,
                                 business_type: str, 
                                 industry: str,
                                 description: str = "",
                                 style: GenerationStyle = GenerationStyle.MODERN,
                                 color_preferences: List[str] = None,
                                 brand_personality: List[str] = None,
                                 optimization_level: PromptOptimizationLevel = PromptOptimizationLevel.ADVANCED,
                                 preferred_provider: str = None) -> Dict[str, Any]:
        """
        Generate a single high-quality AI logo with advanced optimization.
        
        Args:
            business_name: Name of the business
            business_type: Type of business
            industry: Industry category
            description: Business description
            style: Logo generation style
            color_preferences: Preferred colors
            brand_personality: Brand personality traits
            optimization_level: Prompt optimization level
            preferred_provider: Preferred AI provider
            
        Returns:
            Dictionary with logo data and metadata
        """
        
        if not self.is_initialized:
            raise RuntimeError("AI Logo Generator not initialized. Call initialize() first.")
        
        logger.info(f"Generating premium AI logo for '{business_name}' with {optimization_level.value} optimization")
        
        try:
            # Create optimized generation request
            request = LogoGenerationRequest(
                business_name=business_name,
                business_type=business_type,
                industry=industry,
                description=description,
                style=style,
                color_preferences=color_preferences or [],
                brand_personality=brand_personality or [],
                include_text=True,
                preferred_layout="balanced",
                size="1024x1024"
            )
            
            # Generate advanced prompt
            prompt_components = self.prompt_engineer.create_advanced_prompt(
                request, optimization_level
            )
            
            # Optimize for specific provider if requested
            if preferred_provider:
                prompt_components = self.prompt_engineer.optimize_for_provider(
                    prompt_components, preferred_provider
                )
            
            # Generate with preferred provider or best available
            preferred_providers = [preferred_provider] if preferred_provider else None
            
            ai_result = await self.provider_manager.generate_logo(
                request, preferred_providers
            )
            
            # Premium processing options
            processing_options = ProcessingOptions(
                remove_background=True,
                enhance_contrast=True,
                sharpen_edges=True,
                normalize_colors=True,
                optimize_for_vector=True,
                processing_level=optimization_level.value  # Map to processing level
            )
            
            # Process image
            processed_result = None
            if self.image_processor.is_available:
                processed_result = await self.image_processor.process_ai_result(
                    ai_result, processing_options
                )
            
            # Create variant package
            variant = await self._create_variant_package(
                ai_result=ai_result,
                processed_result=processed_result,
                request=request,
                variant_index=0,
                prompt_components=prompt_components
            )
            
            logger.info(f"Successfully generated premium AI logo for '{business_name}'")
            
            return variant
            
        except Exception as e:
            logger.error(f"Failed to generate premium logo: {e}")
            raise
    
    async def _create_variant_package(self,
                                    ai_result: AIGenerationResult,
                                    processed_result: Optional[Any],
                                    request: LogoGenerationRequest,
                                    variant_index: int,
                                    prompt_components: Optional[Any] = None) -> Dict[str, Any]:
        """Create a comprehensive variant package with all metadata."""
        
        package = {
            # Basic info
            "variant_id": f"{request.business_name.lower().replace(' ', '_')}_v{variant_index:02d}",
            "business_name": request.business_name,
            "business_type": request.business_type,
            "industry": request.industry,
            
            # Generation data
            "ai_result": {
                "image_data": ai_result.image_data,
                "format": ai_result.format.value,
                "size": ai_result.size,
                "provider": ai_result.provider,
                "model_used": ai_result.model_used,
                "generation_time": ai_result.generation_time,
                "confidence_score": ai_result.confidence_score,
                "cost_tokens": ai_result.cost_tokens,
                "metadata": ai_result.metadata
            },
            
            # Style and branding
            "style_info": {
                "generation_style": request.style.value,
                "color_preferences": request.color_preferences,
                "brand_personality": request.brand_personality,
                "target_audience": request.target_audience
            },
            
            # Processing results (if available)
            "processed_result": None,
            
            # Quality metrics
            "quality_metrics": {
                "ai_confidence": ai_result.confidence_score,
                "generation_time": ai_result.generation_time,
                "provider_used": ai_result.provider
            },
            
            # Prompt information (if available)
            "prompt_info": None
        }
        
        # Add processed result if available
        if processed_result:
            package["processed_result"] = {
                "processed_image": processed_result.processed_image,
                "format": processed_result.format.value,
                "size": processed_result.processed_size,
                "processing_time": processed_result.processing_time,
                "operations_applied": processed_result.operations_applied,
                "quality_score": processed_result.quality_score,
                "metadata": processed_result.metadata
            }
            
            # Update quality metrics
            package["quality_metrics"]["processing_quality"] = processed_result.quality_score
            package["quality_metrics"]["total_processing_time"] = (
                ai_result.generation_time + processed_result.processing_time
            )
        
        # Add prompt information if available
        if prompt_components:
            package["prompt_info"] = {
                "full_prompt": prompt_components.to_prompt(),
                "negative_prompt": prompt_components.get_negative_prompt(),
                "components": {
                    "base_description": prompt_components.base_description,
                    "industry_context": prompt_components.industry_context,
                    "style_modifiers": prompt_components.style_modifiers,
                    "visual_elements": prompt_components.visual_elements,
                    "color_specifications": prompt_components.color_specifications
                }
            }
        
        return package
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and health information."""
        
        if not self.is_initialized:
            return {
                "status": "not_initialized",
                "message": "AI Logo Generator not initialized"
            }
        
        # Get provider health
        provider_health = await self.provider_manager.health_check()
        
        # Get provider metrics
        provider_metrics = self.provider_manager.get_metrics()
        
        return {
            "status": "healthy" if provider_health["manager_status"] == "healthy" else "degraded",
            "initialization_time": time.time(),  # Would track actual init time
            "providers": {
                "total": provider_health["total_providers"],
                "available": provider_health["available_providers"],
                "health": provider_health["providers"],
                "metrics": provider_metrics
            },
            "image_processor": {
                "available": self.image_processor.is_available,
                "pil_available": hasattr(self.image_processor, 'PIL_AVAILABLE'),
                "opencv_available": hasattr(self.image_processor, 'OPENCV_AVAILABLE')
            },
            "capabilities": {
                "styles_supported": [style.value for style in GenerationStyle],
                "formats_supported": [fmt.value for fmt in ImageFormat],
                "max_batch_size": 10,  # Configure as needed
                "processing_available": self.image_processor.is_available
            }
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up AI Logo Generator...")
        
        # Reset provider metrics if needed
        if hasattr(self.provider_manager, 'reset_metrics'):
            self.provider_manager.reset_metrics()
        
        self.is_initialized = False


# Global instance for easy import
ai_logo_generator = AILogoGenerator()
"""
Example integration of AI Image Generator with existing consumer.py
Demonstrates how to integrate the new AI system with the current workflow
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
import time

# AI Image Generator imports
from .ai_logo_generator_integration import ai_logo_generator
from .ai_engines import GenerationStyle, ProcessingOptions, ProcessingLevel

logger = logging.getLogger(__name__)


class AIConsumerIntegration:
    """
    Integration layer for AI Image Generator with existing consumer workflow.
    Provides backward compatibility while enabling advanced AI features.
    """
    
    def __init__(self):
        self.ai_initialized = False
        self.fallback_to_legacy = True
        
        # Style mapping from legacy preferences to AI styles
        self.style_mapping = {
            "minimalist": GenerationStyle.MINIMALIST,
            "minimal": GenerationStyle.MINIMALIST,
            "modern": GenerationStyle.MODERN,
            "contemporary": GenerationStyle.MODERN,
            "classic": GenerationStyle.CLASSIC,
            "traditional": GenerationStyle.CLASSIC,
            "playful": GenerationStyle.PLAYFUL,
            "fun": GenerationStyle.PLAYFUL,
            "bold": GenerationStyle.BOLD,
            "strong": GenerationStyle.BOLD,
            "elegant": GenerationStyle.ELEGANT,
            "sophisticated": GenerationStyle.ELEGANT,
            "tech": GenerationStyle.TECH,
            "technology": GenerationStyle.TECH,
            "organic": GenerationStyle.ORGANIC,
            "natural": GenerationStyle.ORGANIC
        }
        
        # Industry detection keywords
        self.industry_keywords = {
            "technology": ["tech", "software", "ai", "digital", "data", "app", "platform", "saas", "it"],
            "healthcare": ["health", "medical", "care", "hospital", "clinic", "wellness", "therapy", "pharma"],
            "finance": ["finance", "bank", "investment", "insurance", "trading", "financial", "fintech"],
            "food": ["food", "restaurant", "kitchen", "cooking", "cafe", "bakery", "catering", "culinary"],
            "retail": ["retail", "shop", "store", "fashion", "clothing", "boutique", "brand", "commerce"],
            "creative": ["creative", "design", "art", "agency", "studio", "media", "advertising", "marketing"],
            "education": ["education", "school", "learning", "university", "training", "academic", "course"],
            "consulting": ["consulting", "advisory", "strategy", "management", "business", "professional"]
        }
    
    async def initialize_ai_system(self) -> bool:
        """Initialize AI system with graceful fallback."""
        try:
            logger.info("Initializing AI Logo Generation system...")
            
            success = await ai_logo_generator.initialize()
            
            if success:
                self.ai_initialized = True
                logger.info("✅ AI Logo Generation system initialized successfully")
                
                # Log available providers
                status = await ai_logo_generator.get_system_status()
                available_providers = status.get("providers", {}).get("available", 0)
                logger.info(f"Available AI providers: {available_providers}")
                
                return True
            else:
                logger.warning("⚠️ AI system initialization failed, will use fallback")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI initialization error: {e}")
            return False
    
    def detect_industry(self, business_type: str, description: str = "") -> str:
        """Detect industry from business type and description."""
        
        text = f"{business_type} {description}".lower()
        
        # Score each industry based on keyword matches
        scores = {}
        for industry, keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[industry] = score
        
        # Return industry with highest score, default to 'other'
        return max(scores.items(), key=lambda x: x[1])[0] if scores else "other"
    
    def map_style_preference(self, style_pref: str) -> GenerationStyle:
        """Map legacy style preference to AI GenerationStyle."""
        
        if isinstance(style_pref, str):
            return self.style_mapping.get(style_pref.lower(), GenerationStyle.MODERN)
        
        return GenerationStyle.MODERN  # Default
    
    def extract_brand_personality(self, prefs: Dict[str, Any]) -> List[str]:
        """Extract brand personality traits from preferences."""
        
        personality = []
        
        # Check explicit personality settings
        if "personality" in prefs:
            if isinstance(prefs["personality"], list):
                personality.extend(prefs["personality"])
            elif isinstance(prefs["personality"], str):
                personality.append(prefs["personality"])
        
        # Infer from style preferences
        style = prefs.get("style", "").lower()
        style_personality_map = {
            "minimalist": "clean",
            "modern": "innovative", 
            "classic": "trustworthy",
            "playful": "friendly",
            "bold": "confident",
            "elegant": "premium",
            "tech": "innovative",
            "organic": "caring"
        }
        
        if style in style_personality_map:
            personality.append(style_personality_map[style])
        
        # Infer from business type
        business_type = prefs.get("business_type", "").lower()
        if "premium" in business_type or "luxury" in business_type:
            personality.append("premium")
        if "innovative" in business_type or "cutting-edge" in business_type:
            personality.append("innovative")
        if "trusted" in business_type or "reliable" in business_type:
            personality.append("trustworthy")
        
        # Remove duplicates and limit to 3
        return list(dict.fromkeys(personality))[:3]
    
    def get_processing_options(self, business_type: str, style: str) -> ProcessingOptions:
        """Get recommended processing options based on business type and style."""
        
        # Tech companies need crisp, clean logos
        if any(keyword in business_type.lower() for keyword in ["tech", "software", "digital"]):
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=True,
                sharpen_edges=True,
                normalize_colors=True,
                optimize_for_vector=True,
                processing_level=ProcessingLevel.AGGRESSIVE
            )
        
        # Healthcare needs softer, more trustworthy appearance
        elif any(keyword in business_type.lower() for keyword in ["health", "medical", "care"]):
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=False,
                sharpen_edges=False,
                normalize_colors=True,
                optimize_for_vector=True,
                processing_level=ProcessingLevel.STANDARD
            )
        
        # Creative industries might want to preserve artistic elements
        elif any(keyword in business_type.lower() for keyword in ["creative", "design", "art"]):
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=False,
                sharpen_edges=False,
                normalize_colors=False,
                optimize_for_vector=False,
                processing_level=ProcessingLevel.MINIMAL
            )
        
        # Default processing
        else:
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=True,
                sharpen_edges=True,
                normalize_colors=True,
                optimize_for_vector=True,
                processing_level=ProcessingLevel.STANDARD
            )
    
    def create_color_palette_from_ai_result(self, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Create color palette dictionary from AI generation result."""
        
        # Extract colors from AI result metadata
        ai_metadata = variant.get("ai_result", {}).get("metadata", {})
        style_info = variant.get("style_info", {})
        
        # Use color preferences if available
        colors = style_info.get("color_preferences", [])
        
        # If no colors specified, create default palette based on industry/style
        if not colors:
            industry = variant.get("industry", "other")
            style = variant.get("style_info", {}).get("generation_style", "modern")
            
            # Industry-based default colors
            industry_colors = {
                "technology": ["#0066FF", "#00CCFF", "#4A90E2"],
                "healthcare": ["#2E8B57", "#20B2AA", "#66CDAA"], 
                "finance": ["#1B365D", "#2E5D8B", "#4682B4"],
                "creative": ["#FF6B35", "#F7931E", "#FFD23F"],
                "food": ["#FF8C42", "#FFA726", "#8BC34A"]
            }
            
            colors = industry_colors.get(industry, ["#0066CC", "#4D9EE8", "#B3D9FF"])
        
        # Ensure we have at least 3 colors
        while len(colors) < 3:
            colors.append("#666666")  # Gray fallback
        
        return {
            "name": f"AI Generated {variant.get('business_name', 'Logo')}",
            "colors": colors[:4]  # Limit to 4 colors
        }
    
    async def process_with_ai_generation(self, payload: dict) -> bool:
        """
        Process logo generation using AI system.
        Returns True if successful, False if should fallback to legacy.
        """
        
        if not self.ai_initialized:
            logger.info("AI system not available, using legacy generation")
            return False
        
        try:
            job_id = payload["job_id"]
            business_type = payload.get("business_type", "business")
            prefs = payload.get("prefs", {})
            
            logger.info(f"🤖 AI processing job {job_id} for '{business_type}'")
            
            # Extract parameters
            business_name = prefs.get('business_name', business_type.split(' - ')[0] if ' - ' in business_type else business_type)
            description = prefs.get('description', f"A {business_type} business")
            industry = self.detect_industry(business_type, description)
            style = self.map_style_preference(prefs.get('style', 'modern'))
            color_preferences = prefs.get('colors', [])
            brand_personality = self.extract_brand_personality(prefs)
            
            # Get processing options
            processing_options = self.get_processing_options(business_type, style.value)
            
            logger.info(f"🎨 Generating for industry: {industry}, style: {style.value}")
            
            # Generate AI logo variants
            variants = await ai_logo_generator.generate_logo_variants(
                business_name=business_name,
                business_type=business_type,
                industry=industry,
                description=description,
                style=style,
                color_preferences=color_preferences,
                brand_personality=brand_personality,
                target_audience=prefs.get('target_audience', 'general'),
                count=3,  # Generate 3 variants
                processing_options=processing_options
            )
            
            if not variants:
                logger.warning("No AI variants generated, falling back to legacy")
                return False
            
            # Save variants to S3 and database
            for i, variant in enumerate(variants):
                try:
                    # Use processed image if available, otherwise original AI result
                    if variant.get("processed_result") and variant["processed_result"].get("processed_image"):
                        image_data = variant["processed_result"]["processed_image"]
                        format_ext = variant["processed_result"]["format"].lower()
                    else:
                        image_data = variant["ai_result"]["image_data"]
                        format_ext = variant["ai_result"]["format"].lower()
                    
                    # Create S3 key
                    provider = variant["ai_result"]["provider"]
                    key = f"jobs/{job_id}/v{i:02d}_ai_{provider}.{format_ext}"
                    
                    # Upload to S3 (using existing function)
                    from . import s3_client  # Import from consumer.py context
                    s3 = s3_client()
                    content_type = f"image/{format_ext}"
                    s3.put_object(Bucket="ai-logo-studio", Key=key, Body=image_data, ContentType=content_type)
                    
                    # Create palette from AI result
                    palette = self.create_color_palette_from_ai_result(variant)
                    
                    # Save to database (using existing function)
                    from . import insert_variant  # Import from consumer.py context
                    await insert_variant(job_id, i, palette, key)
                    
                    # Log success
                    quality_score = variant.get("quality_metrics", {}).get("ai_confidence", 0.8)
                    logger.info(f"✨ Saved AI variant {i+1}: {provider} (quality: {quality_score:.2f})")
                    
                except Exception as e:
                    logger.error(f"Failed to save AI variant {i}: {e}")
                    continue
            
            logger.info(f"✅ AI processing completed for job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ AI processing failed for job {job_id}: {e}")
            return False
    
    async def get_ai_system_metrics(self) -> Dict[str, Any]:
        """Get AI system performance metrics."""
        
        if not self.ai_initialized:
            return {"status": "not_initialized"}
        
        try:
            status = await ai_logo_generator.get_system_status()
            return {
                "status": status["status"],
                "providers_available": status["providers"]["available"],
                "providers_total": status["providers"]["total"],
                "image_processing_available": status["image_processor"]["available"],
                "last_check": time.time()
            }
        except Exception as e:
            logger.error(f"Failed to get AI metrics: {e}")
            return {"status": "error", "error": str(e)}


# Global integration instance
ai_consumer_integration = AIConsumerIntegration()


# Example of how to modify the existing process function in consumer.py
async def enhanced_process_function(payload: dict):
    """
    Enhanced process function that uses AI when available, falls back to legacy.
    
    This would replace or enhance the existing process() function in consumer.py
    """
    
    job_id = payload["job_id"]
    
    # Initialize AI system if not done yet
    if not ai_consumer_integration.ai_initialized:
        await ai_consumer_integration.initialize_ai_system()
    
    try:
        # Set status to generating
        from . import set_status  # Import from consumer.py context
        await set_status(job_id, "generating")
        
        # Try AI generation first
        ai_success = await ai_consumer_integration.process_with_ai_generation(payload)
        
        if ai_success:
            # AI generation succeeded
            await set_status(job_id, "exporting") 
            await asyncio.sleep(0.2)
            await set_status(job_id, "done")
            
            logger.info(f"✅ Job {job_id} completed with AI generation")
            
        else:
            # Fall back to legacy generation
            logger.info(f"🔄 Falling back to legacy generation for job {job_id}")
            
            # Import and call original process logic here
            # from .original_consumer import original_process_function
            # await original_process_function(payload)
            
            # Or implement legacy fallback inline:
            await legacy_fallback_process(payload)
    
    except Exception as e:
        logger.error(f"❌ Processing failed for job {job_id}: {e}")
        await set_status(job_id, "error")


async def legacy_fallback_process(payload: dict):
    """Legacy fallback processing (existing logic from consumer.py)."""
    
    # This would contain the existing programmatic generation logic
    # from the original consumer.py file
    
    job_id = payload["job_id"]
    business_type = payload.get("business_type", "business")
    prefs = payload.get("prefs", {})
    
    logger.info(f"📝 Legacy processing for job {job_id}")
    
    # Use existing LAYOUTS and generation logic
    from . import LAYOUTS, suggest_palettes, upload_svg, insert_variant
    
    palettes = suggest_palettes(business_type, prefs)
    
    idx = 0
    for palette in palettes[:3]:
        for layout_func in LAYOUTS[:2]:
            svg_bytes = layout_func(business_type, palette)
            key = f"jobs/{job_id}/v{idx:02d}_legacy_{palette['name']}.svg"
            upload_svg(key, svg_bytes)
            await insert_variant(job_id, idx, palette, key)
            idx += 1
    
    await set_status(job_id, "exporting")
    await asyncio.sleep(0.2) 
    await set_status(job_id, "done")
    
    logger.info(f"✅ Legacy processing completed for job {job_id}")


# Health check endpoint for AI system
async def ai_health_check() -> Dict[str, Any]:
    """Health check for AI system - can be called from API."""
    
    return await ai_consumer_integration.get_ai_system_metrics()
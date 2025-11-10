"""
Advanced Image Processing Pipeline
Post-processing for AI-generated images to optimize for logo use
"""

import asyncio
import logging
import io
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

try:
    from PIL import Image, ImageFilter, ImageEnhance, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from .base_provider import AIGenerationResult, ImageFormat

logger = logging.getLogger(__name__)


class ProcessingLevel(Enum):
    """Image processing intensity levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


class BackgroundRemovalMethod(Enum):
    """Background removal methods."""
    THRESHOLD = "threshold"
    EDGE_DETECTION = "edge_detection"
    COLOR_ANALYSIS = "color_analysis"
    HYBRID = "hybrid"


@dataclass
class ProcessingOptions:
    """Options for image processing pipeline."""
    remove_background: bool = True
    enhance_contrast: bool = True
    sharpen_edges: bool = True
    normalize_colors: bool = True
    optimize_for_vector: bool = True
    background_removal_method: BackgroundRemovalMethod = BackgroundRemovalMethod.HYBRID
    processing_level: ProcessingLevel = ProcessingLevel.STANDARD
    target_size: Optional[Tuple[int, int]] = None
    preserve_transparency: bool = True


@dataclass
class ProcessingResult:
    """Result of image processing."""
    processed_image: bytes
    original_size: Tuple[int, int]
    processed_size: Tuple[int, int]
    format: ImageFormat
    processing_time: float
    operations_applied: List[str]
    quality_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ImageProcessor:
    """Advanced image processor for AI-generated logos."""
    
    def __init__(self):
        """Initialize image processor."""
        self.is_available = PIL_AVAILABLE
        
        if not PIL_AVAILABLE:
            logger.error("PIL not available. Install with: pip install Pillow")
        
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available. Some advanced features will be limited.")
    
    async def process_ai_result(self, ai_result: AIGenerationResult, 
                              options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """Process AI generation result for logo optimization."""
        
        if not self.is_available:
            raise RuntimeError("Image processing not available. PIL not installed.")
        
        if options is None:
            options = ProcessingOptions()
        
        start_time = asyncio.get_event_loop().time()
        operations_applied = []
        
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(ai_result.image_data))
            original_size = image.size
            
            logger.info(f"Processing AI-generated image: {original_size[0]}x{original_size[1]}")
            
            # Ensure we're working with RGBA for transparency support
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                operations_applied.append("converted_to_rgba")
            
            # Background removal (if requested)
            if options.remove_background:
                image = await self._remove_background(image, options.background_removal_method)
                operations_applied.append(f"background_removal_{options.background_removal_method.value}")
            
            # Contrast enhancement
            if options.enhance_contrast:
                image = await self._enhance_contrast(image, options.processing_level)
                operations_applied.append("contrast_enhancement")
            
            # Edge sharpening
            if options.sharpen_edges:
                image = await self._sharpen_edges(image, options.processing_level)
                operations_applied.append("edge_sharpening")
            
            # Color normalization
            if options.normalize_colors:
                image = await self._normalize_colors(image)
                operations_applied.append("color_normalization")
            
            # Vector optimization
            if options.optimize_for_vector:
                image = await self._optimize_for_vector(image)
                operations_applied.append("vector_optimization")
            
            # Resize if target size specified
            if options.target_size:
                image = await self._smart_resize(image, options.target_size)
                operations_applied.append(f"resized_to_{options.target_size[0]}x{options.target_size[1]}")
            
            # Final cleanup
            image = await self._cleanup_image(image, options)
            operations_applied.append("final_cleanup")
            
            # Convert to output format
            output_buffer = io.BytesIO()
            
            if options.preserve_transparency and ai_result.format == ImageFormat.PNG:
                image.save(output_buffer, format='PNG', optimize=True)
                output_format = ImageFormat.PNG
            elif ai_result.format == ImageFormat.JPEG:
                # Convert to RGB for JPEG (no transparency)
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                rgb_image.save(output_buffer, format='JPEG', quality=95, optimize=True)
                image = rgb_image
                output_format = ImageFormat.JPEG
            else:
                # Default to PNG
                image.save(output_buffer, format='PNG', optimize=True)
                output_format = ImageFormat.PNG
            
            processed_data = output_buffer.getvalue()
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(image, original_size)
            
            result = ProcessingResult(
                processed_image=processed_data,
                original_size=original_size,
                processed_size=image.size,
                format=output_format,
                processing_time=processing_time,
                operations_applied=operations_applied,
                quality_score=quality_score,
                metadata={
                    "original_format": ai_result.format.value,
                    "ai_provider": ai_result.provider,
                    "processing_options": {
                        "remove_background": options.remove_background,
                        "enhance_contrast": options.enhance_contrast,
                        "sharpen_edges": options.sharpen_edges,
                        "normalize_colors": options.normalize_colors,
                        "optimize_for_vector": options.optimize_for_vector
                    }
                }
            )
            
            logger.info(f"Image processing completed in {processing_time:.2f}s. Quality score: {quality_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
    
    async def _remove_background(self, image: Image.Image, 
                               method: BackgroundRemovalMethod) -> Image.Image:
        """Remove background from image using specified method."""
        
        if method == BackgroundRemovalMethod.THRESHOLD:
            return await self._remove_background_threshold(image)
        elif method == BackgroundRemovalMethod.EDGE_DETECTION:
            return await self._remove_background_edges(image)
        elif method == BackgroundRemovalMethod.COLOR_ANALYSIS:
            return await self._remove_background_color_analysis(image)
        else:  # HYBRID
            return await self._remove_background_hybrid(image)
    
    async def _remove_background_threshold(self, image: Image.Image) -> Image.Image:
        """Remove background using simple thresholding."""
        
        # Convert to numpy array for processing
        img_array = np.array(image)
        
        # Assume white/light background
        # Create mask where pixels are not close to white
        threshold = 240  # Adjust based on needs
        
        # Calculate brightness of each pixel
        brightness = np.mean(img_array[:, :, :3], axis=2)
        
        # Create alpha mask
        alpha = np.where(brightness < threshold, 255, 0).astype(np.uint8)
        
        # Apply mask
        img_array[:, :, 3] = alpha
        
        return Image.fromarray(img_array, 'RGBA')
    
    async def _remove_background_edges(self, image: Image.Image) -> Image.Image:
        """Remove background using edge detection."""
        
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available, falling back to threshold method")
            return await self._remove_background_threshold(image)
        
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate edges to create regions
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create mask from largest contour (assumed to be logo)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros(gray.shape, np.uint8)
            cv2.fillPoly(mask, [largest_contour], 255)
            
            # Apply mask to alpha channel
            img_array[:, :, 3] = mask
        
        return Image.fromarray(img_array, 'RGBA')
    
    async def _remove_background_color_analysis(self, image: Image.Image) -> Image.Image:
        """Remove background using color analysis."""
        
        img_array = np.array(image)
        
        # Analyze corner pixels to determine background color
        corners = [
            img_array[0, 0, :3],      # top-left
            img_array[0, -1, :3],     # top-right
            img_array[-1, 0, :3],     # bottom-left
            img_array[-1, -1, :3]     # bottom-right
        ]
        
        # Find most common corner color (likely background)
        corner_colors = np.array(corners)
        background_color = np.mean(corner_colors, axis=0)
        
        # Calculate distance from background color
        distances = np.sqrt(np.sum((img_array[:, :, :3] - background_color) ** 2, axis=2))
        
        # Create mask based on distance threshold
        threshold = 30  # Adjust based on needs
        alpha = np.where(distances > threshold, 255, 0).astype(np.uint8)
        
        img_array[:, :, 3] = alpha
        
        return Image.fromarray(img_array, 'RGBA')
    
    async def _remove_background_hybrid(self, image: Image.Image) -> Image.Image:
        """Remove background using hybrid approach."""
        
        # Try multiple methods and combine results
        threshold_result = await self._remove_background_threshold(image)
        color_result = await self._remove_background_color_analysis(image)
        
        # Combine alpha channels (take intersection for more conservative removal)
        threshold_alpha = np.array(threshold_result)[:, :, 3]
        color_alpha = np.array(color_result)[:, :, 3]
        
        # Use minimum alpha (more conservative)
        combined_alpha = np.minimum(threshold_alpha, color_alpha)
        
        img_array = np.array(image)
        img_array[:, :, 3] = combined_alpha
        
        return Image.fromarray(img_array, 'RGBA')
    
    async def _enhance_contrast(self, image: Image.Image, 
                              level: ProcessingLevel) -> Image.Image:
        """Enhance image contrast."""
        
        enhancer = ImageEnhance.Contrast(image)
        
        if level == ProcessingLevel.MINIMAL:
            factor = 1.1
        elif level == ProcessingLevel.STANDARD:
            factor = 1.2
        else:  # AGGRESSIVE
            factor = 1.4
        
        return enhancer.enhance(factor)
    
    async def _sharpen_edges(self, image: Image.Image, 
                           level: ProcessingLevel) -> Image.Image:
        """Sharpen image edges."""
        
        if level == ProcessingLevel.MINIMAL:
            return image.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=3))
        elif level == ProcessingLevel.STANDARD:
            return image.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))
        else:  # AGGRESSIVE
            return image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=2))
    
    async def _normalize_colors(self, image: Image.Image) -> Image.Image:
        """Normalize image colors for better logo appearance."""
        
        # Auto-level the image
        image_rgb = image.convert('RGB')
        normalized = ImageOps.autocontrast(image_rgb, cutoff=0.1)
        
        # Restore alpha channel if it existed
        if image.mode == 'RGBA':
            alpha = image.split()[-1]
            normalized = normalized.convert('RGBA')
            normalized.putalpha(alpha)
        
        return normalized
    
    async def _optimize_for_vector(self, image: Image.Image) -> Image.Image:
        """Optimize image for vector conversion."""
        
        # Reduce noise while preserving edges
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Enhance edges slightly
        image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        return image
    
    async def _smart_resize(self, image: Image.Image, 
                          target_size: Tuple[int, int]) -> Image.Image:
        """Intelligently resize image maintaining aspect ratio and quality."""
        
        current_width, current_height = image.size
        target_width, target_height = target_size
        
        # Calculate scaling to fit within target size while maintaining aspect ratio
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        scale = min(scale_x, scale_y)
        
        new_width = int(current_width * scale)
        new_height = int(current_height * scale)
        
        # Use high-quality resampling
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    async def _cleanup_image(self, image: Image.Image, 
                           options: ProcessingOptions) -> Image.Image:
        """Final cleanup operations."""
        
        # Remove very small transparent regions (noise)
        if image.mode == 'RGBA':
            img_array = np.array(image)
            alpha = img_array[:, :, 3]
            
            # Remove pixels with very low alpha (likely noise)
            alpha = np.where(alpha < 50, 0, alpha)
            alpha = np.where(alpha > 200, 255, alpha)
            
            img_array[:, :, 3] = alpha
            image = Image.fromarray(img_array, 'RGBA')
        
        return image
    
    async def _calculate_quality_score(self, image: Image.Image, 
                                     original_size: Tuple[int, int]) -> float:
        """Calculate quality score for processed image."""
        
        score = 0.8  # Base score
        
        # Size factor
        if image.size[0] >= original_size[0] * 0.8 and image.size[1] >= original_size[1] * 0.8:
            score += 0.1  # Good size retention
        
        # Check if image has transparency (good for logos)
        if image.mode == 'RGBA':
            alpha_array = np.array(image.split()[-1])
            has_transparency = np.any(alpha_array < 255)
            if has_transparency:
                score += 0.1  # Transparency is good for logos
        
        return min(1.0, score)
    
    async def process_multiple_results(self, ai_results: List[AIGenerationResult],
                                     options: Optional[ProcessingOptions] = None) -> List[ProcessingResult]:
        """Process multiple AI results concurrently."""
        
        if options is None:
            options = ProcessingOptions()
        
        # Process all images concurrently
        tasks = [
            asyncio.create_task(self.process_ai_result(result, options))
            for result in ai_results
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process AI result {i}: {result}")
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_recommended_options(self, business_type: str, 
                              style: str = "modern") -> ProcessingOptions:
        """Get recommended processing options based on business type and style."""
        
        # Tech companies often need clean, sharp logos
        if "tech" in business_type.lower() or "software" in business_type.lower():
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=True,
                sharpen_edges=True,
                normalize_colors=True,
                optimize_for_vector=True,
                processing_level=ProcessingLevel.AGGRESSIVE,
                background_removal_method=BackgroundRemovalMethod.HYBRID
            )
        
        # Healthcare needs trustworthy, clean appearance
        elif "health" in business_type.lower() or "medical" in business_type.lower():
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=False,  # Softer approach
                sharpen_edges=False,
                normalize_colors=True,
                optimize_for_vector=True,
                processing_level=ProcessingLevel.STANDARD,
                background_removal_method=BackgroundRemovalMethod.COLOR_ANALYSIS
            )
        
        # Creative industries might want to preserve more artistic elements
        elif "creative" in business_type.lower() or "design" in business_type.lower():
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=False,
                sharpen_edges=False,
                normalize_colors=False,  # Preserve creative colors
                optimize_for_vector=False,
                processing_level=ProcessingLevel.MINIMAL,
                background_removal_method=BackgroundRemovalMethod.THRESHOLD
            )
        
        # Default for other business types
        else:
            return ProcessingOptions(
                remove_background=True,
                enhance_contrast=True,
                sharpen_edges=True,
                normalize_colors=True,
                optimize_for_vector=True,
                processing_level=ProcessingLevel.STANDARD,
                background_removal_method=BackgroundRemovalMethod.HYBRID
            )


# Global instance
image_processor = ImageProcessor()
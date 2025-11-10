"""
Base AI Provider Interface
Abstract base class for all AI image generation providers
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import time

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Custom exception for AI provider errors."""
    
    def __init__(self, message: str, provider: str, error_code: Optional[str] = None):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        super().__init__(f"[{provider}] {message}")


class GenerationStyle(Enum):
    """Logo generation style options."""
    MINIMALIST = "minimalist"
    MODERN = "modern"
    CLASSIC = "classic"
    PLAYFUL = "playful"
    BOLD = "bold"
    ELEGANT = "elegant"
    TECH = "tech"
    ORGANIC = "organic"


class ImageFormat(Enum):
    """Supported image output formats."""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


@dataclass
class LogoGenerationRequest:
    """Request for logo generation."""
    business_name: str
    business_type: str
    industry: str
    description: str = ""
    style: GenerationStyle = GenerationStyle.MODERN
    color_preferences: List[str] = field(default_factory=list)
    avoid_colors: List[str] = field(default_factory=list)
    include_text: bool = True
    preferred_layout: str = "balanced"  # balanced, horizontal, vertical, icon_only
    brand_personality: List[str] = field(default_factory=list)
    target_audience: str = "general"
    additional_requirements: str = ""
    size: str = "1024x1024"
    format: ImageFormat = ImageFormat.PNG


@dataclass
class AIGenerationResult:
    """Result of AI logo generation."""
    image_data: bytes
    format: ImageFormat
    size: tuple[int, int]
    provider: str
    model_used: str
    generation_time: float
    prompt_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0  # Provider's confidence in result quality
    cost_tokens: int = 0  # Approximate cost in tokens/credits
    
    def __post_init__(self):
        """Validate result after creation."""
        if not self.image_data:
            raise ValueError("Image data cannot be empty")
        if self.confidence_score < 0 or self.confidence_score > 1:
            raise ValueError("Confidence score must be between 0 and 1")


@dataclass 
class ProviderCapabilities:
    """Capabilities of an AI provider."""
    max_image_size: tuple[int, int]
    supported_formats: List[ImageFormat]
    supports_style_control: bool
    supports_color_control: bool
    supports_text_in_image: bool
    supports_batch_generation: bool
    max_batch_size: int = 1
    rate_limit_per_minute: int = 60
    estimated_cost_per_image: float = 0.0  # In USD
    

class BaseAIProvider(ABC):
    """Abstract base class for AI image generation providers."""
    
    def __init__(self, provider_name: str, api_key: Optional[str] = None):
        self.provider_name = provider_name
        self.api_key = api_key
        self.is_initialized = False
        self.last_request_time = 0.0
        self.request_count = 0
        self.rate_limit_reset_time = 0.0
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider. Returns True if successful."""
        pass
        
    @abstractmethod 
    def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities."""
        pass
        
    @abstractmethod
    async def generate_logo(self, request: LogoGenerationRequest) -> AIGenerationResult:
        """Generate a logo based on the request."""
        pass
        
    @abstractmethod
    async def generate_multiple_logos(self, request: LogoGenerationRequest, count: int = 3) -> List[AIGenerationResult]:
        """Generate multiple logo variations."""
        pass
        
    def is_available(self) -> bool:
        """Check if provider is available and initialized."""
        return self.is_initialized and self.api_key is not None
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the provider."""
        try:
            start_time = time.time()
            
            # Simple test request
            test_request = LogoGenerationRequest(
                business_name="Test",
                business_type="Technology",
                industry="tech",
                description="Health check test"
            )
            
            # Don't actually generate, just validate setup
            capabilities = self.get_capabilities()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "response_time": response_time,
                "capabilities": capabilities,
                "is_available": self.is_available()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "provider": self.provider_name,
                "error": str(e),
                "is_available": False
            }
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting for the provider."""
        capabilities = self.get_capabilities()
        current_time = time.time()
        
        # Reset rate limit counter if minute has passed
        if current_time - self.rate_limit_reset_time > 60:
            self.request_count = 0
            self.rate_limit_reset_time = current_time
            
        # Check if we've exceeded rate limit
        if self.request_count >= capabilities.rate_limit_per_minute:
            sleep_time = 60 - (current_time - self.rate_limit_reset_time)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached for {self.provider_name}, sleeping for {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_reset_time = time.time()
        
        self.request_count += 1
        self.last_request_time = current_time
    
    def _validate_request(self, request: LogoGenerationRequest) -> None:
        """Validate generation request against provider capabilities."""
        capabilities = self.get_capabilities()
        
        # Parse size
        try:
            width, height = map(int, request.size.split('x'))
            max_width, max_height = capabilities.max_image_size
            
            if width > max_width or height > max_height:
                raise AIProviderError(
                    f"Requested size {request.size} exceeds maximum {max_width}x{max_height}",
                    self.provider_name,
                    "SIZE_EXCEEDED"
                )
        except ValueError:
            raise AIProviderError(
                f"Invalid size format: {request.size}. Expected format: WIDTHxHEIGHT",
                self.provider_name,
                "INVALID_SIZE_FORMAT"
            )
        
        # Check format support
        if request.format not in capabilities.supported_formats:
            raise AIProviderError(
                f"Format {request.format.value} not supported. Supported: {[f.value for f in capabilities.supported_formats]}",
                self.provider_name,
                "UNSUPPORTED_FORMAT"
            )
        
        # Validate business name
        if not request.business_name or not request.business_name.strip():
            raise AIProviderError(
                "Business name cannot be empty",
                self.provider_name,
                "EMPTY_BUSINESS_NAME"
            )
            
        # Validate business type
        if not request.business_type or not request.business_type.strip():
            raise AIProviderError(
                "Business type cannot be empty", 
                self.provider_name,
                "EMPTY_BUSINESS_TYPE"
            )
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass
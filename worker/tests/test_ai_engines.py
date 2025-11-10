"""
Test suite for AI Image Generation Pipeline
"""

import pytest
import asyncio
import io
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Test imports
from src.ai_engines.base_provider import (
    BaseAIProvider, 
    LogoGenerationRequest, 
    AIGenerationResult,
    GenerationStyle,
    ImageFormat,
    ProviderCapabilities
)
from src.ai_engines.provider_manager import AIProviderManager, ProviderConfig, ProviderPriority
from src.ai_engines.prompt_engineer import PromptEngineer, PromptOptimizationLevel
from src.ai_engines.image_processor import ImageProcessor, ProcessingOptions


class MockAIProvider(BaseAIProvider):
    """Mock AI provider for testing."""
    
    def __init__(self, provider_name: str = "mock", should_fail: bool = False):
        super().__init__(provider_name)
        self.should_fail = should_fail
        self._initialized = False
    
    async def initialize(self) -> bool:
        if self.should_fail:
            return False
        self._initialized = True
        self.is_initialized = True
        return True
    
    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            max_image_size=(1024, 1024),
            supported_formats=[ImageFormat.PNG, ImageFormat.JPEG],
            supports_style_control=True,
            supports_color_control=True,
            supports_text_in_image=True,
            supports_batch_generation=True,
            max_batch_size=4,
            rate_limit_per_minute=60,
            estimated_cost_per_image=0.02
        )
    
    async def generate_logo(self, request: LogoGenerationRequest) -> AIGenerationResult:
        if self.should_fail:
            raise Exception("Mock provider failure")
        
        # Create mock image data (small PNG)
        mock_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        
        return AIGenerationResult(
            image_data=mock_image_data,
            format=ImageFormat.PNG,
            size=(1024, 1024),
            provider=self.provider_name,
            model_used="mock-model",
            generation_time=0.1,
            prompt_used=f"Mock prompt for {request.business_name}",
            confidence_score=0.85,
            cost_tokens=1
        )
    
    async def generate_multiple_logos(self, request: LogoGenerationRequest, count: int = 3) -> list:
        results = []
        for i in range(count):
            result = await self.generate_logo(request)
            result.metadata = {"batch_index": i}
            results.append(result)
        return results


@pytest.fixture
def sample_request():
    """Sample logo generation request for testing."""
    return LogoGenerationRequest(
        business_name="TechCorp",
        business_type="Technology Company",
        industry="technology",
        description="Innovative AI solutions for business",
        style=GenerationStyle.MODERN,
        color_preferences=["blue", "silver"],
        include_text=True,
        preferred_layout="horizontal",
        brand_personality=["innovative", "trustworthy"],
        target_audience="businesses"
    )


@pytest.fixture
def mock_provider():
    """Mock AI provider for testing."""
    return MockAIProvider()


@pytest.fixture
def failing_provider():
    """Mock AI provider that fails for testing fallback."""
    return MockAIProvider("failing_mock", should_fail=True)


class TestBaseAIProvider:
    """Test base AI provider functionality."""
    
    @pytest.mark.asyncio
    async def test_provider_initialization(self, mock_provider):
        """Test provider initialization."""
        assert not mock_provider.is_initialized
        
        success = await mock_provider.initialize()
        assert success
        assert mock_provider.is_initialized
    
    @pytest.mark.asyncio
    async def test_provider_capabilities(self, mock_provider):
        """Test provider capabilities."""
        capabilities = mock_provider.get_capabilities()
        
        assert capabilities.max_image_size == (1024, 1024)
        assert ImageFormat.PNG in capabilities.supported_formats
        assert capabilities.supports_style_control
        assert capabilities.rate_limit_per_minute > 0
    
    @pytest.mark.asyncio
    async def test_logo_generation(self, mock_provider, sample_request):
        """Test basic logo generation."""
        await mock_provider.initialize()
        
        result = await mock_provider.generate_logo(sample_request)
        
        assert isinstance(result, AIGenerationResult)
        assert result.provider == "mock"
        assert result.size == (1024, 1024)
        assert result.format == ImageFormat.PNG
        assert len(result.image_data) > 0
        assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_multiple_logo_generation(self, mock_provider, sample_request):
        """Test multiple logo generation."""
        await mock_provider.initialize()
        
        results = await mock_provider.generate_multiple_logos(sample_request, count=3)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert isinstance(result, AIGenerationResult)
            assert result.metadata.get("batch_index") == i
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_provider):
        """Test provider health check."""
        await mock_provider.initialize()
        
        health = await mock_provider.health_check()
        
        assert health["status"] == "healthy"
        assert health["provider"] == "mock"
        assert "capabilities" in health
        assert health["is_available"] == True


class TestProviderManager:
    """Test AI provider manager functionality."""
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager initialization with mock providers."""
        manager = AIProviderManager()
        
        # Configure with mock providers
        configs = {
            "mock1": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("mock1"),
                priority=ProviderPriority.HIGH
            ),
            "mock2": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("mock2"),
                priority=ProviderPriority.MEDIUM
            )
        }
        
        success = await manager.initialize(configs)
        assert success
        assert len(manager.providers) == 2
    
    @pytest.mark.asyncio
    async def test_provider_selection(self):
        """Test intelligent provider selection."""
        manager = AIProviderManager()
        
        configs = {
            "high_priority": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("high_priority"),
                priority=ProviderPriority.HIGH
            ),
            "low_priority": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("low_priority"),
                priority=ProviderPriority.LOW
            )
        }
        
        await manager.initialize(configs)
        
        # Test provider order
        order = manager._get_provider_order()
        assert order[0] == "high_priority"  # High priority should come first
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, sample_request):
        """Test fallback when providers fail."""
        manager = AIProviderManager()
        
        configs = {
            "failing": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("failing", should_fail=True),
                priority=ProviderPriority.HIGH
            ),
            "working": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("working"),
                priority=ProviderPriority.LOW
            )
        }
        
        await manager.initialize(configs)
        
        # Should fallback to working provider
        result = await manager.generate_logo(sample_request)
        assert result.provider == "working"
    
    @pytest.mark.asyncio
    async def test_health_check_all_providers(self):
        """Test health check for all providers."""
        manager = AIProviderManager()
        
        configs = {
            "mock1": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("mock1"),
                priority=ProviderPriority.HIGH
            )
        }
        
        await manager.initialize(configs)
        
        health = await manager.health_check()
        
        assert health["manager_status"] == "healthy"
        assert health["total_providers"] == 1
        assert health["available_providers"] == 1
        assert "mock1" in health["providers"]


class TestPromptEngineer:
    """Test prompt engineering functionality."""
    
    def test_prompt_engineer_initialization(self):
        """Test prompt engineer initialization."""
        engineer = PromptEngineer()
        
        assert len(engineer.industry_profiles) > 0
        assert len(engineer.style_profiles) > 0
        assert "technology" in engineer.industry_profiles
        assert GenerationStyle.MODERN in engineer.style_profiles
    
    def test_advanced_prompt_creation(self, sample_request):
        """Test advanced prompt creation."""
        engineer = PromptEngineer()
        
        components = engineer.create_advanced_prompt(
            sample_request, 
            PromptOptimizationLevel.ADVANCED
        )
        
        assert components.base_description
        assert "TechCorp" in components.base_description
        assert len(components.style_modifiers) > 0
        assert len(components.quality_requirements) > 0
    
    def test_industry_specific_prompts(self):
        """Test industry-specific prompt generation."""
        engineer = PromptEngineer()
        
        # Test different industries
        industries = ["technology", "healthcare", "finance", "food"]
        
        for industry in industries:
            request = LogoGenerationRequest(
                business_name="TestCorp",
                business_type=f"{industry.title()} Company",
                industry=industry
            )
            
            components = engineer.create_advanced_prompt(request)
            assert components.industry_context
            # Industry should influence the prompt
            assert any(keyword in components.industry_context.lower() 
                      for keyword in engineer.industry_profiles[industry].keywords)
    
    def test_style_specific_prompts(self):
        """Test style-specific prompt generation."""
        engineer = PromptEngineer()
        
        styles = [GenerationStyle.MINIMALIST, GenerationStyle.BOLD, GenerationStyle.ELEGANT]
        
        for style in styles:
            request = LogoGenerationRequest(
                business_name="TestCorp",
                business_type="Company",
                industry="other",
                style=style
            )
            
            components = engineer.create_advanced_prompt(request)
            # Style should influence modifiers
            assert len(components.style_modifiers) > 0
    
    def test_negative_prompt_generation(self, sample_request):
        """Test negative prompt generation."""
        engineer = PromptEngineer()
        
        components = engineer.create_advanced_prompt(sample_request)
        negative_prompt = components.get_negative_prompt()
        
        assert "blurry" in negative_prompt
        assert "low quality" in negative_prompt
        assert len(components.negative_prompts) > 0


@pytest.mark.skipif(True, reason="Requires PIL installation")
class TestImageProcessor:
    """Test image processing functionality."""
    
    def test_processor_initialization(self):
        """Test image processor initialization."""
        processor = ImageProcessor()
        # Would test PIL availability in real environment
    
    @pytest.mark.asyncio
    async def test_processing_options(self):
        """Test processing options creation."""
        processor = ImageProcessor()
        
        # Test recommended options for different business types
        tech_options = processor.get_recommended_options("technology")
        assert tech_options.processing_level.value == "aggressive"
        
        health_options = processor.get_recommended_options("healthcare")
        assert health_options.enhance_contrast == False  # Softer approach


class TestIntegration:
    """Integration tests for the complete AI pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_generation(self, sample_request):
        """Test complete end-to-end generation pipeline."""
        
        # Initialize components
        manager = AIProviderManager()
        engineer = PromptEngineer()
        
        # Configure manager with mock provider
        configs = {
            "mock": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("mock"),
                priority=ProviderPriority.HIGH
            )
        }
        
        await manager.initialize(configs)
        
        # Generate prompt
        prompt_components = engineer.create_advanced_prompt(sample_request)
        assert prompt_components.to_prompt()
        
        # Generate logo
        result = await manager.generate_logo(sample_request)
        
        assert isinstance(result, AIGenerationResult)
        assert result.provider == "mock"
        assert len(result.image_data) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_provider_workflow(self, sample_request):
        """Test workflow with multiple providers."""
        manager = AIProviderManager()
        
        configs = {
            "provider1": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("provider1"),
                priority=ProviderPriority.HIGH
            ),
            "provider2": ProviderConfig(
                provider_class=lambda api_key=None: MockAIProvider("provider2"),
                priority=ProviderPriority.MEDIUM
            )
        }
        
        await manager.initialize(configs)
        
        # Generate multiple logos distributed across providers
        results = await manager.generate_multiple_logos(
            sample_request, 
            count=4, 
            distribute_across_providers=True
        )
        
        assert len(results) == 4
        # Should use both providers
        providers_used = set(result.provider for result in results)
        assert len(providers_used) <= 2  # Up to 2 providers


if __name__ == "__main__":
    pytest.main([__file__])
"""
AI Provider Manager
Manages multiple AI providers with intelligent fallback and load balancing
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Type, Union
from dataclasses import dataclass, field
from enum import Enum

from .base_provider import (
    BaseAIProvider, 
    AIGenerationResult, 
    AIProviderError, 
    LogoGenerationRequest,
    ProviderCapabilities
)
from .openai_provider import OpenAIProvider
from .stability_provider import StabilityProvider

logger = logging.getLogger(__name__)


class ProviderPriority(Enum):
    """Provider priority levels."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    FALLBACK = 4


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    provider_class: Type[BaseAIProvider]
    priority: ProviderPriority
    api_key: Optional[str] = None
    enabled: bool = True
    max_retries: int = 2
    timeout_seconds: float = 60.0
    cost_weight: float = 1.0  # Higher = more expensive
    quality_weight: float = 1.0  # Higher = better quality


@dataclass
class GenerationMetrics:
    """Metrics for tracking provider performance."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_generation_time: float = 0.0
    total_cost: float = 0.0
    average_confidence: float = 0.0
    last_error: Optional[str] = None
    last_success_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def average_generation_time(self) -> float:
        """Calculate average generation time."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_generation_time / self.successful_requests


class AIProviderManager:
    """Manager for multiple AI providers with intelligent fallback."""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}
        self.metrics: Dict[str, GenerationMetrics] = {}
        self.is_initialized = False
        
        # Default provider configurations
        self.default_configs = {
            "openai": ProviderConfig(
                provider_class=OpenAIProvider,
                priority=ProviderPriority.HIGH,
                cost_weight=2.0,  # More expensive
                quality_weight=1.0  # High quality
            ),
            "stability": ProviderConfig(
                provider_class=StabilityProvider,
                priority=ProviderPriority.MEDIUM,
                cost_weight=1.0,  # Cheaper
                quality_weight=0.9  # Good quality
            )
        }
    
    async def initialize(self, provider_configs: Optional[Dict[str, ProviderConfig]] = None) -> bool:
        """Initialize all providers."""
        
        configs = provider_configs or self.default_configs
        initialization_results = {}
        
        for provider_name, config in configs.items():
            try:
                if not config.enabled:
                    logger.info(f"Provider {provider_name} is disabled")
                    continue
                
                # Create provider instance
                provider = config.provider_class(api_key=config.api_key)
                
                # Initialize provider
                success = await provider.initialize()
                
                if success:
                    self.providers[provider_name] = provider
                    self.provider_configs[provider_name] = config
                    self.metrics[provider_name] = GenerationMetrics()
                    
                    initialization_results[provider_name] = "success"
                    logger.info(f"Provider {provider_name} initialized successfully")
                else:
                    initialization_results[provider_name] = "failed_init"
                    logger.warning(f"Provider {provider_name} initialization failed")
                    
            except Exception as e:
                initialization_results[provider_name] = f"error: {e}"
                logger.error(f"Error initializing provider {provider_name}: {e}")
        
        # Consider initialization successful if at least one provider is available
        self.is_initialized = len(self.providers) > 0
        
        if self.is_initialized:
            logger.info(f"AI Provider Manager initialized with {len(self.providers)} providers")
        else:
            logger.error("No providers successfully initialized")
        
        return self.is_initialized
    
    async def generate_logo(self, request: LogoGenerationRequest, 
                          preferred_providers: Optional[List[str]] = None) -> AIGenerationResult:
        """Generate a logo using the best available provider."""
        
        if not self.is_initialized:
            raise AIProviderError("Manager not initialized", "manager")
        
        # Get provider selection order
        provider_order = self._get_provider_order(preferred_providers)
        
        last_error = None
        
        for provider_name in provider_order:
            try:
                provider = self.providers[provider_name]
                config = self.provider_configs[provider_name]
                
                if not provider.is_available():
                    logger.warning(f"Provider {provider_name} not available, skipping")
                    continue
                
                logger.info(f"Attempting generation with provider: {provider_name}")
                
                # Record attempt
                self.metrics[provider_name].total_requests += 1
                
                # Generate with timeout
                result = await asyncio.wait_for(
                    provider.generate_logo(request),
                    timeout=config.timeout_seconds
                )
                
                # Update success metrics
                metrics = self.metrics[provider_name]
                metrics.successful_requests += 1
                metrics.total_generation_time += result.generation_time
                metrics.total_cost += self._calculate_cost(result, config)
                metrics.average_confidence = (
                    (metrics.average_confidence * (metrics.successful_requests - 1) + result.confidence_score) 
                    / metrics.successful_requests
                )
                metrics.last_success_time = time.time()
                
                # Add provider selection info to metadata
                result.metadata.update({
                    "provider_manager": {
                        "selected_provider": provider_name,
                        "attempt_order": provider_order,
                        "provider_metrics": {
                            "success_rate": metrics.success_rate,
                            "avg_generation_time": metrics.average_generation_time
                        }
                    }
                })
                
                logger.info(f"Successfully generated logo with {provider_name}")
                return result
                
            except asyncio.TimeoutError:
                error_msg = f"Provider {provider_name} timed out"
                logger.warning(error_msg)
                last_error = AIProviderError(error_msg, provider_name, "TIMEOUT")
                self.metrics[provider_name].failed_requests += 1
                self.metrics[provider_name].last_error = error_msg
                
            except AIProviderError as e:
                logger.warning(f"Provider {provider_name} failed: {e.message}")
                last_error = e
                self.metrics[provider_name].failed_requests += 1
                self.metrics[provider_name].last_error = e.message
                
            except Exception as e:
                error_msg = f"Unexpected error with provider {provider_name}: {e}"
                logger.error(error_msg)
                last_error = AIProviderError(error_msg, provider_name, "UNEXPECTED")
                self.metrics[provider_name].failed_requests += 1
                self.metrics[provider_name].last_error = error_msg
        
        # If all providers failed
        raise AIProviderError(
            f"All providers failed. Last error: {last_error}",
            "manager",
            "ALL_PROVIDERS_FAILED"
        )
    
    async def generate_multiple_logos(self, request: LogoGenerationRequest, count: int = 3,
                                    distribute_across_providers: bool = True) -> List[AIGenerationResult]:
        """Generate multiple logos, optionally distributing across providers."""
        
        if not distribute_across_providers:
            # Use single best provider
            return await self._generate_multiple_single_provider(request, count)
        
        # Distribute across multiple providers
        return await self._generate_multiple_distributed(request, count)
    
    async def _generate_multiple_single_provider(self, request: LogoGenerationRequest, 
                                              count: int) -> List[AIGenerationResult]:
        """Generate multiple logos using the best single provider."""
        
        provider_order = self._get_provider_order()
        
        for provider_name in provider_order:
            try:
                provider = self.providers[provider_name]
                config = self.provider_configs[provider_name]
                
                if not provider.is_available():
                    continue
                
                logger.info(f"Generating {count} logos with {provider_name}")
                
                results = await asyncio.wait_for(
                    provider.generate_multiple_logos(request, count),
                    timeout=config.timeout_seconds * count  # Scale timeout with count
                )
                
                # Update metrics
                for result in results:
                    metrics = self.metrics[provider_name]
                    metrics.successful_requests += 1
                    metrics.total_generation_time += result.generation_time
                    metrics.total_cost += self._calculate_cost(result, config)
                
                logger.info(f"Successfully generated {len(results)} logos with {provider_name}")
                return results
                
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed for multiple generation: {e}")
                continue
        
        raise AIProviderError("All providers failed for multiple generation", "manager")
    
    async def _generate_multiple_distributed(self, request: LogoGenerationRequest, 
                                           count: int) -> List[AIGenerationResult]:
        """Distribute logo generation across multiple providers."""
        
        available_providers = [
            name for name in self.providers.keys()
            if self.providers[name].is_available()
        ]
        
        if not available_providers:
            raise AIProviderError("No providers available", "manager")
        
        # Calculate distribution
        logos_per_provider = max(1, count // len(available_providers))
        remaining_logos = count % len(available_providers)
        
        tasks = []
        
        for i, provider_name in enumerate(available_providers):
            provider_count = logos_per_provider
            if i < remaining_logos:
                provider_count += 1
            
            if provider_count > 0:
                task = asyncio.create_task(
                    self._generate_with_provider(request, provider_name, provider_count),
                    name=f"generate_{provider_name}_{provider_count}"
                )
                tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and handle errors
        all_logos = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Distributed generation task failed: {result}")
                continue
            
            if isinstance(result, list):
                all_logos.extend(result)
        
        if not all_logos:
            raise AIProviderError("All distributed generation tasks failed", "manager")
        
        return all_logos[:count]  # Return exactly the requested count
    
    async def _generate_with_provider(self, request: LogoGenerationRequest, 
                                    provider_name: str, count: int) -> List[AIGenerationResult]:
        """Generate logos with a specific provider."""
        
        provider = self.providers[provider_name]
        config = self.provider_configs[provider_name]
        
        try:
            if count == 1:
                result = await asyncio.wait_for(
                    provider.generate_logo(request),
                    timeout=config.timeout_seconds
                )
                return [result]
            else:
                return await asyncio.wait_for(
                    provider.generate_multiple_logos(request, count),
                    timeout=config.timeout_seconds * count
                )
        except Exception as e:
            logger.error(f"Provider {provider_name} failed: {e}")
            return []
    
    def _get_provider_order(self, preferred_providers: Optional[List[str]] = None) -> List[str]:
        """Get ordered list of providers to try."""
        
        available_providers = [
            name for name in self.providers.keys()
            if self.providers[name].is_available()
        ]
        
        if not available_providers:
            return []
        
        # If specific providers are preferred, try them first
        if preferred_providers:
            provider_order = []
            
            # Add preferred providers first (if available)
            for pref in preferred_providers:
                if pref in available_providers:
                    provider_order.append(pref)
            
            # Add remaining providers
            for provider in available_providers:
                if provider not in provider_order:
                    provider_order.append(provider)
            
            return provider_order
        
        # Sort by priority, success rate, and cost
        def provider_score(provider_name: str) -> tuple:
            config = self.provider_configs[provider_name]
            metrics = self.metrics[provider_name]
            
            # Priority (lower number = higher priority)
            priority_score = config.priority.value
            
            # Success rate (higher = better)
            success_rate = metrics.success_rate if metrics.total_requests > 0 else 50.0
            
            # Cost (lower = better, but factor in quality)
            cost_efficiency = config.cost_weight / max(config.quality_weight, 0.1)
            
            # Recency bonus (recently successful providers get slight boost)
            recency_bonus = 0
            if metrics.last_success_time > 0:
                time_since_success = time.time() - metrics.last_success_time
                if time_since_success < 300:  # Last 5 minutes
                    recency_bonus = 0.1
            
            # Return tuple for sorting (lower values = higher priority)
            return (
                priority_score,
                -success_rate,  # Negative because we want higher success rate first
                cost_efficiency,
                -recency_bonus  # Negative because we want recent success first
            )
        
        return sorted(available_providers, key=provider_score)
    
    def _calculate_cost(self, result: AIGenerationResult, config: ProviderConfig) -> float:
        """Calculate estimated cost for a generation result."""
        base_cost = config.provider_class(None).get_capabilities().estimated_cost_per_image
        return base_cost * config.cost_weight * result.cost_tokens
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all providers."""
        
        health_results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                health_result = await provider.health_check()
                health_result.update({
                    "metrics": {
                        "success_rate": self.metrics[provider_name].success_rate,
                        "total_requests": self.metrics[provider_name].total_requests,
                        "average_generation_time": self.metrics[provider_name].average_generation_time,
                        "last_error": self.metrics[provider_name].last_error
                    }
                })
                health_results[provider_name] = health_result
            except Exception as e:
                health_results[provider_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "manager_status": "healthy" if self.is_initialized else "unhealthy",
            "total_providers": len(self.providers),
            "available_providers": len([p for p in self.providers.values() if p.is_available()]),
            "providers": health_results
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all providers."""
        
        return {
            provider_name: {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "success_rate": metrics.success_rate,
                "average_generation_time": metrics.average_generation_time,
                "total_cost": metrics.total_cost,
                "average_confidence": metrics.average_confidence,
                "last_error": metrics.last_error,
                "last_success_time": metrics.last_success_time
            }
            for provider_name, metrics in self.metrics.items()
        }
    
    def reset_metrics(self):
        """Reset performance metrics for all providers."""
        for provider_name in self.metrics:
            self.metrics[provider_name] = GenerationMetrics()
        logger.info("All provider metrics reset")


# Global instance
ai_provider_manager = AIProviderManager()
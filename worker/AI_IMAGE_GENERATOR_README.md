# AI Image Generator for Logo Studio

Advanced logo generation system using AI models (DALL-E 3, Stable Diffusion) with intelligent fallback mechanism and image post-processing.

## 🚀 Key Features

- **Multiple AI providers**: OpenAI DALL-E 3, Stability AI
- **Intelligent fallback**: Automatic switching between providers
- **Advanced prompt engineering**: Industry-specific prompts
- **Image post-processing**: Background removal, quality enhancement
- **Scalable architecture**: Easy to add new AI providers

## 🏗️ Architecture

```
ai_engines/
├── base_provider.py          # Base interface for AI providers  
├── openai_provider.py        # OpenAI DALL-E 3 integration
├── stability_provider.py     # Stability AI integration
├── provider_manager.py       # Manager with fallback logic
├── prompt_engineer.py        # Advanced prompt engineering
└── image_processor.py        # Image post-processing
```

## 🛠️ Installation and Setup

### 1. Install Dependencies

```bash
cd worker
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# .env file or environment variables
export OPENAI_API_KEY="your-openai-api-key"
export STABILITY_API_KEY="your-stability-api-key"
```

### 3. System Initialization

```python
from src.ai_logo_generator_integration import ai_logo_generator

# Initialize
success = await ai_logo_generator.initialize()
if success:
    print("AI Logo Generator is ready to use!")
```

## 💻 Usage

### Basic Logo Generation

```python
from src.ai_engines import GenerationStyle

# Generate single logo
result = await ai_logo_generator.generate_single_logo(
    business_name="TechCorp",
    business_type="Technology Company", 
    industry="technology",
    description="AI solutions for business",
    style=GenerationStyle.MODERN,
    color_preferences=["blue", "silver"],
    brand_personality=["innovative", "trustworthy"]
)

# Result contains:
# - result["ai_result"]["image_data"] - image bytes
# - result["processed_result"] - processed image  
# - result["quality_metrics"] - quality metrics
```

### Multiple Variants Generation

```python
# Generate multiple variants distributed across providers
variants = await ai_logo_generator.generate_logo_variants(
    business_name="HealthCare Plus",
    business_type="Healthcare Provider",
    industry="healthcare", 
    description="Premium healthcare services",
    style=GenerationStyle.ELEGANT,
    count=6,
    preferred_providers=["openai", "stability"]
)

# Each variant contains complete generation information
for i, variant in enumerate(variants):
    print(f"Variant {i+1}: {variant['ai_result']['provider']}")
```

## 🎨 Supported Styles

- `MINIMALIST` - Clean, minimalist design
- `MODERN` - Contemporary, technological style  
- `CLASSIC` - Classic, timeless design
- `PLAYFUL` - Playful, creative style
- `BOLD` - Bright, impactful design
- `ELEGANT` - Refined, premium style
- `TECH` - Technological, futuristic
- `ORGANIC` - Natural, eco-friendly

## 🏭 Industry Profiles

The system automatically adapts prompts for different industries:

- **Technology** - Innovation, digital solutions, neural networks
- **Healthcare** - Care, trust, medical symbolism  
- **Finance** - Stability, growth, premium quality
- **Food** - Freshness, quality, appetizing appeal
- **Creative** - Artistry, inspiration, creativity
- **Retail** - Lifestyle, consumer appeal
- **Education** - Knowledge, development, academic excellence
- **Consulting** - Expertise, professionalism, solutions

## ⚙️ Provider Configuration

```python
from src.ai_engines import ProviderConfig, ProviderPriority

custom_configs = {
    "openai": ProviderConfig(
        provider_class=OpenAIProvider,
        priority=ProviderPriority.HIGH,
        api_key="your-key",
        cost_weight=2.0,      # Более дорогой
        quality_weight=1.0,   # Высокое качество
        timeout_seconds=90.0
    ),
    "stability": ProviderConfig(
        provider_class=StabilityProvider, 
        priority=ProviderPriority.MEDIUM,
        api_key="your-key",
        cost_weight=1.0,      # Дешевле
        quality_weight=0.9,   # Хорошее качество
        timeout_seconds=120.0
    )
}

await ai_logo_generator.initialize(custom_configs)
```

## 🔧 Постобработка изображений

```python
from src.ai_engines import ProcessingOptions, ProcessingLevel

# Настройки обработки
processing_options = ProcessingOptions(
    remove_background=True,           # Удаление фона
    enhance_contrast=True,            # Улучшение контраста
    sharpen_edges=True,              # Заострение краев
    normalize_colors=True,           # Нормализация цветов
    optimize_for_vector=True,        # Оптимизация для векторизации
    processing_level=ProcessingLevel.AGGRESSIVE
)

# Применяется автоматически при генерации
variants = await ai_logo_generator.generate_logo_variants(
    # ... parameters ...
    processing_options=processing_options
)
```

## 📊 Мониторинг и метрики

```python
# Проверка статуса системы
status = await ai_logo_generator.get_system_status()

print(f"Статус: {status['status']}")
print(f"Доступных провайдеров: {status['providers']['available']}")

# Метрики производительности
for provider, metrics in status['providers']['metrics'].items():
    print(f"{provider}: {metrics['success_rate']:.1f}% успешность")
```

## 🧪 Тестирование

```bash
# Запуск тестов
cd worker
python -m pytest tests/test_ai_engines.py -v

# Тесты включают:
# - Инициализацию провайдеров
# - Fallback механизм  
# - Prompt engineering
# - Обработку изображений
# - End-to-end интеграцию
```

## 🚦 Fallback стратегия

Система автоматически обеспечивает надежность через:

1. **Приоритезация провайдеров** по качеству и стоимости
2. **Автоматический fallback** при сбоях
3. **Мониторинг успешности** запросов
4. **Rate limiting** для соблюдения лимитов API
5. **Timeout handling** для избежания зависаний

```python
# Пример fallback последовательности:
# 1. OpenAI DALL-E 3 (высокий приоритет)
# 2. Stability AI (средний приоритет)  
# 3. Programmatic fallback (legacy система)
```

## 🔐 Безопасность и лимиты

- **Rate limiting** - автоматическое соблюдение лимитов API
- **API key безопасность** - ключи загружаются из environment
- **Timeout protection** - защита от зависших запросов
- **Error handling** - graceful обработка ошибок
- **Cost tracking** - отслеживание затрат на генерацию

## 🎯 Лучшие практики

### Для максимального качества:

```python
# Используйте детальные описания
description = "Innovative AI company specializing in computer vision and machine learning solutions for healthcare industry"

# Указывайте специфичные цвета
color_preferences = ["#0066CC", "#4A90E2", "#FFFFFF"] 

# Определяйте личность бренда
brand_personality = ["innovative", "trustworthy", "premium", "caring"]

# Используйте продвинутую оптимизацию
optimization_level = PromptOptimizationLevel.PREMIUM
```

### Для экономии ресурсов:

```python
# Предпочитайте более дешевые провайдеры
preferred_providers = ["stability"]

# Используйте batch генерацию
variants = await generate_logo_variants(count=6, distribute_across_providers=True)

# Настройте таймауты
timeout_seconds = 60.0  # Вместо 120.0
```

## 📈 Производительность

**Типичные времена генерации:**

- OpenAI DALL-E 3: ~15-30 секунд
- Stability AI: ~20-45 секунд  
- Постобработка: ~2-5 секунд
- **Общее время**: 20-50 секунд на логотип

**Масштабирование:**

- Параллельная генерация нескольких вариантов
- Распределение нагрузки между провайдерами
- Кэширование промптов и настроек
- Асинхронная обработка

## 🔄 Интеграция с существующей системой

Для интеграции с текущим `consumer.py`:

```python
# В consumer.py
from src.ai_logo_generator_integration import ai_logo_generator
from src.ai_engines import GenerationStyle, ProcessingOptions

async def process_with_ai(payload: dict):
    """Updated processing function with AI."""
    
    job_id = payload["job_id"]
    business_type = payload.get("business_type", "business")
    prefs = payload.get("prefs", {})
    
    # Инициализация AI (если еще не сделано)
    if not ai_logo_generator.is_initialized:
        await ai_logo_generator.initialize()
    
    # Generation parameters
    business_name = prefs.get('business_name', business_type.split(' - ')[0])
    description = prefs.get('description', f"A {business_type} business")
    
    # Генерация вариантов
    variants = await ai_logo_generator.generate_logo_variants(
        business_name=business_name,
        business_type=business_type,
        industry=determine_industry(business_type),  # Industry determination function
        description=description,
        style=map_style_preference(prefs.get('style', 'modern')),  # Маппинг стиля
        color_preferences=prefs.get('colors', []),
        count=3
    )
    
    # Сохранение результатов
    for i, variant in enumerate(variants):
        # Используем обработанное изображение если доступно
        image_data = (variant.get("processed_result", {}).get("processed_image") or 
                     variant["ai_result"]["image_data"])
        
        key = f"jobs/{job_id}/v{i:02d}_ai_{variant['ai_result']['provider']}.png"
        upload_svg(key, image_data)  # Обновить для PNG
        
        # Создание palette из AI результата
        palette = extract_palette_from_variant(variant)
        await insert_variant(job_id, i, palette, key)
```

## 🚨 Обработка ошибок

```python
try:
    result = await ai_logo_generator.generate_single_logo(...)
except RuntimeError as e:
    logger.error(f"Initialization error: {e}")
    # Fallback к legacy системе
except Exception as e:
    logger.error(f"AI generation failed: {e}")
    # Fallback к programmatic генерации
```

## 📋 TODO / Roadmap

- [ ] Поддержка локальных Stable Diffusion моделей
- [ ] Векторизация (PNG → SVG) через potrace/autotrace
- [ ] Design System генерация (цвета, типографика, компоненты)
- [ ] Batch API для множественных запросов  
- [ ] Кэширование результатов
- [ ] A/B тестирование промптов
- [ ] Интеграция с Midjourney API
- [ ] Поддержка видео логотипов

---

## 🤝 Contributing

1. Добавление нового AI провайдера:
   - Наследуйтесь от `BaseAIProvider`
   - Реализуйте все абстрактные методы
   - Добавьте конфигурацию в `AIProviderManager`

2. Улучшение prompt engineering:
   - Обновите `industry_profiles` в `PromptEngineer`
   - Добавьте новые `style_prompts`
   - Протестируйте качество результатов

3. Обработка изображений:
   - Добавьте новые методы в `ImageProcessor`
   - Учитывайте различные форматы входных данных
   - Тестируйте производительность

**Результат:** Полноценный AI Image Generator готов к использованию! 🎉
# AI Logo Studio Worker 🔧

This is the **background processing worker** for AI Logo Studio. It consumes logo generation jobs from Kafka queue and generates multiple logo variants using AI algorithms.

## 🚀 Features

- **Kafka Consumer** - Processes jobs from `logo.requests` topic
- **Logo Generation** - Creates 6 unique logo variants per job
- **Multiple Palettes** - Generates warm, cool, and monochrome color schemes
- **S3 Upload** - Stores generated SVG files in S3-compatible storage
- **Database Updates** - Persists generation results and metadata
- **Error Handling** - Robust error handling with job status updates
- **Scalability** - Multiple workers can run in parallel

## 🛠️ Tech Stack

- **Python 3.11** - Runtime environment
- **aiokafka** - Async Kafka consumer
- **SQLAlchemy** - Database ORM with async support
- **boto3** - AWS S3 client for file storage
- **AsyncPG** - PostgreSQL async driver

## 🏗️ Project Structure

```
worker/
├── src/
│   └── consumer.py         # Main worker implementation
├── requirements.txt        # Python dependencies
└── Dockerfile             # Container configuration
```

## ⚡ How It Works

### 1. Message Consumption

The worker listens to the `logo.requests` Kafka topic:

```python
async for msg in consumer:
    job_data = json.loads(msg.value.decode())
    job_id = job_data["job_id"]
    business_type = job_data["business_type"] 
    preferences = job_data["prefs"]
    
    await process_job(job_id, business_type, preferences)
```

### 2. Logo Generation Process

For each job, the worker generates 6 logo variants:

```python
# Color palettes
palettes = [
    ("warm", ["#FF6B6B", "#FFD93D", "#FFA552", "#2C2C2C"]),
    ("cool", ["#4D96FF", "#6BCB77", "#3D5AF1", "#222222"]),
    ("mono", ["#111111", "#555555", "#999999", "#FFFFFF"])
]

# Generate 2 variants per palette = 6 total
for palette_name, colors in palettes:
    for i in range(2):
        svg_content = generate_logo_svg(business_type, colors, preferences)
        # Save to S3 and database
```

### 3. SVG Generation Algorithm

The worker creates professional SVG logos with:

- **Business initials** extracted from business type
- **Dynamic sizing** based on content
- **Color application** from selected palette
- **Typography** with appropriate font sizing
- **Geometric shapes** (circles, rectangles) for visual appeal

### 4. File Storage

Generated SVGs are uploaded to S3 with structured keys:

```
s3://ai-logo-studio/jobs/{job_id}/v{index:02d}_{palette}.svg

Examples:
- jobs/12345.../v00_warm.svg
- jobs/12345.../v01_warm.svg  
- jobs/12345.../v02_cool.svg
- jobs/12345.../v03_cool.svg
- jobs/12345.../v04_mono.svg
- jobs/12345.../v05_mono.svg
```

### 5. Database Updates

Results are persisted in PostgreSQL:

```sql
-- Update job status
UPDATE jobs SET status = 'done' WHERE id = ?

-- Insert logo variants
INSERT INTO logo_variants (job_id, index, palette, svg_key) VALUES ...
```

## 🔧 Configuration

### Environment Variables

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Database Configuration  
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/appdb

# S3 Configuration
S3_ENDPOINT_URL=http://localstack:4566
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
S3_BUCKET=ai-logo-studio
```

### Kafka Consumer Settings

```python
consumer = AIOKafkaConsumer(
    "logo.requests",
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id="logo-workers",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode())
)
```

## 🚀 Running the Worker

### Docker (Recommended)

```bash
# Start all services including worker
docker-compose up --build -d

# Start only worker (requires DB, Kafka, S3)
docker-compose up worker -d

# View worker logs
docker-compose logs worker -f

# Scale workers for parallel processing
docker-compose up worker --scale worker=3 -d
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export KAFKA_BOOTSTRAP_SERVERS="localhost:29092"
export DATABASE_URL="postgresql+asyncpg://app:app@localhost:5432/appdb"
export S3_ENDPOINT_URL="http://localhost:4566"
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"  
export S3_BUCKET="ai-logo-studio"

# Run worker
cd worker
python -m src.consumer
```

## 📊 Monitoring

### Worker Logs

```bash
# View real-time logs
docker-compose logs worker -f

# Sample log output:
[worker] starting; kafka=kafka:9092 db=postgresql+asyncpg://app:app@db:5432/appdb
[worker] consumer started, waiting messages…
[worker] processing job 73831643-6ce8-42e6-aa50-0e9da805cc53
[worker] job 73831643-6ce8-42e6-aa50-0e9da805cc53 done, 6 variants uploaded
```

### Kafka Topic Monitoring

```bash
# List topics
docker-compose exec kafka kafka-topics --bootstrap-server kafka:9092 --list

# Monitor topic messages
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server kafka:9092 \
  --topic logo.requests \
  --from-beginning
```

### Database Monitoring

```bash
# Check job status
docker-compose exec db psql -U app -d appdb -c \
  "SELECT id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 5;"

# Check generated variants
docker-compose exec db psql -U app -d appdb -c \
  "SELECT job_id, index, palette->>'name' as palette_name FROM logo_variants;"
```

## 🎨 Logo Generation Details

### Business Type Processing

The worker extracts meaningful initials from business types:

```python
def extract_initials(business_type: str) -> str:
    # "tech startup" -> "TS" 
    # "restaurant" -> "R"
    # "e-commerce store" -> "ES"
    words = business_type.upper().split()
    if len(words) >= 2:
        return words[0][0] + words[1][0]  
    else:
        return words[0][:2]
```

### Color Palette Application

Each palette creates distinct visual styles:

- **Warm Palette**: `#FF6B6B`, `#FFD93D`, `#FFA552`, `#2C2C2C`
  - Energetic, friendly, creative brands
- **Cool Palette**: `#4D96FF`, `#6BCB77`, `#3D5AF1`, `#222222`  
  - Professional, trustworthy, tech-focused
- **Mono Palette**: `#111111`, `#555555`, `#999999`, `#FFFFFF`
  - Minimalist, elegant, timeless design

### SVG Structure

Generated SVGs follow a consistent structure:

```xml
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect fill="#FFFFFF" width="512" height="512"/>
  
  <!-- Main shape (circle/rectangle) -->
  <circle cx="256" cy="215" fill="{primary_color}" r="112"/>
  
  <!-- Business initials -->
  <text x="50%" y="235" fill="{text_color}" 
        font-family="Arial" font-size="92" text-anchor="middle">
    {initials}
  </text>
  
  <!-- Business type label -->  
  <text x="50%" y="399" fill="{secondary_color}"
        font-family="Arial" font-size="36" text-anchor="middle">
    {business_type}
  </text>
</svg>
```

## 🔄 Scaling & Performance

### Horizontal Scaling

Multiple workers can process jobs in parallel:

```bash
# Run 5 worker instances
docker-compose up worker --scale worker=5 -d
```

### Performance Characteristics

- **Processing Time**: ~1-2 seconds per job (6 variants)
- **Throughput**: 30-60 jobs/minute per worker
- **Memory Usage**: ~50MB per worker instance  
- **S3 Upload**: ~6KB per SVG file (minimal bandwidth)

### Error Handling

The worker implements robust error handling:

```python
try:
    await process_job(job_id, business_type, preferences)
    await update_job_status(job_id, "done")
except Exception as e:
    logger.error(f"Job {job_id} failed: {e}")
    await update_job_status(job_id, "error") 
```

## 🧪 Testing

### Manual Testing

```bash
# Create a test job via API
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"business_type": "test company", "preferences": {}}'

# Monitor worker logs
docker-compose logs worker -f

# Check results
curl http://localhost:8000/api/result/{job_id}
```

### Load Testing

```bash
# Generate multiple jobs quickly
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/generate \
    -H "Content-Type: application/json" \
    -d "{\"business_type\": \"company $i\", \"preferences\": {}}"
done

# Monitor processing
docker-compose logs worker -f
```

## 🚀 Deployment

### Production Considerations

1. **Resource Allocation**: 
   - CPU: 0.5-1 core per worker
   - Memory: 100-200MB per worker
   
2. **Scaling Strategy**:
   - Monitor queue depth in Kafka
   - Scale workers based on processing lag
   - Use Kubernetes HPA for auto-scaling

3. **Error Monitoring**:
   - Implement structured logging
   - Add metrics collection (Prometheus)
   - Set up alerting for failed jobs

4. **Data Persistence**:
   - Use persistent Kafka topics
   - Ensure S3 bucket has proper retention
   - Regular database backups

### Container Optimization

```dockerfile
# Multi-stage build for smaller images
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ /app/src/
WORKDIR /app
CMD ["python", "-m", "src.consumer"]
```

## 🤝 Contributing

1. **Code Style**: Follow PEP 8 guidelines
2. **Error Handling**: Add proper try/catch blocks
3. **Logging**: Use structured logging with context
4. **Testing**: Add unit tests for generation logic
5. **Documentation**: Update docstrings and comments

## 📚 Learn More

- [aiokafka Documentation](https://aiokafka.readthedocs.io/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [SVG Specification](https://www.w3.org/TR/SVG2/)

---

Part of the **AI Logo Studio** project. See main [README](../README.md) for full project documentation.
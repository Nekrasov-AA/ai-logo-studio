# AI Logo Studio Backend 🚀

This is the **backend API server** for AI Logo Studio, built with FastAPI. It provides REST endpoints for logo generation, manages job queues via Kafka, and handles data persistence with PostgreSQL.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Async/Await** - Full asynchronous support for high performance
- **PostgreSQL** - Reliable data persistence with SQLAlchemy ORM
- **Kafka Integration** - Message queue for asynchronous processing
- **S3 Storage** - File storage with presigned URL generation
- **Auto-generated API docs** - Interactive documentation with Swagger UI
- **Database migrations** - Version-controlled schema changes with Alembic
- **Health checks** - Service monitoring and status endpoints

## 🛠️ Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - Database ORM with async support
- **Alembic** - Database migration tool
- **AsyncPG** - PostgreSQL async driver
- **aiokafka** - Async Kafka client
- **boto3** - AWS S3 client
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/                 # REST API endpoints
│   │   ├── routes_generate.py  # Logo generation endpoints
│   │   └── routes_progress.py  # Progress tracking (SSE)
│   ├── core/                # Core modules
│   │   ├── db.py           # Database configuration
│   │   ├── kafka.py        # Kafka producer/consumer
│   │   ├── s3.py          # S3 storage operations
│   │   └── settings.py     # Application settings
│   ├── models/             # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py        # Base model class
│   │   ├── job.py         # Job model
│   │   ├── user.py        # User model
│   │   └── variant.py     # Logo variant model
│   └── schemas/            # Pydantic schemas
│       └── job.py         # Job request/response schemas
├── alembic/               # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/          # Migration files
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
└── Dockerfile           # Container configuration
```

## 🔧 Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Apache Kafka
- LocalStack (for S3 emulation)

### Local Development

**Option 1: Docker (Recommended)**
```bash
# From project root
docker-compose up --build -d

# Apply migrations
docker-compose exec backend alembic upgrade head
```

**Option 2: Virtual Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://app:app@localhost:5432/appdb"
export KAFKA_BOOTSTRAP_SERVERS="localhost:29092"
export S3_ENDPOINT_URL="http://localhost:4566"

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 API Endpoints

### Logo Generation

#### Create Generation Job
```http
POST /api/generate
Content-Type: application/json

{
  "business_type": "tech startup",
  "preferences": {
    "style": "modern",
    "theme": "minimalist",
    "color": "blue"
  }
}
```

**Response:**
```json
{
  "job_id": "73831643-6ce8-42e6-aa50-0e9da805cc53",
  "status": "queued"
}
```

#### Get Generation Results
```http
GET /api/result/{job_id}
```

**Response:**
```json
{
  "job_id": "73831643-6ce8-42e6-aa50-0e9da805cc53",
  "status": "done",
  "variants": [
    {
      "index": 0,
      "palette": {
        "name": "warm",
        "colors": ["#FF6B6B", "#FFD93D", "#FFA552", "#2C2C2C"]
      },
      "svg": {
        "s3_key": "jobs/.../v00_warm.svg",
        "url": "http://localhost:4566/..."
      }
    }
  ]
}
```

#### Progress Tracking (SSE)
```http
GET /api/progress/{job_id}
Accept: text/event-stream
```

**Response Stream:**
```
data: {"status": "queued", "progress": 0}

data: {"status": "processing", "progress": 50}

data: {"status": "done", "progress": 100}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok"
}
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🗄️ Database Models

### Job Model
```python
class Job(Base):
    id: UUID
    user_id: UUID | None
    business_type: str
    prefs: Dict[str, Any]  # JSON preferences
    status: str  # queued, processing, done, error
    result_svg_key: str | None
    created_at: datetime
    updated_at: datetime
```

### LogoVariant Model
```python
class LogoVariant(Base):
    id: UUID
    job_id: UUID  # Foreign key to Job
    index: int
    palette: Dict[str, Any]  # Color palette info
    svg_key: str  # S3 object key
    created_at: datetime
```

### User Model
```python
class User(Base):
    id: UUID
    email: str
    created_at: datetime
    updated_at: datetime
```

## 🔄 Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
docker-compose exec backend alembic revision --autogenerate -m "Add new field"

# Create empty migration
docker-compose exec backend alembic revision -m "Custom migration"
```

### Applying Migrations

```bash
# Apply all pending migrations
docker-compose exec backend alembic upgrade head

# Apply specific migration
docker-compose exec backend alembic upgrade <revision_id>

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### Migration History

```bash
# Show migration history
docker-compose exec backend alembic history

# Show current revision
docker-compose exec backend alembic current
```

## 📡 Kafka Integration

### Message Producer

The API publishes logo generation jobs to Kafka:

```python
# In routes_generate.py
msg = {
    "job_id": str(job.id),
    "user_id": None,
    "business_type": job.business_type,
    "prefs": job.prefs,
}
producer = get_producer()
await producer.send_and_wait("logo.requests", msg)
```

### Topics Used

- `logo.requests` - Logo generation job requests

## 💾 S3 Storage

### File Operations

```python
# Upload file to S3
await upload_to_s3(file_content, s3_key)

# Generate presigned download URL
url = presigned_get_url(s3_key, expires_in=3600)

# Ensure bucket exists
ensure_bucket()
```

### S3 Configuration

- **Endpoint**: LocalStack (http://localhost:4566)
- **Bucket**: `ai-logo-studio`
- **Path Structure**: `jobs/{job_id}/v{index}_{palette}.svg`

## ⚙️ Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/appdb

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# S3 Storage
S3_ENDPOINT_URL=http://localstack:4566
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
S3_BUCKET=ai-logo-studio
S3_PUBLIC_BASE=http://localhost:4566  # For presigned URLs
```

### Settings Module

Configuration is managed in `app/core/settings.py` using Pydantic BaseSettings:

```python
class Settings(BaseSettings):
    database_url: str
    kafka_bootstrap_servers: str
    s3_endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    s3_bucket: str
    
    class Config:
        env_file = ".env"
```

## 🧪 Testing

### Manual API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Create generation job
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"business_type": "tech startup", "preferences": {"style": "modern"}}'

# Check job result
curl http://localhost:8000/api/result/{job_id}
```

### Database Testing

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U app -d appdb

# List tables
\dt

# Query jobs
SELECT * FROM jobs;

# Query variants
SELECT * FROM logo_variants;
```

## 🚀 Deployment

### Docker Build

```bash
# Build production image
docker build -t ai-logo-studio-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e KAFKA_BOOTSTRAP_SERVERS="kafka:9092" \
  ai-logo-studio-backend
```

### Production Considerations

1. **Database Connection Pool**: Configure SQLAlchemy pool size
2. **Kafka Reliability**: Use persistent topics and proper error handling
3. **S3 Security**: Use proper AWS IAM roles in production
4. **Monitoring**: Add structured logging and metrics
5. **Rate Limiting**: Implement API rate limiting
6. **Authentication**: Add JWT or similar auth mechanism

## 📊 Monitoring

### Logs

```bash
# Application logs
docker-compose logs backend -f

# Database logs
docker-compose logs db

# Kafka logs
docker-compose logs kafka
```

### Health Checks

The application includes health checks for:
- Database connectivity
- Kafka producer status
- S3 bucket accessibility

## 🔧 Development Commands

```bash
# Start only backend services
docker-compose up db kafka localstack -d

# Restart backend after code changes
docker-compose restart backend

# Run alembic commands
docker-compose exec backend alembic <command>

# Access backend container shell
docker-compose exec backend bash

# View real-time logs
docker-compose logs backend -f
```

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Use type hints for all functions
3. Write docstrings for public methods
4. Add proper error handling
5. Create migrations for model changes
6. Test API endpoints manually

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [aiokafka Documentation](https://aiokafka.readthedocs.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

---

Part of the **AI Logo Studio** project. See main [README](../README.md) for full project documentation.
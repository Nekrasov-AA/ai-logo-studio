# AI Logo Studio 🎨

**AI Logo Studio** is a modern platform for automatic logo generation using microservice architecture. The system enables creating professional logos in real-time based on user preferences.

## ✨ Features

- 🎯 **Intelligent generation** of logos based on business type and preferences
- 🎨 **Multiple variants** — 6 different designs for each request  
- 🌈 **Color schemes** — warm, cool and monochrome palettes
- ⚡ **Asynchronous processing** through message queues
- 📊 **Real-time progress tracking** via Server-Sent Events
- 🔄 **Scalability** thanks to microservice architecture
- 💾 **Cloud storage** for generated files

## 🏗️ Tech Stack

### Backend
- **FastAPI** — modern web framework for APIs
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM with async/await support
- **Alembic** — database migrations
- **Pydantic** — data validation

### Message Queue & Processing
- **Apache Kafka** — message queue for asynchronous processing
- **Confluent Platform** — Kafka infrastructure
- **Zookeeper** — Kafka cluster coordination

### Storage & Monitoring
- **LocalStack** — local AWS S3 emulation
- **Kafdrop** — web interface for Kafka monitoring

### Frontend
- **Next.js 15** — React framework with Server-Side Rendering
- **React 19** — UI library
- **TypeScript** — typed JavaScript
- **Tailwind CSS** — utility-first CSS framework

### DevOps
- **Docker** — service containerization
- **Docker Compose** — multi-container application orchestration

## 🚀 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │────│   Backend API   │────│   PostgreSQL    │
│   (Next.js)     │    │   (FastAPI)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Kafka       │
                       │   (Message      │
                       │    Queue)       │
                       └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LocalStack    │────│     Worker      │    │    Kafdrop      │
│      (S3)       │    │  (Processing)   │    │  (Monitoring)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Services and Ports

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 3000 | Next.js application |
| **Backend** | 8000 | FastAPI REST API |
| **PostgreSQL** | 5432 | Database |
| **Kafka** | 29092 | Message broker |
| **Zookeeper** | 2181 | Kafka coordinator |
| **LocalStack** | 4566 | S3-compatible storage |
| **Kafdrop** | 19000 | Kafka web interface |

## 🛠️ Installation and Setup

### Prerequisites

- **Docker** >= 20.0
- **Docker Compose** >= 2.0
- **Git**

### Clone Repository

```bash
git clone https://github.com/Nekrasov-AA/ai-logo-studio.git
cd ai-logo-studio
```

### Launch Project

1. **Build and start all services:**
```bash
docker-compose up --build -d
```

2. **Apply database migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

3. **Check service status:**
```bash
docker-compose ps
```

### Access Applications

- **Web application**: http://localhost:3000
- **API documentation**: http://localhost:8000/docs
- **Kafka monitoring**: http://localhost:19000

## 🧪 Testing

### API Health Check

```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

### Create Logo Generation Task

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "tech startup",
    "preferences": {
      "style": "modern",
      "theme": "minimalist", 
      "color": "blue"
    }
  }'
```

**Response:**
```json
{
  "job_id": "73831643-6ce8-42e6-aa50-0e9da805cc53",
  "status": "queued"
}
```

### Get Results

```bash
curl http://localhost:8000/api/result/{job_id}
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
    // ... 5 more variants
  ]
}
```

### Progress Tracking (Server-Sent Events)

```bash
curl http://localhost:8000/api/progress/{job_id}
```

## 📊 Monitoring

### View Logs

```bash
# All services logs
docker-compose logs -f

# Specific service logs
docker-compose logs backend
docker-compose logs worker
docker-compose logs frontend
```

### Kafka Monitoring

1. Open http://localhost:19000
2. Browse topics and messages
3. Main topic: `logo.requests`

### Check Kafka Topics

```bash
docker-compose exec kafka kafka-topics \
  --bootstrap-server kafka:9092 --list
```

## 🔧 Development

### Project Structure

```
ai-logo-studio/
├── backend/           # FastAPI application
│   ├── app/          
│   │   ├── api/      # REST API endpoints
│   │   ├── core/     # Core modules (DB, Kafka, S3)
│   │   ├── models/   # SQLAlchemy models
│   │   └── schemas/  # Pydantic schemas
│   ├── alembic/      # DB migrations
│   └── Dockerfile
├── frontend/         # Next.js application
│   ├── src/
│   │   └── app/     # App Router pages
│   └── Dockerfile
├── worker/           # Kafka consumer
│   ├── src/
│   └── Dockerfile
└── docker-compose.yml
```

### Local Development

```bash
# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose up backend -d

# Connect to container
docker-compose exec backend bash
```

### Create Migrations

```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
docker-compose exec backend alembic upgrade head
```

## 🛡️ Environment Variables

Main variables configured in `docker-compose.yml`:

- `DATABASE_URL` — PostgreSQL connection
- `KAFKA_BOOTSTRAP_SERVERS` — Kafka broker addresses  
- `S3_ENDPOINT_URL` — LocalStack S3 endpoint
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` — AWS credentials for LocalStack
- `S3_BUCKET` — S3 bucket name for file storage

## 📈 Performance

- **Asynchronous processing** via Kafka ensures high throughput
- **Horizontal scaling** of workers for increased performance
- **Result caching** in database
- **CDN-ready** URLs for fast content delivery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

Made with ❤️ by [Nekrasov-AA](https://github.com/Nekrasov-AA)
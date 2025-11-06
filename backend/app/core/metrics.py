"""
Prometheus metrics for monitoring AI Logo Studio performance
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
from functools import wraps

# HTTP Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

# Business Logic metrics
LOGO_JOBS_CREATED = Counter('logo_jobs_created_total', 'Total logo generation jobs created')
LOGO_JOBS_COMPLETED = Counter('logo_jobs_completed_total', 'Total logo generation jobs completed', ['status'])
ACTIVE_LOGO_JOBS = Gauge('logo_jobs_active', 'Number of currently active logo generation jobs')
LOGO_GENERATION_TIME = Histogram('logo_generation_duration_seconds', 'Time taken to generate logos', buckets=[1, 5, 10, 30, 60])

# Kafka metrics
KAFKA_MESSAGES_SENT = Counter('kafka_messages_sent_total', 'Total Kafka messages sent', ['topic', 'status'])
KAFKA_MESSAGES_PROCESSED = Counter('kafka_messages_processed_total', 'Total Kafka messages processed', ['topic', 'status'])
KAFKA_PROCESSING_TIME = Histogram('kafka_message_processing_seconds', 'Time taken to process Kafka messages')

# Database metrics
DB_CONNECTIONS_ACTIVE = Gauge('db_connections_active', 'Number of active database connections')
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Database query duration', ['operation'])

# S3 metrics
S3_UPLOADS = Counter('s3_uploads_total', 'Total S3 uploads', ['status'])
S3_UPLOAD_SIZE = Histogram('s3_upload_size_bytes', 'Size of S3 uploads')


def track_request_metrics(func):
    """Decorator to automatically track HTTP request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status_code = 200
        method = "unknown"
        endpoint = func.__name__
        
        try:
            # Try to get method and path from request
            if 'request' in kwargs:
                request = kwargs['request']
                method = request.method
                endpoint = request.url.path
            
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    return wrapper


def track_logo_job_created():
    """Track when a new logo job is created"""
    LOGO_JOBS_CREATED.inc()
    ACTIVE_LOGO_JOBS.inc()


def track_logo_job_completed(status: str = "success"):
    """Track when a logo job is completed"""
    LOGO_JOBS_COMPLETED.labels(status=status).inc()
    ACTIVE_LOGO_JOBS.dec()


def track_kafka_message_sent(topic: str, success: bool = True):
    """Track Kafka message sending"""
    status = "success" if success else "error"
    KAFKA_MESSAGES_SENT.labels(topic=topic, status=status).inc()


def track_kafka_message_processed(topic: str, success: bool = True, duration: float = 0):
    """Track Kafka message processing"""
    status = "success" if success else "error"
    KAFKA_MESSAGES_PROCESSED.labels(topic=topic, status=status).inc()
    if duration > 0:
        KAFKA_PROCESSING_TIME.observe(duration)


def track_s3_upload(success: bool = True, file_size: int = 0):
    """Track S3 upload metrics"""
    status = "success" if success else "error"
    S3_UPLOADS.labels(status=status).inc()
    if file_size > 0:
        S3_UPLOAD_SIZE.observe(file_size)


async def get_prometheus_metrics():
    """Return Prometheus metrics in the expected format"""
    return generate_latest()
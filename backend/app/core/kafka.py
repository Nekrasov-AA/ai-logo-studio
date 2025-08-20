import json
from aiokafka import AIOKafkaProducer
from .settings import settings

_producer: AIOKafkaProducer | None = None

async def init_producer():
    global _producer
    _producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await _producer.start()

async def shutdown_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None

def get_producer() -> AIOKafkaProducer:
    if _producer is None:
        raise RuntimeError("Kafka producer is not initialized")
    return _producer

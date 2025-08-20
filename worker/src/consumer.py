import asyncio, json, os, uuid, sys, datetime
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import boto3
from botocore.config import Config

KAFKA = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
DB_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://app:app@db:5432/appdb")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localstack:4566")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
S3_BUCKET = os.getenv("S3_BUCKET", "ai-logo-studio")

engine = create_async_engine(DB_URL, echo=False, future=True)

def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(s3={"addressing_style": "path"})
    )

async def set_status(job_id: str, status: str):
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE jobs SET status=:s WHERE id=:id"),
                           {"s": status, "id": uuid.UUID(job_id)})

async def set_result_key(job_id: str, key: str):
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE jobs SET result_svg_key=:k WHERE id=:id"),
                           {"k": key, "id": uuid.UUID(job_id)})

def make_simple_svg(text_label: str) -> bytes:
    # элементарный SVG: круг + текст
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <circle cx="256" cy="200" r="120" fill="#111111"/>
  <text x="50%" y="360" text-anchor="middle" font-size="32" font-family="Arial" fill="#111111">
    {text_label}
  </text>
</svg>'''
    return svg.encode("utf-8")

async def process(payload: dict):
    job_id = payload["job_id"]
    business_type = payload.get("business_type", "business")

    print(f"[worker] processing job {job_id}", flush=True)
    for stage in ["generating", "vectorizing", "exporting"]:
        await set_status(job_id, stage)
        await asyncio.sleep(0.8)

    # Подготовка и загрузка SVG
    key = f"jobs/{job_id}/logo.svg"
    body = make_simple_svg(business_type)
    s3 = s3_client()
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="image/svg+xml")

    await set_result_key(job_id, key)
    await set_status(job_id, "done")
    print(f"[worker] job {job_id} uploaded to s3://{S3_BUCKET}/{key}", flush=True)

async def main():
    print(f"[worker] starting; kafka={KAFKA} db={DB_URL}", flush=True)
    consumer = AIOKafkaConsumer(
        "logo.requests",
        bootstrap_servers=KAFKA,
        group_id="logo-worker",
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    print("[worker] consumer started, waiting messages…", flush=True)
    try:
        async for msg in consumer:
            try:
                await process(msg.value)
            except Exception as e:
                print(f"[worker] error processing: {e}", file=sys.stderr, flush=True)
                try:
                    await set_status(msg.value.get("job_id"), "error")
                except Exception:
                    pass
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())

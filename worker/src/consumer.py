import asyncio, json, os, uuid, sys
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

KAFKA = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
DB_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://app:app@db:5432/appdb")

engine = create_async_engine(DB_URL, echo=False, future=True)

async def set_status(job_id: str, status: str):
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE jobs SET status = :status WHERE id = :id"),
            {"status": status, "id": uuid.UUID(job_id)},
        )

async def process(payload: dict):
    job_id = payload["job_id"]
    print(f"[worker] processing job {job_id}", flush=True)
    for stage in ["generating", "vectorizing", "exporting"]:
        await set_status(job_id, stage)
        print(f"[worker] job {job_id} -> {stage}", flush=True)
        await asyncio.sleep(1.0)
    await set_status(job_id, "done")
    print(f"[worker] job {job_id} -> done", flush=True)

async def main():
    print(f"[worker] starting; kafka={KAFKA} db={DB_URL}", flush=True)
    consumer = AIOKafkaConsumer(
        "logo.requests",
        bootstrap_servers=KAFKA,
        group_id="logo-worker",
        enable_auto_commit=True,
        auto_offset_reset="earliest",           # важное дополнение
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    print("[worker] consumer started, waiting messages…", flush=True)
    try:
        async for msg in consumer:
            try:
                await process(msg.value)
            except Exception as e:
                print(f"[worker] error processing message: {e}", file=sys.stderr, flush=True)
                try:
                    await set_status(msg.value.get("job_id"), "error")
                except Exception:
                    pass
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())

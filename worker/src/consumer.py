import asyncio, json, os, uuid, sys, math
from typing import List, Dict
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import svgwrite
import boto3
from botocore.config import Config

# --- ENV ---
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

# --- DB helpers ---
async def set_status(job_id: str, status: str):
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE jobs SET status=:s WHERE id=:id"),
                           {"s": status, "id": uuid.UUID(job_id)})

async def insert_variant(job_id: str, index: int, palette: Dict, key: str):
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO logo_variants (id, job_id, "index", palette, svg_key)
                VALUES (:id, :job_id, :idx, :palette, :key)
            """),
            {
                "id": uuid.uuid4(),
                "job_id": uuid.UUID(job_id),
                "idx": index,
                "palette": json.dumps(palette),
                "key": key,
            }
        )

# --- Palettes ---
PRESET_PALETTES = [
    {"name":"warm","colors":["#FF6B6B","#FFD93D","#FFA552","#2C2C2C"]},
    {"name":"cool","colors":["#4D96FF","#6BCB77","#3D5AF1","#222222"]},
    {"name":"mono","colors":["#111111","#555555","#999999","#FFFFFF"]},
]

def suggest_palettes(business_type: str, prefs: Dict) -> List[Dict]:
    # simple heuristic: if user specified colors, put it first
    fav = None
    colors_pref = prefs.get("colors")
    if isinstance(colors_pref, list) and colors_pref:
        # allow "warm"/"cool" etc.
        name = colors_pref[0]
        for p in PRESET_PALETTES:
            if p["name"] == name:
                fav = p
                break
    palettes = PRESET_PALETTES.copy()
    if fav:
        palettes = [fav] + [p for p in palettes if p["name"] != fav["name"]]
    return palettes[:3]  # maximum 3 palettes

# --- SVG layouts ---
def initials_from_business(business_type: str) -> str:
    parts = [w for w in business_type.split() if w.strip()]
    if not parts: return "AI"
    if len(parts) == 1: return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()

def layout_emblem(business_type: str, palette: Dict, size: int = 512) -> bytes:
    d = svgwrite.Drawing(size=(size, size))
    bg = "#FFFFFF"
    d.add(d.rect(insert=(0,0), size=(size,size), fill=bg))
    c = palette["colors"]
    # circle + letters
    d.add(d.circle(center=(size/2, size*0.42), r=size*0.22, fill=c[0]))
    initials = initials_from_business(business_type)
    d.add(d.text(initials,
                 insert=("50%", size*0.46),
                 text_anchor="middle",
                 font_size=size*0.18,
                 font_family="Arial",
                 fill="#FFFFFF"))
    # business label
    d.add(d.text(business_type.title(),
                 insert=("50%", size*0.78),
                 text_anchor="middle",
                 font_size=size*0.07,
                 font_family="Arial",
                 fill=c[3] if len(c)>3 else "#222"))
    return d.tostring().encode("utf-8")

def layout_mark_left_text(business_type: str, palette: Dict, size: int = 512) -> bytes:
    d = svgwrite.Drawing(size=(size, size))
    d.add(d.rect(insert=(0,0), size=(size,size), fill="#FFFFFF"))
    c = palette["colors"]
    # abstract mark: three rectangles/bars
    pad = size*0.12
    w = size*0.16
    h = size*0.48
    x = pad
    y = size*0.26
    d.add(d.rect(insert=(x, y), size=(w, h), rx=size*0.02, fill=c[0]))
    d.add(d.rect(insert=(x+w*1.2, y), size=(w, h*0.8), rx=size*0.02, fill=c[1]))
    d.add(d.rect(insert=(x+w*2.4, y), size=(w, h*0.6), rx=size*0.02, fill=c[2]))
    # text on the right
    d.add(d.text(business_type.title(),
                 insert=(size*0.55, size*0.45),
                 font_size=size*0.1, font_family="Arial",
                 fill="#111111"))
    d.add(d.text("since 2025",
                 insert=(size*0.55, size*0.58),
                 font_size=size*0.05, font_family="Arial",
                 fill="#666"))
    return d.tostring().encode("utf-8")

LAYOUTS = [layout_emblem, layout_mark_left_text]

# --- S3 upload ---
def upload_svg(key: str, content: bytes):
    s3 = s3_client()
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=content, ContentType="image/svg+xml")

# --- Core processing ---
async def process(payload: dict):
    job_id = payload["job_id"]
    business_type = payload.get("business_type", "business")
    prefs = payload.get("prefs", {})

    print(f"[worker] processing job {job_id}", flush=True)
    await set_status(job_id, "generating")
    await asyncio.sleep(0.3)

    palettes = suggest_palettes(business_type, prefs)
    await set_status(job_id, "vectorizing")
    await asyncio.sleep(0.3)

    idx = 0
    for p in palettes:
        for layout in LAYOUTS:
            svg_bytes = layout(business_type, p)
            key = f"jobs/{job_id}/v{idx:02d}_{p['name']}.svg"
            upload_svg(key, svg_bytes)
            await insert_variant(job_id, idx, p, key)
            idx += 1

    await set_status(job_id, "exporting")
    await asyncio.sleep(0.2)
    await set_status(job_id, "done")
    print(f"[worker] job {job_id} done, {idx} variants uploaded", flush=True)

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


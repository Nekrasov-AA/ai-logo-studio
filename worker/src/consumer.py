import asyncio, json, os, uuid, sys
from typing import List, Dict
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import svgwrite
import boto3
from botocore.config import Config

# Import AI modules
try:
    # New AI Image Generator system
    from .ai_logo_generator_integration import ai_logo_generator
    from .ai_engines import GenerationStyle, ProcessingOptions, ProcessingLevel
    NEW_AI_ENABLED = True
    print("[worker] 🚀 New AI Image Generator system loaded successfully")
    
    # Legacy AI modules (fallback)
    from .logo_ai import logo_ai
    from .geometric_ai import geometric_ai
    from .premium_engine import premium_engine
    from .hybrid_ai import hybrid_ai
    from .ai_visual_generator import ai_visual_generator
    AI_ENABLED = True
    HYBRID_AI_ENABLED = True
    print("[worker] 🧠 Legacy AI system also available as fallback")
except ImportError as e:
    print(f"[worker] Warning: AI modules not available ({e}), using fallback generation")
    NEW_AI_ENABLED = False
    AI_ENABLED = False
    HYBRID_AI_ENABLED = False

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

# --- Helper functions ---
def determine_industry(business_type: str) -> str:
    """Determine industry from business type."""
    bt_lower = business_type.lower()
    if any(word in bt_lower for word in ['tech', 'software', 'ai', 'digital', 'data']):
        return 'technology'
    elif any(word in bt_lower for word in ['health', 'medical', 'care', 'clinic', 'hospital']):
        return 'healthcare'
    elif any(word in bt_lower for word in ['finance', 'bank', 'investment', 'trading']):
        return 'finance'
    elif any(word in bt_lower for word in ['food', 'restaurant', 'cafe', 'culinary']):
        return 'food'
    elif any(word in bt_lower for word in ['design', 'creative', 'art', 'agency']):
        return 'creative'
    elif any(word in bt_lower for word in ['retail', 'shop', 'store', 'fashion']):
        return 'retail'
    elif any(word in bt_lower for word in ['education', 'school', 'university', 'learning']):
        return 'education'
    elif any(word in bt_lower for word in ['consulting', 'advisory', 'strategy']):
        return 'consulting'
    else:
        return 'other'

def map_style_preference(style_pref: str) -> 'GenerationStyle':
    """Map user style preference to GenerationStyle enum."""
    if not NEW_AI_ENABLED:
        return None
        
    style_mapping = {
        'minimal': GenerationStyle.MINIMALIST,
        'minimalist': GenerationStyle.MINIMALIST,
        'modern': GenerationStyle.MODERN,
        'contemporary': GenerationStyle.MODERN,
        'classic': GenerationStyle.CLASSIC,
        'traditional': GenerationStyle.CLASSIC,
        'playful': GenerationStyle.PLAYFUL,
        'fun': GenerationStyle.PLAYFUL,
        'bold': GenerationStyle.BOLD,
        'strong': GenerationStyle.BOLD,
        'elegant': GenerationStyle.ELEGANT,
        'sophisticated': GenerationStyle.ELEGANT,
        'tech': GenerationStyle.TECH,
        'technology': GenerationStyle.TECH,
        'organic': GenerationStyle.ORGANIC,
        'natural': GenerationStyle.ORGANIC
    }
    
    return style_mapping.get(style_pref.lower(), GenerationStyle.MODERN)

def extract_palette_from_variant(variant: Dict) -> Dict:
    """Extract palette from AI variant result."""
    # Try to get colors from AI analysis or use defaults
    default_colors = ["#0066CC", "#4D9EE8", "#B3D9FF", "#333333"]
    
    # If we have style info, try to extract colors
    style_info = variant.get('style_info', {})
    color_prefs = style_info.get('color_preferences', [])
    
    if color_prefs:
        # Pad with defaults if needed
        colors = color_prefs + default_colors
        colors = colors[:4]  # Take first 4
    else:
        colors = default_colors
    
    return {
        "name": f"ai_generated_{variant.get('variant_id', 'unknown')}",
        "colors": colors
    }

# --- NEW AI-powered processing ---
async def process_with_new_ai(payload: dict):
    """Process using new AI Image Generator system."""
    job_id = payload["job_id"]
    business_type = payload.get("business_type", "business")
    prefs = payload.get("prefs", {})

    print(f"[worker] 🚀 NEW AI processing job {job_id} for '{business_type}'", flush=True)
    await set_status(job_id, "generating")
    
    try:
        # Initialize AI system if not already done
        if not ai_logo_generator.is_initialized:
            print(f"[worker] 🔧 Initializing AI Logo Generator...", flush=True)
            success = await ai_logo_generator.initialize()
            if not success:
                print(f"[worker] ❌ Failed to initialize AI system, falling back to legacy", flush=True)
                return await process_legacy(payload)
        
        # Extract parameters
        business_name = prefs.get('business_name', business_type.split(' - ')[0] if ' - ' in business_type else business_type)
        description = prefs.get('description', f"A {business_type} business")
        industry = determine_industry(business_type)
        style = map_style_preference(prefs.get('style', 'modern'))
        color_preferences = prefs.get('colors', [])
        
        print(f"[worker] 🎯 Parameters: name='{business_name}', industry={industry}, style={style.value if style else 'modern'}", flush=True)
        
        # Configure processing options based on industry
        processing_options = ProcessingOptions(
            remove_background=True,
            enhance_contrast=True,
            sharpen_edges=True,
            normalize_colors=True,
            optimize_for_vector=True,
            processing_level=ProcessingLevel.STANDARD
        )
        
        await set_status(job_id, "ai_generating")
        
        # Generate AI logo variants
        variants = await ai_logo_generator.generate_logo_variants(
            business_name=business_name,
            business_type=business_type,
            industry=industry,
            description=description,
            style=style,
            color_preferences=color_preferences,
            brand_personality=prefs.get('personality', ['professional', 'trustworthy']),
            target_audience=prefs.get('target_audience', 'businesses'),
            count=3,
            processing_options=processing_options
        )
        
        print(f"[worker] ✨ Generated {len(variants)} AI logo variants", flush=True)
        
        await set_status(job_id, "vectorizing")
        
        # Save variants to S3
        for i, variant in enumerate(variants):
            # Use processed image if available, otherwise use AI result
            image_data = (variant.get("processed_result", {}).get("processed_image") or 
                         variant["ai_result"]["image_data"])
            
            provider = variant["ai_result"]["provider"]
            key = f"jobs/{job_id}/v{i:02d}_ai_{provider}.png"
            
            # Upload to S3
            s3 = s3_client()
            s3.put_object(
                Bucket=S3_BUCKET, 
                Key=key, 
                Body=image_data, 
                ContentType="image/png"
            )
            
            # Extract palette and save to database
            palette = extract_palette_from_variant(variant)
            await insert_variant(job_id, i, palette, key)
            
            print(f"[worker] 💾 Saved variant {i+1}: {key} ({provider})", flush=True)
        
        await set_status(job_id, "exporting")
        await asyncio.sleep(0.2)
        await set_status(job_id, "done")
        
        print(f"[worker] ✅ Job {job_id} completed with NEW AI system! Generated {len(variants)} variants", flush=True)
        
    except Exception as e:
        print(f"[worker] ❌ NEW AI processing failed: {e}, falling back to legacy", flush=True)
        # Fallback to legacy system
        return await process_legacy(payload)

# --- LEGACY AI-powered processing ---
async def process_legacy(payload: dict):
    """Legacy processing function (renamed from process)."""
    job_id = payload["job_id"]
    business_type = payload.get("business_type", "business")
    prefs = payload.get("prefs", {})

    print(f"[worker] 🤖 LEGACY AI processing job {job_id} for '{business_type}'", flush=True)
    await set_status(job_id, "generating")
    
    if HYBRID_AI_ENABLED:
        # Hybrid AI-powered generation with LLM
        print(f"[worker] 🧠 LLM-powered analysis of business: {business_type}", flush=True)
        
        # Step 1: Hybrid AI Business Analysis (LLM + Rules)
        business_name = prefs.get('business_name', business_type.split(' - ')[0] if ' - ' in business_type else business_type)
        business_description = prefs.get('description', f"A {business_type} business")
        
        # Use hybrid AI for deep analysis
        ai_analysis = await hybrid_ai.analyze_brand_with_ai(
            business_name, business_type, business_description
        )
        
        print(f"[worker] 🔍 Hybrid analysis: industry={ai_analysis.get('industry_classification')}, concepts={len(ai_analysis.get('logo_concepts', []))}", flush=True)
        
        # Step 2: AI Color Generation with psychology
        color_palettes = ai_analysis.get('color_palettes', [])
        ai_palettes = []
        
        for i, palette_colors in enumerate(color_palettes[:3]):
            ai_palettes.append({
                "name": f"ai_palette_{i+1}",
                "colors": palette_colors
            })
        
        # Fallback if no AI palettes
        if not ai_palettes:
            ai_palettes = suggest_palettes(business_type, prefs)
            
        print(f"[worker] 🎨 Generated {len(ai_palettes)} AI-driven palettes", flush=True)
        
    elif AI_ENABLED:
        # Standard AI-powered generation
        print(f"[worker] 🧠 Analyzing business: {business_type}", flush=True)
        
        # Step 1: AI Business Analysis
        business_name = prefs.get('business_name', business_type.split(' - ')[0] if ' - ' in business_type else business_type)
        business_analysis = logo_ai.analyze_business(business_name, business_type, prefs)
        
        print(f"[worker] 📊 Analysis complete: industry={business_analysis.industry}, complexity={business_analysis.complexity:.2f}, styles={business_analysis.style_preferences}", flush=True)
        
        # Step 2: AI Color Generation
        ai_palettes = logo_ai.generate_ai_palettes(business_analysis)
        print(f"[worker] 🎨 Generated {len(ai_palettes)} AI palettes", flush=True)
        
    else:
        # Fallback to simple generation
        from .logo_ai import BusinessAnalysis
        business_analysis = BusinessAnalysis(
            industry='other',
            keywords=[business_type.lower()],
            complexity=0.5,
            style_preferences=['modern'],
            target_audience='general',
            brand_personality=['professional'],
            recommended_colors=[(0, 100, 200), (100, 100, 100)]
        )
        ai_palettes = suggest_palettes(business_type, prefs)
        print(f"[worker] ⚠️ Using fallback generation", flush=True)
    
    await set_status(job_id, "vectorizing")
    
    # Step 3: AI Geometric Design
    layout_styles = ["emblem", "symbol_text", "wordmark"]
    idx = 0
    
    for palette in ai_palettes[:3]:  # Top 3 palettes
        for layout_style in layout_styles[:2]:  # Top 2 layouts per palette
            
            try:
                if HYBRID_AI_ENABLED:
                    # Hybrid AI-generated logo with LLM analysis + Visual AI
                    business_name = prefs.get('business_name', business_type.split(' - ')[0] if ' - ' in business_type else business_type)
                    business_description = prefs.get('description', f"A {business_type} business")
                    
                    svg_bytes = await ai_visual_generator.create_ai_powered_logo(
                        business_name, business_type, business_description, palette, layout_style
                    )
                    variant_name = f"hybrid_ai_{layout_style}_{palette['name']}"
                    
                elif AI_ENABLED:
                    # Premium AI-generated logo using advanced design engine
                    business_name = prefs.get('business_name', business_type.split(' - ')[0] if ' - ' in business_type else business_type)
                    svg_bytes = premium_engine.create_stunning_logo(
                        business_name, business_analysis, palette, layout_style
                    )
                    variant_name = f"premium_{layout_style}_{palette['name']}"
                else:
                    # Fallback generation
                    if idx < len(LAYOUTS):
                        svg_bytes = LAYOUTS[idx % len(LAYOUTS)](business_type, palette)
                    else:
                        svg_bytes = LAYOUTS[0](business_type, palette)
                    variant_name = f"fallback_{palette['name']}"
                    
            except Exception as e:
                print(f"[worker] ⚠️ AI generation failed for variant {idx+1}: {e}", flush=True)
                # Emergency fallback to simple generation
                svg_bytes = LAYOUTS[0](business_type, palette)
                variant_name = f"emergency_fallback_{palette['name']}"
            
            key = f"jobs/{job_id}/v{idx:02d}_{variant_name}.svg"
            upload_svg(key, svg_bytes)
            await insert_variant(job_id, idx, palette, key)
            
            print(f"[worker] ✨ Generated variant {idx+1}: {variant_name}", flush=True)
            idx += 1
            
            if idx >= 6:  # Limit to 6 variants
                break
        
        if idx >= 6:
            break

    await set_status(job_id, "exporting")
    await asyncio.sleep(0.2)
    await set_status(job_id, "done")
    
    if HYBRID_AI_ENABLED:
        ai_status = "� Hybrid AI-powered (LLM + Visual AI)"
    elif AI_ENABLED:
        ai_status = "🤖 AI-powered"
    else:
        ai_status = "📝 Template-based"
    print(f"[worker] ✅ Job {job_id} complete! Generated {idx} {ai_status} logo variants", flush=True)

# --- MAIN PROCESSING FUNCTION ---
async def process(payload: dict):
    """Main processing function - routes to new AI or legacy system."""
    
    # Check if new AI system should be used
    use_new_ai = NEW_AI_ENABLED and os.getenv("USE_NEW_AI", "true").lower() == "true"
    
    if use_new_ai:
        print(f"[worker] 🚀 Using NEW AI Image Generator system", flush=True)
        await process_with_new_ai(payload)
    else:
        print(f"[worker] 🤖 Using LEGACY AI system", flush=True)
        await process_legacy(payload)

async def main():
    print(f"[worker] starting; kafka={KAFKA} db={DB_URL}", flush=True)
    
    # Print AI system status
    if NEW_AI_ENABLED:
        print(f"[worker] 🚀 NEW AI Image Generator: AVAILABLE", flush=True)
    if AI_ENABLED:
        print(f"[worker] 🤖 Legacy AI system: AVAILABLE", flush=True)
    if not NEW_AI_ENABLED and not AI_ENABLED:
        print(f"[worker] ⚠️  No AI systems available, using basic fallback", flush=True)
    
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


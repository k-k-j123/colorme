import os
import io
import base64
import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

from backend.config import PROVIDER_PRESETS, DEFAULT_BASE_URL, DEFAULT_MODEL, DEFAULT_API_KEY
from backend.sample_data import SAMPLE_ITEMS
from backend.database import (
    init_db,
    get_all_items,
    get_item,
    insert_item,
    update_item_analysis,
    update_item_attributes,
    update_item_basic,
    delete_item,
    clear_all_items
)
from backend.ai_service import (
    test_endpoint_connection,
    extract_garment_metadata,
    generate_outfits_from_extracted_data
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Initialize database schema
init_db()

app = FastAPI(
    title="ColorMe Style AI",
    description="Smart Wardrobe Stylist with single-image feature extraction and zero-image styling generation.",
    version="2.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionTestRequest(BaseModel):
    base_url: str
    api_key: Optional[str] = ""
    model: str

class StyleRequest(BaseModel):
    item_ids: Optional[List[str]] = None
    items: Optional[List[Dict[str, Any]]] = None
    occasion: Optional[str] = "Smart Casual"
    season: Optional[str] = "Mild / Spring-Fall"
    vibe_notes: Optional[str] = ""
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

class EditItemRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    color_hex: Optional[str] = None
    pattern: Optional[str] = None
    material_texture: Optional[str] = None
    fit_silhouette: Optional[str] = None
    formality_level: Optional[str] = None
    seasonality: Optional[List[str]] = None
    style_vibes: Optional[List[str]] = None
    key_features: Optional[List[str]] = None
    full_description: Optional[str] = None

class AnalyzeItemRequest(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

@app.get("/api/presets")
async def get_presets():
    """Returns available provider presets and environment defaults."""
    return {
        "presets": PROVIDER_PRESETS,
        "defaults": {
            "base_url": DEFAULT_BASE_URL,
            "model": DEFAULT_MODEL,
            "has_default_api_key": bool(DEFAULT_API_KEY)
        }
    }

@app.post("/api/test-connection")
async def test_connection(payload: ConnectionTestRequest):
    """Verifies that an OpenAI-compatible endpoint responds properly."""
    result = await test_endpoint_connection(
        base_url=payload.base_url,
        api_key=payload.api_key or "",
        model=payload.model
    )
    return result

@app.get("/api/wardrobe")
async def list_wardrobe_items():
    """Returns all clothing items stored in the SQLite database."""
    items = get_all_items()
    return {"items": items}

@app.post("/api/samples")
async def load_sample_wardrobe():
    """Loads pre-analyzed stylish wardrobe garments into the SQLite database."""
    for item in SAMPLE_ITEMS:
        insert_item(item)
    return {"items": get_all_items()}

@app.post("/api/upload")
async def upload_and_analyze_garment(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    category: Optional[str] = Form("Tops"),
    base_url: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    model: Optional[str] = Form(None)
):
    """
    1. Compresses and saves the single uploaded clothing image.
    2. Sends ONLY this single image to the AI model to extract rich attributes.
    3. Persists the extracted item to SQLite DB for all future zero-image outfit queries.
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert RGBA/P to RGB if needed
        if image.mode in ("RGBA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "RGBA":
                background.paste(image, mask=image.split()[3])
            else:
                background.paste(image)
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")
            
        # Resize to max 1024x1024
        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        item_id = f"item-{uuid.uuid4().hex[:8]}"
        filename = f"{item_id}.jpg"
        file_path = os.path.join(UPLOADS_DIR, filename)
        image.save(file_path, format="JPEG", quality=85, optimize=True)
        
        # Also prepare base64 for vision call
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85, optimize=True)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{img_b64}"
        image_url = f"/uploads/{filename}"

        clean_filename = file.filename or "Garment"
        hint_name = name or os.path.splitext(clean_filename)[0].replace("-", " ").replace("_", " ").title()

        # Initial database insert
        initial_item = {
            "id": item_id,
            "name": hint_name,
            "category": category or "Tops",
            "image_url": image_url,
            "is_analyzed": False
        }
        insert_item(initial_item)

        # Extract attributes using AI model on this SINGLE image
        try:
            analysis = await extract_garment_metadata(
                image_data=data_url,
                garment_hint_name=hint_name,
                base_url=base_url,
                api_key=api_key,
                model=model
            )
            updated_item = update_item_analysis(item_id, analysis)
            return updated_item or initial_item
        except Exception as ai_err:
            print(f"Warning: AI extraction failed ({str(ai_err)}). Storing basic record.")
            return initial_item

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

@app.post("/api/analyze-item/{item_id}")
async def analyze_existing_item(item_id: str, payload: AnalyzeItemRequest):
    """Re-analyzes an existing item in the DB with a single-image vision call."""
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    image_url = item["image_url"]
    
    # Read image data
    if image_url.startswith("/uploads/"):
        disk_path = os.path.join(BASE_DIR, image_url.lstrip("/"))
        if not os.path.exists(disk_path):
            raise HTTPException(status_code=404, detail="Image file not found on disk")
        with open(disk_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"
    elif image_url.startswith("data:image"):
        data_url = image_url
    else:
        data_url = image_url

    analysis = await extract_garment_metadata(
        image_data=data_url,
        garment_hint_name=item["name"],
        base_url=payload.base_url,
        api_key=payload.api_key,
        model=payload.model
    )
    updated = update_item_analysis(item_id, analysis)
    return updated

@app.put("/api/wardrobe/{item_id}")
async def edit_wardrobe_item(item_id: str, payload: EditItemRequest):
    """Updates identified attributes (color, hex, name, category, material, fit, etc.) for a wardrobe item."""
    data = payload.model_dump(exclude_unset=True)
    updated = update_item_attributes(item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@app.delete("/api/wardrobe/{item_id}")
async def remove_wardrobe_item(item_id: str):
    """Deletes an item from the wardrobe DB."""
    item = get_item(item_id)
    if item and item.get("image_url", "").startswith("/uploads/"):
        file_path = os.path.join(BASE_DIR, item["image_url"].lstrip("/"))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
    delete_item(item_id)
    return {"success": True, "deleted_id": item_id}

@app.delete("/api/wardrobe")
async def clear_wardrobe():
    """Clears all garments from the wardrobe DB."""
    clear_all_items()
    return {"success": True}

@app.post("/api/style")
async def style_outfits(payload: StyleRequest):
    """
    Takes the selected wardrobe items' stored metadata and generates outfit combinations
    and buying suggestions using PURE TEXT (ZERO IMAGES SENT).
    """
    items_to_style: List[Dict[str, Any]] = []

    # If item IDs were sent, fetch full records from DB
    if payload.item_ids:
        for i_id in payload.item_ids:
            item = get_item(i_id)
            if item:
                items_to_style.append(item)
    elif payload.items:
        items_to_style = payload.items
    else:
        # Style all items in DB
        items_to_style = get_all_items()

    if not items_to_style:
        raise HTTPException(status_code=400, detail="Please select at least 1 garment to style.")

    try:
        result = await generate_outfits_from_extracted_data(
            items=items_to_style,
            occasion=payload.occasion or "Smart Casual",
            season=payload.season or "Mild / Spring-Fall",
            vibe_notes=payload.vibe_notes or "",
            base_url=payload.base_url,
            api_key=payload.api_key,
            model=payload.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount uploads directory to serve uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Mount static folder for frontend UI
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

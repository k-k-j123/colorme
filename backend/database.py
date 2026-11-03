import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DB_DIR, "wardrobe.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wardrobe_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        sub_category TEXT,
        color_primary TEXT,
        color_secondary TEXT,
        color_hex TEXT,
        pattern TEXT,
        material_texture TEXT,
        fit_silhouette TEXT,
        formality_level TEXT,
        seasonality TEXT,
        style_vibes TEXT,
        key_features TEXT,
        full_description TEXT,
        image_url TEXT NOT NULL,
        is_analyzed INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    # Parse JSON fields
    for field in ("seasonality", "style_vibes", "key_features"):
        if d.get(field):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
        else:
            d[field] = []
    d["is_analyzed"] = bool(d.get("is_analyzed", 0))
    return d

def get_all_items() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wardrobe_items ORDER BY created_at DESC")
    rows = cursor.fetchall()
    items = [row_to_dict(r) for r in rows]
    conn.close()
    return items

def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wardrobe_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row) if row else None

def insert_item(item: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = item.get("created_at") or datetime.utcnow().isoformat()
    seasonality = json.dumps(item.get("seasonality") or [])
    style_vibes = json.dumps(item.get("style_vibes") or [])
    key_features = json.dumps(item.get("key_features") or [])

    cursor.execute("""
    INSERT OR REPLACE INTO wardrobe_items (
        id, name, category, sub_category, color_primary, color_secondary, color_hex,
        pattern, material_texture, fit_silhouette, formality_level,
        seasonality, style_vibes, key_features, full_description, image_url,
        is_analyzed, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item["id"],
        item["name"],
        item.get("category", "Tops"),
        item.get("sub_category", ""),
        item.get("color_primary", ""),
        item.get("color_secondary", ""),
        item.get("color_hex", "#4A5568"),
        item.get("pattern", "Solid"),
        item.get("material_texture", ""),
        item.get("fit_silhouette", ""),
        item.get("formality_level", "Casual"),
        seasonality,
        style_vibes,
        key_features,
        item.get("full_description", ""),
        item["image_url"],
        1 if item.get("is_analyzed") else 0,
        created_at
    ))
    conn.commit()
    conn.close()

def update_item_analysis(item_id: str, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    seasonality = json.dumps(analysis.get("seasonality") or [])
    style_vibes = json.dumps(analysis.get("style_vibes") or [])
    key_features = json.dumps(analysis.get("key_features") or [])

    cursor.execute("""
    UPDATE wardrobe_items SET
        name = COALESCE(NULLIF(?, ''), name),
        category = COALESCE(NULLIF(?, ''), category),
        sub_category = ?,
        color_primary = ?,
        color_secondary = ?,
        color_hex = ?,
        pattern = ?,
        material_texture = ?,
        fit_silhouette = ?,
        formality_level = ?,
        seasonality = ?,
        style_vibes = ?,
        key_features = ?,
        full_description = ?,
        is_analyzed = 1
    WHERE id = ?
    """, (
        analysis.get("name", ""),
        analysis.get("category", ""),
        analysis.get("sub_category", ""),
        analysis.get("color_primary", ""),
        analysis.get("color_secondary", ""),
        analysis.get("color_hex", "#4A5568"),
        analysis.get("pattern", ""),
        analysis.get("material_texture", ""),
        analysis.get("fit_silhouette", ""),
        analysis.get("formality_level", ""),
        seasonality,
        style_vibes,
        key_features,
        analysis.get("full_description", ""),
        item_id
    ))
    conn.commit()
    conn.close()
    return get_item(item_id)

def update_item_attributes(item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Process json fields if provided as lists
    seasonality = json.dumps(updates["seasonality"]) if "seasonality" in updates and isinstance(updates["seasonality"], list) else updates.get("seasonality")
    style_vibes = json.dumps(updates["style_vibes"]) if "style_vibes" in updates and isinstance(updates["style_vibes"], list) else updates.get("style_vibes")
    key_features = json.dumps(updates["key_features"]) if "key_features" in updates and isinstance(updates["key_features"], list) else updates.get("key_features")

    cursor.execute("""
    UPDATE wardrobe_items SET
        name = COALESCE(?, name),
        category = COALESCE(?, category),
        sub_category = COALESCE(?, sub_category),
        color_primary = COALESCE(?, color_primary),
        color_secondary = COALESCE(?, color_secondary),
        color_hex = COALESCE(?, color_hex),
        pattern = COALESCE(?, pattern),
        material_texture = COALESCE(?, material_texture),
        fit_silhouette = COALESCE(?, fit_silhouette),
        formality_level = COALESCE(?, formality_level),
        seasonality = COALESCE(?, seasonality),
        style_vibes = COALESCE(?, style_vibes),
        key_features = COALESCE(?, key_features),
        full_description = COALESCE(?, full_description),
        is_analyzed = 1
    WHERE id = ?
    """, (
        updates.get("name"),
        updates.get("category"),
        updates.get("sub_category"),
        updates.get("color_primary"),
        updates.get("color_secondary"),
        updates.get("color_hex"),
        updates.get("pattern"),
        updates.get("material_texture"),
        updates.get("fit_silhouette"),
        updates.get("formality_level"),
        seasonality,
        style_vibes,
        key_features,
        updates.get("full_description"),
        item_id
    ))
    conn.commit()
    conn.close()
    return get_item(item_id)

def update_item_basic(item_id: str, name: str, category: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE wardrobe_items SET name = ?, category = ? WHERE id = ?", (name, category, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wardrobe_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def clear_all_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wardrobe_items")
    conn.commit()
    conn.close()


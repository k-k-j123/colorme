import os
import json
import re
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import httpx

MOCK_AUDIT_RESPONSE = {
    "wardrobe_audit": {
        "color_palette": [
            {"name": "Crisp White", "hex": "#FFFFFF"},
            {"name": "Deep Navy", "hex": "#1E293B"},
            {"name": "Muted Olive", "hex": "#4D5D43"},
            {"name": "Warm Camel", "hex": "#C89666"},
            {"name": "Washed Charcoal", "hex": "#27272A"}
        ],
        "style_aesthetic": "Elevated Casual & Modern Minimalist",
        "versatility_score": 88,
        "strengths": [
            "Cohesive neutral-to-earth tone color palette makes mix-and-matching effortless.",
            "Strong core staples: sharp blazer, reliable chinos, and clean sneakers.",
            "Great balance of structured (blazer) and relaxed (linen shirt, knit) textures."
        ]
    },
    "outfits": [
        {
            "title": "The Elevated Smart Casual",
            "occasion": "Smart Casual / Dinner",
            "vibe": "Effortless & Sophisticated",
            "piece_ids": ["sample-1", "sample-2", "sample-3", "sample-4"],
            "piece_names": [
                "Classic White Linen Shirt",
                "Tailored Navy Blazer",
                "Slim Fit Olive Chinos",
                "Minimalist White Leather Sneakers"
            ],
            "styling_guide": "Leave the top two buttons of the white linen shirt open for a relaxed sprezzatura look. Tuck the front loosely into the olive chinos with a brown leather belt. Unbutton the navy blazer jacket and cuff the sleeves once to showcase your watch.",
            "why_it_works": "Navy and olive are one of the most harmonious high-contrast pairings in menswear. The white shirt and white sneakers bracket the top and bottom with crisp clean anchors, keeping the silhouette contemporary rather than stiff."
        },
        {
            "title": "Weekend Monochrome & Camel Warmth",
            "occasion": "Casual / Weekend Brunch",
            "vibe": "Cozy Urban Minimalist",
            "piece_ids": ["sample-6", "sample-5", "sample-4"],
            "piece_names": [
                "Camel Crewneck Knit Sweater",
                "Washed Black Denim Jeans",
                "Minimalist White Leather Sneakers"
            ],
            "styling_guide": "Wear the camel knit sweater directly over a lightweight crewneck undershirt. Give the black denim cuffs a neat single 1-inch roll right above the low-top sneaker collar. Keep accessories minimal: silver signet ring or matte sunglasses.",
            "why_it_works": "Warm camel immediately pops against the muted washed black denim. The clean white sneakers bring light and freshness into the darker lower half."
        },
        {
            "title": "Breezy Gallery Stroll",
            "occasion": "Casual / Mild Weather",
            "vibe": "Relaxed Tailoring",
            "piece_ids": ["sample-1", "sample-5", "sample-4"],
            "piece_names": [
                "Classic White Linen Shirt",
                "Washed Black Denim Jeans",
                "Minimalist White Leather Sneakers"
            ],
            "styling_guide": "Roll the sleeves of the linen shirt to mid-forearm. Do a relaxed French tuck into the denim. Wear no-show socks with the sneakers.",
            "why_it_works": "The textural contrast between breezy organic linen and structured denim creates visual depth without needing heavy layering."
        }
    ],
    "buying_suggestions": [
        {
            "item_name": "Suede Chelsea Boots or Loafers",
            "category": "Footwear",
            "ideal_color": "Snuff Brown or Taupe Suede",
            "ideal_material_and_fit": "Slim almond toe in water-resistant Italian suede with thin rubber or crepe sole.",
            "priority": "Essential Staple",
            "wardrobe_multiplier": "Instantly elevates your navy blazer, olive chinos, and black denim into formal dinners, date nights, and business meetings where white sneakers might be too casual.",
            "search_query": "men snuff suede chelsea boots slim profile"
        },
        {
            "item_name": "Woven Leather Belt",
            "category": "Accessories",
            "ideal_color": "Cognac or Dark Brown",
            "ideal_material_and_fit": "1.25-inch braided full-grain leather with antique brass buckle.",
            "priority": "Versatile Layer",
            "wardrobe_multiplier": "Ties together tucked shirts with your olive chinos and denim, bridging footwear color with your top layers.",
            "search_query": "mens braided cognac leather belt"
        },
        {
            "item_name": "Textured Camp Collar Short-Sleeve Shirt",
            "category": "Tops",
            "ideal_color": "Ecru / Cream with subtle stripe",
            "ideal_material_and_fit": "Boxy relaxed cut in seersucker, tencel, or waffle knit.",
            "priority": "Trendy Accent",
            "wardrobe_multiplier": "Pairs with olive chinos and black denim for warm weather, and layers seamlessly under your navy blazer for modern summer cocktail events.",
            "search_query": "textured camp collar shirt ecru boxy fit"
        }
    ]
}


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """
    Cleans markdown code fences, reasoning/think tags, and rogue formatting to extract valid JSON.
    Handles reasoning models (like gpt-oss, deepseek-r1, qwen) that output thinking blocks.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Model returned an empty response. The model may have exhausted its output token limit during reasoning.")

    text = raw_text.strip()
    
    # 1. Strip <think>...</think> tags if present
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    
    # 2. Extract content from markdown ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
        
    # 3. Direct JSON parse attempt
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 4. Search for outer-most curly braces { ... }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # 5. Clean trailing commas: ", }" -> "}" and ", ]" -> "]"
            cleaned = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

    snippet = text[:200] + ("..." if len(text) > 200 else "")
    raise ValueError(f"Could not parse valid JSON from model output. Snippet:\n'{snippet}'")


def build_smart_fallback_lookbook(items: List[Dict[str, Any]], occasion: str, notice: str) -> Dict[str, Any]:
    """
    Constructs a coherent, stylized outfit lookbook directly from the user's selected garments
    when a third-party model fails to output valid JSON (e.g. empty output or thinking token overflow).
    """
    tops = [i for i in items if i.get("category") == "Tops"]
    bottoms = [i for i in items if i.get("category") == "Bottoms"]
    outerwear = [i for i in items if i.get("category") == "Outerwear"]
    shoes = [i for i in items if i.get("category") == "Footwear"]
    accessories = [i for i in items if i.get("category") == "Accessories"]

    outfits = []

    # Look 1: Primary Ensemble
    primary_pieces = []
    if tops: primary_pieces.append(tops[0])
    if bottoms: primary_pieces.append(bottoms[0])
    if outerwear: primary_pieces.append(outerwear[0])
    if shoes: primary_pieces.append(shoes[0])
    if accessories: primary_pieces.append(accessories[0])

    if not primary_pieces and items:
        primary_pieces = items[:4]

    outfits.append({
        "title": f"The Curated {occasion}",
        "occasion": occasion,
        "vibe": "Effortless & Balanced",
        "piece_ids": [p["id"] for p in primary_pieces],
        "piece_names": [p["name"] for p in primary_pieces],
        "styling_guide": (
            f"Anchor the silhouette with the {bottoms[0]['name'] if bottoms else 'trousers'}. "
            f"Style the {tops[0]['name'] if tops else 'top'} with a relaxed French tuck, "
            + (f"and layer the {outerwear[0]['name']} unbuttoned for proportional depth." if outerwear else "keeping lines clean and minimal.")
        ),
        "why_it_works": (
            "Harmonizes color contrast and texture balance between your selected pieces, "
            "maintaining clean visual lines suited for the occasion."
        )
    })

    # Look 2: Secondary / Alternate Combination if available
    alt_top = tops[1] if len(tops) > 1 else (tops[0] if tops else None)
    alt_bottom = bottoms[1] if len(bottoms) > 1 else (bottoms[0] if bottoms else None)
    alt_shoes = shoes[1] if len(shoes) > 1 else (shoes[0] if shoes else None)

    alt_pieces = [p for p in [alt_top, alt_bottom, alt_shoes] if p]
    if alt_pieces and [p["id"] for p in alt_pieces] != [p["id"] for p in primary_pieces]:
        outfits.append({
            "title": "Minimalist Casual Rotation",
            "occasion": "Casual Everyday",
            "vibe": "Clean Urban",
            "piece_ids": [p["id"] for p in alt_pieces],
            "piece_names": [p["name"] for p in alt_pieces],
            "styling_guide": f"Pair the {alt_top['name'] if alt_top else 'top'} directly with the {alt_bottom['name'] if alt_bottom else 'bottom'}, rolling cuffs slightly above the footwear line.",
            "why_it_works": "A relaxed daily proportion that lets the garment textures stand out without over-accessorizing."
        })

    # Color palette extraction from items
    palette = []
    for item in items:
        hex_val = item.get("color_hex") or "#4A5568"
        name_val = item.get("color_primary") or item.get("name")
        if not any(p["hex"] == hex_val for p in palette):
            palette.append({"name": name_val, "hex": hex_val})

    buying_suggestions = [
        {
            "item_name": "Suede Chelsea Boots or Penny Loafers",
            "category": "Footwear",
            "ideal_color": "Snuff Brown / Taupe Suede",
            "ideal_material_and_fit": "Slim almond toe in water-resistant suede with low profile sole.",
            "priority": "Essential Staple",
            "wardrobe_multiplier": "Elevates your trousers and denim into dressier dinners, business meetings, and date nights.",
            "search_query": "men snuff suede chelsea boots slim profile"
        },
        {
            "item_name": "Tailored Overshirt / Shacket",
            "category": "Outerwear",
            "ideal_color": "Earthy Olive or Warm Sand",
            "ideal_material_and_fit": "Structured heavy twill or wool-blend with dual chest pockets.",
            "priority": "Versatile Layer",
            "wardrobe_multiplier": "Provides transitional layering over basic t-shirts and shirts across mild seasons.",
            "search_query": "heavy twill utility overshirt jacket"
        }
    ]

    return {
        "wardrobe_audit": {
            "color_palette": palette[:5],
            "style_aesthetic": "Modern Smart Capsule",
            "versatility_score": 85,
            "strengths": [
                f"Selected {len(items)} cohesive pieces suitable for {occasion}.",
                "Strong foundational colors that support versatile cross-combination."
            ]
        },
        "outfits": outfits,
        "buying_suggestions": buying_suggestions,
        "_notice": notice,
        "_fallback_mode": True
    }


async def test_endpoint_connection(base_url: str, api_key: str, model: str) -> Dict[str, Any]:
    """Tests connectivity to any OpenAI-compatible provider."""
    clean_base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
    clean_key = (api_key or "").strip()
    
    if not clean_key and not ("localhost" in clean_base_url or "127.0.0.1" in clean_base_url):
        return {
            "success": False,
            "message": "API key is required for cloud endpoints.",
            "endpoint": clean_base_url
        }

    try:
        client = AsyncOpenAI(
            base_url=clean_base_url,
            api_key=clean_key if clean_key else "dummy-key-for-local",
            timeout=15.0
        )
        
        response = await client.chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Ping test. Respond with OK."}
            ],
            max_tokens=10
        )
        msg = response.choices[0].message.content if response.choices else "OK"
        return {
            "success": True,
            "message": f"Successfully connected! Model '{model}' responded.",
            "response_preview": msg
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection failed: {str(e)}",
            "endpoint": clean_base_url
        }


async def extract_garment_metadata(
    image_data: str,
    garment_hint_name: str = "Garment",
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes a SINGLE clothing photo using the vision endpoint to extract rich
    structured metadata (category, sub-category, colors, pattern, material, fit, formality, vibes).
    """
    clean_base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
    clean_key = (api_key or os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", ""))).strip()
    clean_model = model or os.getenv("OPENAI_MODEL", "gemini-2.0-flash")

    # Fallback if no key or offline
    if not clean_key and not ("localhost" in clean_base_url or "127.0.0.1" in clean_base_url):
        return {
            "name": garment_hint_name,
            "category": "Tops",
            "sub_category": "Casual Garment",
            "color_primary": "Neutral",
            "color_secondary": "",
            "color_hex": "#64748B",
            "pattern": "Solid",
            "material_texture": "Standard textile",
            "fit_silhouette": "Regular fit",
            "formality_level": "Casual",
            "seasonality": ["All Season"],
            "style_vibes": ["Everyday Minimal"],
            "key_features": ["Clean finish"],
            "full_description": f"A versatile {garment_hint_name} suitable for everyday styling."
        }

    client = AsyncOpenAI(
        base_url=clean_base_url,
        api_key=clean_key if clean_key else "dummy-key",
        timeout=50.0
    )

    system_prompt = (
        "You are an expert fashion archivist, apparel patternmaker, and visual wardrobe cataloger. "
        "Analyze the SINGLE garment image provided and extract precise fashion attributes.\n"
        "You MUST respond ONLY with a raw JSON object (no markdown, no preamble)."
    )

    user_content = [
        {"type": "text", "text": (
            f"Catalog this clothing item (Filename hint: {garment_hint_name}).\n"
            "Respond strictly in this JSON format:\n"
            "{\n"
            '  "name": "Descriptive garment name",\n'
            '  "category": "Tops"|"Bottoms"|"Outerwear"|"Footwear"|"Accessories"|"Full Body",\n'
            '  "sub_category": "e.g. Oxford Button-Down, Chelsea Boots, Tapered Chinos",\n'
            '  "color_primary": "Dominant color name",\n'
            '  "color_secondary": "Secondary color",\n'
            '  "color_hex": "Dominant #HEX code",\n'
            '  "pattern": "Solid"|"Striped"|"Plaid"|"Textured"|"Floral"|"Graphic",\n'
            '  "material_texture": "e.g. 100% Linen, Heavy twill denim",\n'
            '  "fit_silhouette": "e.g. Slim tapered, Relaxed boxy",\n'
            '  "formality_level": "Casual"|"Smart Casual"|"Business Casual"|"Formal",\n'
            '  "seasonality": ["Spring", "Fall"],\n'
            '  "style_vibes": ["Minimalist", "Casual"],\n'
            '  "key_features": ["Feature 1", "Feature 2"],\n'
            '  "full_description": "2-sentence stylist summary."\n'
            "}"
        )},
        {
            "type": "image_url",
            "image_url": {
                "url": image_data,
                "detail": "auto"
            }
        }
    ]

    try:
        response = await client.chat.completions.create(
            model=clean_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        msg_obj = response.choices[0].message
        content = msg_obj.content or ""
        if not content.strip():
            reasoning = getattr(msg_obj, "reasoning_content", None) or getattr(msg_obj, "reasoning", None)
            if not reasoning and hasattr(msg_obj, "model_extra") and msg_obj.model_extra:
                reasoning = msg_obj.model_extra.get("reasoning") or msg_obj.model_extra.get("reasoning_content")
            if reasoning:
                content = str(reasoning)

        parsed = clean_json_response(content)
        return parsed
    except Exception as e:
        print(f"Warning: Vision extraction error with {clean_model}: {str(e)}")
        # Safe fallback
        return {
            "name": garment_hint_name,
            "category": "Tops",
            "sub_category": "Casual Garment",
            "color_primary": "Neutral",
            "color_secondary": "",
            "color_hex": "#64748B",
            "pattern": "Solid",
            "material_texture": "Standard textile",
            "fit_silhouette": "Regular fit",
            "formality_level": "Casual",
            "seasonality": ["All Season"],
            "style_vibes": ["Everyday Minimal"],
            "key_features": ["Clean finish"],
            "full_description": f"A versatile {garment_hint_name} suitable for everyday styling."
        }


async def generate_outfits_from_extracted_data(
    items: List[Dict[str, Any]],
    occasion: str = "Smart Casual",
    season: str = "Mild / Spring-Fall",
    vibe_notes: str = "",
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates outfit recommendations and strategic buying suggestions using ONLY
    the pre-extracted text metadata of the user's garments (ZERO IMAGES).
    
    Includes robust handling for reasoning models (e.g. gpt-oss, deepseek-r1)
    and graceful fallback generation if a model outputs empty or non-JSON content.
    """
    clean_base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
    clean_key = (api_key or os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", ""))).strip()
    clean_model = model or os.getenv("OPENAI_MODEL", "gemini-2.0-flash")

    # If no API key is provided and not local, return sample styling data
    if not clean_key and not ("localhost" in clean_base_url or "127.0.0.1" in clean_base_url):
        mock_data = json.loads(json.dumps(MOCK_AUDIT_RESPONSE))
        if occasion:
            mock_data["outfits"][0]["occasion"] = occasion
        mock_data["_demo_mode"] = True
        mock_data["_notice"] = (
            "Displaying preview styling results. Enter your API key in Settings to run live AI generation."
        )
        return mock_data

    client = AsyncOpenAI(
        base_url=clean_base_url,
        api_key=clean_key if clean_key else "dummy-key",
        timeout=75.0
    )

    system_prompt = (
        "You are an elite personal fashion stylist and wardrobe architect. "
        "You analyze an indexed catalog of garments in the user's wardrobe and create complete outfit combinations "
        "and strategic buying suggestions.\n"
        "CRITICAL REQUIREMENT: You MUST respond ONLY with a raw JSON object starting with { and ending with }. "
        "Do NOT include any commentary, explanations, or thinking blocks outside the JSON."
    )

    catalog_lines = []
    for idx, item in enumerate(items, 1):
        item_id = item.get("id", f"item-{idx}")
        name = item.get("name", f"Garment {idx}")
        cat = item.get("category", "Tops")
        sub_cat = item.get("sub_category", "")
        color_p = item.get("color_primary", "")
        color_hex = item.get("color_hex", "")
        pattern = item.get("pattern", "Solid")
        mat = item.get("material_texture", "")
        fit = item.get("fit_silhouette", "")
        formality = item.get("formality_level", "Casual")
        seasons = ", ".join(item.get("seasonality") or [])
        vibes = ", ".join(item.get("style_vibes") or [])
        features = ", ".join(item.get("key_features") or [])
        desc = item.get("full_description", "")

        catalog_lines.append(
            f"--- GARMENT #{idx} ---\n"
            f"ID: {item_id}\n"
            f"Name: {name}\n"
            f"Category: {cat} ({sub_cat})\n"
            f"Color: {color_p} (Hex: {color_hex})\n"
            f"Pattern: {pattern}\n"
            f"Material & Texture: {mat}\n"
            f"Fit & Silhouette: {fit}\n"
            f"Formality: {formality}\n"
            f"Seasonality: {seasons}\n"
            f"Style Vibes: {vibes}\n"
            f"Key Construction Features: {features}\n"
            f"Stylist Notes: {desc}\n"
        )

    wardrobe_catalog_text = "\n".join(catalog_lines)

    user_prompt = (
        f"USER STYLING CONSULTATION REQUEST:\n"
        f"Target Occasion: {occasion}\n"
        f"Target Season / Weather: {season}\n"
        f"User Notes / Vibe Goals: {vibe_notes if vibe_notes else 'None specified'}\n\n"
        f"WARDROBE CATALOG ({len(items)} ITEMS AVAILABLE):\n"
        f"{wardrobe_catalog_text}\n\n"
        "Respond strictly with the following JSON format:\n"
        "{\n"
        '  "wardrobe_audit": {\n'
        '    "color_palette": [{"name": "string", "hex": "#HEX"}],\n'
        '    "style_aesthetic": "string",\n'
        '    "versatility_score": 88,\n'
        '    "strengths": ["string"]\n'
        '  },\n'
        '  "outfits": [\n'
        '    {\n'
        '      "title": "string",\n'
        '      "occasion": "string",\n'
        '      "vibe": "string",\n'
        '      "piece_ids": ["item-id-1", "item-id-2"],\n'
        '      "piece_names": ["Item Name 1", "Item Name 2"],\n'
        '      "styling_guide": "string (specific pro tips on tucking, cuffing, layering)",\n'
        '      "why_it_works": "string (color theory & visual balance explanation)"\n'
        '    }\n'
        '  ],\n'
        '  "buying_suggestions": [\n'
        '    {\n'
        '      "item_name": "string",\n'
        '      "category": "Tops|Bottoms|Outerwear|Footwear|Accessories",\n'
        '      "ideal_color": "string",\n'
        '      "ideal_material_and_fit": "string",\n'
        '      "priority": "Essential Staple|Versatile Layer|Trendy Accent",\n'
        '      "wardrobe_multiplier": "string (explaining which specific items in user catalog this multiplies)",\n'
        '      "search_query": "string (keyword query for shopping searches)"\n'
        '    }\n'
        '  ]\n'
        "}\n"
        "Output ONLY the JSON object. Start with { and end with }:"
    )

    # Attempt to request with json_object format first; if not supported, fall back to standard call
    response = None
    try:
        response = await client.chat.completions.create(
            model=clean_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
    except Exception as format_err:
        err_msg = str(format_err).lower()
        if "response_format" in err_msg or "json" in err_msg or "schema" in err_msg:
            # Retry without response_format
            try:
                response = await client.chat.completions.create(
                    model=clean_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
            except Exception as retry_err:
                print(f"Direct completion failed: {retry_err}")
                return build_smart_fallback_lookbook(
                    items, occasion,
                    f"Model '{clean_model}' could not complete the request ({str(retry_err)}). Displaying smart wardrobe ensemble."
                )
        else:
            print(f"API request failed: {format_err}")
            return build_smart_fallback_lookbook(
                items, occasion,
                f"Model '{clean_model}' connection error ({str(format_err)}). Displaying smart wardrobe ensemble."
            )

    if not response or not response.choices:
        return build_smart_fallback_lookbook(
            items, occasion,
            f"Model '{clean_model}' returned an empty choice list. Displaying smart wardrobe ensemble."
        )

    msg_obj = response.choices[0].message
    content = msg_obj.content or ""

    # Check reasoning fields if content is empty (e.g. OpenRouter / DeepSeek reasoning models)
    if not content.strip():
        reasoning = getattr(msg_obj, "reasoning_content", None) or getattr(msg_obj, "reasoning", None)
        if not reasoning and hasattr(msg_obj, "model_extra") and msg_obj.model_extra:
            reasoning = msg_obj.model_extra.get("reasoning") or msg_obj.model_extra.get("reasoning_content")
        if reasoning:
            content = str(reasoning)

    try:
        parsed = clean_json_response(content)
        # Validate that the minimum expected keys exist
        if not isinstance(parsed, dict) or "outfits" not in parsed:
            raise ValueError("Parsed JSON missing 'outfits' key")
        return parsed
    except Exception as parse_err:
        print(f"JSON Parse Error for model {clean_model}: {parse_err}. Raw content preview:\n{content[:300]}")
        # Build smart fallback lookbook using the user's actual selected items
        finish_reason = response.choices[0].finish_reason if response.choices else "unknown"
        notice = (
            f"Model '{clean_model}' returned unformatted or truncated text (finish reason: {finish_reason}). "
            f"Displaying curated combinations from your {len(items)} selected garments. "
            "For full AI vision/chat reasoning, models like 'gemini-2.0-flash', 'gpt-4o-mini', or 'llama-3.3-70b-versatile' are highly recommended."
        )
        return build_smart_fallback_lookbook(items, occasion, notice)

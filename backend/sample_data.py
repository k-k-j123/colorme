import base64

def _svg_to_data_uri(svg_code: str) -> str:
    encoded = base64.b64encode(svg_code.strip().encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"

# Clean, minimalist illustrated garment cards for instant testing with extracted metadata
SAMPLE_ITEMS = [
    {
        "id": "sample-1",
        "name": "Classic White Linen Shirt",
        "category": "Tops",
        "sub_category": "Linen Button-Down",
        "color_primary": "Crisp White",
        "color_secondary": "Pearl White",
        "color_hex": "#FFFFFF",
        "pattern": "Solid",
        "material_texture": "Lightweight breathable 100% European linen",
        "fit_silhouette": "Relaxed tailored fit with band collar",
        "formality_level": "Smart Casual",
        "seasonality": ["Spring", "Summer", "Warm Weather"],
        "style_vibes": ["Mediterranean", "Old Money", "Resort / Riviera", "Minimalist"],
        "key_features": ["Band collar", "Mother-of-pearl buttons", "Chest pocket", "Breathable weave"],
        "full_description": "A breezy, sophisticated white linen long-sleeve shirt with relaxed proportions, ideal for layering or solo wear.",
        "image_url": _svg_to_data_uri('''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
                <rect width="300" height="300" rx="20" fill="#F8FAFC"/>
                <!-- Shirt silhouette -->
                <path d="M110 65 L150 85 L190 65 L225 100 L205 125 L185 105 L185 240 L115 240 L115 105 L95 125 L75 100 Z" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="3"/>
                <!-- Collar -->
                <polygon points="150,85 120,65 140,60 150,80" fill="#F1F5F9" stroke="#94A3B8" stroke-width="2"/>
                <polygon points="150,85 180,65 160,60 150,80" fill="#F1F5F9" stroke="#94A3B8" stroke-width="2"/>
                <!-- Buttons line -->
                <line x1="150" y1="85" x2="150" y2="240" stroke="#CBD5E1" stroke-width="2" stroke-dasharray="2 12"/>
                <!-- Chest Pocket -->
                <rect x="125" y="120" width="20" height="25" rx="3" fill="none" stroke="#E2E8F0" stroke-width="2"/>
                <text x="150" y="275" font-family="sans-serif" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">White Linen Shirt</text>
            </svg>
        '''),
        "is_analyzed": True
    },
    {
        "id": "sample-2",
        "name": "Tailored Navy Blazer",
        "category": "Outerwear",
        "sub_category": "Unstructured Suit Jacket",
        "color_primary": "Deep Navy Blue",
        "color_secondary": "Dark Slate",
        "color_hex": "#1E293B",
        "pattern": "Solid / Fine Hopsack",
        "material_texture": "Italian wool-blend hopsack with subtle texture",
        "fit_silhouette": "Modern slim cut, soft unstructured natural shoulders",
        "formality_level": "Business Casual / Smart Casual",
        "seasonality": ["All Season", "Spring", "Fall", "Winter"],
        "style_vibes": ["Classic Sartorial", "Smart Casual", "Ivy League", "Contemporary Tailoring"],
        "key_features": ["Notch lapel", "Two-button front", "Dual side vents", "Patch pockets"],
        "full_description": "An essential versatile navy jacket with soft shoulders that transitions smoothly between denim and tailored trousers.",
        "image_url": _svg_to_data_uri('''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
                <rect width="300" height="300" rx="20" fill="#F8FAFC"/>
                <!-- Blazer Body -->
                <path d="M100 65 L150 90 L200 65 L245 115 L220 145 L195 120 L195 245 L105 245 L105 120 L80 145 L55 115 Z" fill="#1E293B" stroke="#0F172A" stroke-width="3"/>
                <!-- Lapels -->
                <path d="M125 65 L150 145 L105 110 Z" fill="#334155"/>
                <path d="M175 65 L150 145 L195 110 Z" fill="#334155"/>
                <!-- Buttons -->
                <circle cx="150" cy="165" r="4" fill="#F59E0B"/>
                <circle cx="150" cy="195" r="4" fill="#F59E0B"/>
                <!-- Flap Pockets -->
                <line x1="115" y1="200" x2="135" y2="200" stroke="#475569" stroke-width="3"/>
                <line x1="165" y1="200" x2="185" y2="200" stroke="#475569" stroke-width="3"/>
                <text x="150" y="275" font-family="sans-serif" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">Navy Tailored Blazer</text>
            </svg>
        '''),
        "is_analyzed": True
    },
    {
        "id": "sample-3",
        "name": "Slim Fit Olive Chinos",
        "category": "Bottoms",
        "sub_category": "Tapered Cotton Chinos",
        "color_primary": "Muted Olive Green",
        "color_secondary": "Earthy Military Green",
        "color_hex": "#4D5D43",
        "pattern": "Solid",
        "material_texture": "Midweight stretch cotton twill",
        "fit_silhouette": "Mid-rise, slim tapered from knee to hem",
        "formality_level": "Smart Casual",
        "seasonality": ["All Season", "Spring", "Fall"],
        "style_vibes": ["Military Workwear", "Smart Casual", "Earth Tones"],
        "key_features": ["Clean flat front", "Slanted trouser pockets", "Welt back pockets"],
        "full_description": "Versatile earth-toned chinos that pair naturally with white shirts, camel knitwear, and navy blazers.",
        "image_url": _svg_to_data_uri('''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
                <rect width="300" height="300" rx="20" fill="#F8FAFC"/>
                <!-- Pants -->
                <path d="M110 70 L190 70 L200 240 L165 240 L150 140 L135 240 L100 240 Z" fill="#4D5D43" stroke="#3A4732" stroke-width="3"/>
                <!-- Waistband & Belt Loops -->
                <rect x="110" y="70" width="80" height="15" fill="#3A4732"/>
                <line x1="150" y1="85" x2="150" y2="135" stroke="#3A4732" stroke-width="2"/>
                <!-- Pockets -->
                <line x1="118" y1="87" x2="130" y2="105" stroke="#607154" stroke-width="2"/>
                <line x1="182" y1="87" x2="170" y2="105" stroke="#607154" stroke-width="2"/>
                <text x="150" y="275" font-family="sans-serif" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">Olive Chinos</text>
            </svg>
        '''),
        "is_analyzed": True
    },
    {
        "id": "sample-4",
        "name": "Minimalist White Leather Sneakers",
        "category": "Footwear",
        "sub_category": "Low-Top Cupsole Sneakers",
        "color_primary": "Clean White",
        "color_secondary": "Off-White Rubber Sole",
        "color_hex": "#F8FAFC",
        "pattern": "Solid",
        "material_texture": "Smooth full-grain calfskin leather",
        "fit_silhouette": "Low-profile streamlined silhouette",
        "formality_level": "Casual to Smart Casual",
        "seasonality": ["Spring", "Summer", "Mild Weather"],
        "style_vibes": ["Minimalist", "Scandinavian", "Smart Casual"],
        "key_features": ["Italian cupsole", "Tonal laces", "Padded leather collar"],
        "full_description": "Clean, unbranded white leather sneakers that elevate casual outfits and tone down formal tailored pieces.",
        "image_url": _svg_to_data_uri('''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
                <rect width="300" height="300" rx="20" fill="#F8FAFC"/>
                <!-- Sneaker outline -->
                <path d="M60 170 C70 140 100 135 130 135 L170 135 C190 135 215 145 235 160 C245 168 250 180 245 195 L65 195 Z" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="3"/>
                <!-- Sole -->
                <rect x="58" y="195" width="190" height="20" rx="5" fill="#E2E8F0" stroke="#94A3B8" stroke-width="2"/>
                <!-- Laces -->
                <line x1="130" y1="145" x2="170" y2="145" stroke="#94A3B8" stroke-width="3"/>
                <line x1="135" y1="155" x2="175" y2="155" stroke="#94A3B8" stroke-width="3"/>
                <line x1="140" y1="165" x2="180" y2="165" stroke="#94A3B8" stroke-width="3"/>
                <!-- Heel patch -->
                <path d="M62 170 C65 155 75 150 85 150 L85 195 L60 195 Z" fill="#CBD5E1"/>
                <text x="150" y="275" font-family="sans-serif" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">White Low-Top Sneakers</text>
            </svg>
        '''),
        "is_analyzed": True
    },
    {
        "id": "sample-5",
        "name": "Washed Black Denim Jeans",
        "category": "Bottoms",
        "sub_category": "Straight-Leg Jeans",
        "color_primary": "Washed Charcoal Black",
        "color_secondary": "Faded Grey",
        "color_hex": "#27272A",
        "pattern": "Subtle vintage wash",
        "material_texture": "13oz 100% cotton rigid selvedge denim",
        "fit_silhouette": "Classic straight leg, regular rise",
        "formality_level": "Casual",
        "seasonality": ["All Season", "Fall", "Winter"],
        "style_vibes": ["Streetwear", "Minimalist Rock / Grunge", "Urban Everyday"],
        "key_features": ["5-pocket styling", "Matte silver hardware", "Straight leg hem"],
        "full_description": "Faded charcoal black jeans that provide a neutral, modern base for knitwear, blazers, and shirts.",
        "image_url": _svg_to_data_uri('''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
                <rect width="300" height="300" rx="20" fill="#F8FAFC"/>
                <path d="M108 70 L192 70 L202 240 L168 240 L150 142 L132 240 L98 240 Z" fill="#27272A" stroke="#18181B" stroke-width="3"/>
                <rect x="108" y="70" width="84" height="15" fill="#18181B"/>
                <line x1="150" y1="85" x2="150" y2="135" stroke="#52525B" stroke-width="2"/>
                <!-- Rivets & Seams -->
                <circle cx="118" cy="88" r="2" fill="#E4E4E7"/>
                <circle cx="182" cy="88" r="2" fill="#E4E4E7"/>
                <text x="150" y="275" font-family="sans-serif" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">Washed Black Denim</text>
            </svg>
        '''),
        "is_analyzed": True
    },
    {
        "id": "sample-6",
        "name": "Camel Crewneck Knit Sweater",
        "category": "Tops",
        "sub_category": "Fine-Knit Crewneck",
        "color_primary": "Warm Honey Camel",
        "color_secondary": "Ochre / Tan",
        "color_hex": "#C89666",
        "pattern": "Solid",
        "material_texture": "Fine gauge 100% extrafine merino wool",
        "fit_silhouette": "Regular tailored fit with ribbed hems",
        "formality_level": "Smart Casual",
        "seasonality": ["Fall", "Winter", "Spring"],
        "style_vibes": ["Quiet Luxury", "Cozy Earth Tones", "Academic / Prep"],
        "key_features": ["Ribbed crewneck collar", "Set-in sleeves", "Dense knit gauge"],
        "full_description": "A refined camel merino crewneck that introduces rich warm tones into neutral wardrobes.",
        "image_url": _svg_to_data_uri('''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
                <rect width="300" height="300" rx="20" fill="#F8FAFC"/>
                <!-- Sweater Body -->
                <path d="M115 70 C130 85 170 85 185 70 L230 115 L205 140 L185 120 L185 240 L115 240 L115 120 L95 140 L70 115 Z" fill="#C89666" stroke="#9A6B3D" stroke-width="3"/>
                <!-- Ribbed Collar -->
                <path d="M115 70 C130 85 170 85 185 70 C170 80 130 80 115 70 Z" fill="#9A6B3D"/>
                <!-- Ribbed hem -->
                <rect x="115" y="225" width="70" height="15" fill="#B78252"/>
                <text x="150" y="275" font-family="sans-serif" font-size="12" font-weight="600" fill="#64748B" text-anchor="middle">Camel Crewneck Knit</text>
            </svg>
        '''),
        "is_analyzed": True
    }
]

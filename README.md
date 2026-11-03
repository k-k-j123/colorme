# ColorMe AI 👗✨

An intelligent wardrobe stylist and smart shopping advisor application where users upload photos of their clothes, receive tailored outfit combinations, and get strategic buying suggestions that multiply their wardrobe versatility.

Built with **flexible OpenAI-compatible vision endpoints**, allowing you to effortlessly switch between **OpenAI**, **OpenRouter**, **Groq**, **Ollama (local)**, **Together AI**, or any custom endpoint without changing code.

---

## 🌟 Features

- **🧠 Two-Phase Efficient AI Architecture (Free-Tier Friendly)**:
  - **Phase 1 (Single-Image Ingestion & Feature Extraction)**: Each garment photo is analyzed individually using a single-image vision call to extract deep attributes (garment sub-type, primary color & hex, pattern, fabric/texture, fit silhouette, formality, seasonality, and style vibes).
  - **SQLite Database Persistence**: All extracted clothing profiles are saved locally in `wardrobe.db` so they persist across reboots and never need re-uploading.
  - **Phase 2 (Zero-Image Styling & Shopping Generation)**: Outfit generation and buying recommendations receive **PURE TEXT METADATA (0 IMAGES SENT)**. This avoids multi-image token limits, prevents rate limiting, and runs blazing fast on free tier models (e.g. Google Gemini 2.0 Flash, Groq, Ollama).

- **📸 Wardrobe Photo Upload & Management**:
  - Drag-and-drop or browse multiple clothing photos (shirts, jackets, pants, shoes, accessories).
  - Images are saved locally to `uploads/` and mapped to SQLite records.
  - Color dot indicator, sub-category tags, and AI indexed status badge on every garment card.
  - 1-click **"Sample Wardrobe"** button pre-populates the database with 6 fully cataloged staples.

- **🎨 Interactive Attribute & Color Editor**:
  - Edit any AI-extracted garment property with an emphasis on **color precision**.
  - Interactive visual color swatch picker `<input type="color">` synced with hex codes and color names.
  - 13 1-click palette presets (*Crisp White, Deep Navy, Muted Olive, Warm Camel, True Black, Charcoal, Burgundy, Forest Green, etc.*).
  - Modify sub-category, pattern, fabric/texture, fit silhouette, and formality level.
  - Instant SQLite persistence and card badge refresh.

- **🎨 Tailored Outfit Suggestions**:
  - Full-look ensembles composed strictly from your uploaded garments.
  - Step-by-step pro styling execution notes (tucking techniques, sleeve cuffs, collar rules, footwear styling).
  - Color theory and proportion rationale explaining *why* the outfit works.
  - Contextualized by Occasion (*Smart Casual, Work, Date Night, Streetwear, etc.*) and Season (*Summer, Winter, Mild, Rainy*).

- **🛍️ Strategic Buying Suggestions ("Wardrobe Multipliers")**:
  - Analyzes gaps in your wardrobe to recommend 2–4 versatile pieces.
  - Explains the exact items from your current wardrobe that each new piece unlocks combinations with.
  - Priority badges (*Essential Staple*, *Versatile Layer*, *Statement Upgrade*).
  - 1-click shopping search links directly to **Google Shopping**, **Amazon**, and **ASOS**.

- **📊 Wardrobe Audit & Color Palette**:
  - Generates a visual color swatch palette of your wardrobe.
  - Computes a wardrobe versatility score (1-100).
  - Summarizes your core style aesthetic and wardrobe highlights.

- **⚡ Flexible OpenAI-Compatible Endpoints**:
  - Switch providers live in the UI or via `.env`.
  - Built-in presets for:
    - **Google AI Studio / Gemini** (`gemini-2.0-flash`, `gemini-1.5-pro`)
    - **OpenAI** (`gpt-4o-mini`, `gpt-4o`)
    - **OpenRouter** (`google/gemini-2.0-flash-001`, `meta-llama/llama-3.2-11b-vision-instruct`, `anthropic/claude-3.5-sonnet`)
    - **Groq** (`llama-3.2-11b-vision-preview`, `llama-3.2-90b-vision-preview`)
    - **Together AI** (`meta-llama/Llama-Vision-Free`)
    - **Ollama (Local)** (`llama3.2-vision`, `llava`)
    - **Custom Endpoint** (Self-hosted vLLM, LM Studio, DeepSeek, etc.)
  - Built-in **"Test Connection"** utility to verify endpoint and model availability in real-time.
  - Safe local fallback/demo mode when testing without an API key.

---

## 🚀 Quick Start

### 1. Requirements & Setup
Make sure Python 3.10+ is installed:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` or configure provider settings directly inside the web UI:

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
```

*(Note: You can also leave `.env` blank and configure your API key and base URL directly inside the Settings modal in your browser!)*

### 3. Launch the Server

```bash
python run.py
```
Open your browser to:
👉 **`http://localhost:8000`**

---

## 🔌 Switching Providers Easily

You can switch AI providers on the fly in the app UI:
1. Click the **Provider badge** in the top navigation bar (e.g. `OpenAI (gpt-4o-mini)`).
2. Choose your preferred preset or select **Custom OpenAI Endpoint**.
3. Enter your API key and target model.
4. Click **"Test Connection"** to verify the provider responds.
5. Click **"Save Changes"** — your preferences persist in your browser `localStorage`.

### Supported Provider Examples

| Provider | Base URL | Recommended Vision Model |
| :--- | :--- | :--- |
| **Google AI Studio (Gemini)** | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.0-flash` or `gemini-1.5-pro` |
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o-mini` or `gpt-4o` |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `google/gemini-2.0-flash-001` or `meta-llama/llama-3.2-11b-vision-instruct` |
| **Groq** | `https://api.groq.com/openai/v1` | `llama-3.2-11b-vision-preview` |
| **Ollama (Local)** | `http://localhost:11434/v1` | `llama3.2-vision` |
| **Together AI** | `https://api.together.xyz/v1` | `meta-llama/Llama-Vision-Free` |
| **Custom** | `http://your-server:8000/v1` | Any vision-enabled model |

---

## 📁 Project Structure

```
colorme/
├── backend/
│   ├── app.py             # FastAPI server, REST routes, static file serving
│   ├── config.py          # Provider presets and default configuration
│   ├── database.py        # SQLite database manager (wardrobe.db)
│   ├── ai_service.py      # Single-image feature extractor & zero-image styling generator
│   └── sample_data.py     # Bundled stylish garments with pre-extracted attributes
├── uploads/               # Stored uploaded garment images
├── wardrobe.db            # SQLite persistent database
├── static/
│   ├── index.html         # Responsive, luxury editorial styling UI
│   ├── css/
│   │   └── style.css      # Styling rules, pill controls, badges, animations
│   └── js/
│       └── app.js         # Client-side state, sequential single-image upload, rendering
├── .env                   # Local configuration
├── .env.example           # Environment template (includes Google AI Studio / Gemini)
├── requirements.txt       # Dependencies
└── run.py                 # Application runner
```


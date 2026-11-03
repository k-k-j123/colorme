import os
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ProviderConfig(BaseModel):
    name: str
    base_url: str
    default_model: str
    description: str
    vision_supported: bool = True
    default_api_key_env: str

# Default provider presets
PROVIDER_PRESETS: Dict[str, Dict[str, Any]] = {
    "gemini": {
        "name": "Google AI Studio (Gemini)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_model": "gemini-2.0-flash",
        "recommended_models": [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ],
        "description": "Google Gemini multimodal models via official OpenAI-compatible endpoint.",
        "default_api_key_env": "GEMINI_API_KEY",
        "doc_url": "https://aistudio.google.com/app/apikey",
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "recommended_models": ["gpt-4o-mini", "gpt-4o", "gpt-4.5-preview"],
        "description": "Industry standard multimodal GPT-4o models.",
        "default_api_key_env": "OPENAI_API_KEY",
        "doc_url": "https://platform.openai.com/api-keys",
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "google/gemini-2.0-flash-001",
        "recommended_models": [
            "google/gemini-2.0-flash-001",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.2-11b-vision-instruct",
            "anthropic/claude-3.5-sonnet"
        ],
        "description": "Multi-provider router with low latency and flexible models.",
        "default_api_key_env": "OPENROUTER_API_KEY",
        "doc_url": "https://openrouter.ai/keys",
    },
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.2-11b-vision-preview",
        "recommended_models": [
            "llama-3.2-11b-vision-preview",
            "llama-3.2-90b-vision-preview"
        ],
        "description": "Ultra-fast inference for open-source Llama vision models.",
        "default_api_key_env": "GROQ_API_KEY",
        "doc_url": "https://console.groq.com/keys",
    },
    "together": {
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "default_model": "meta-llama/Llama-Vision-Free",
        "recommended_models": [
            "meta-llama/Llama-Vision-Free",
            "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
        ],
        "description": "Open-source model hosting with OpenAI API compatibility.",
        "default_api_key_env": "TOGETHER_API_KEY",
        "doc_url": "https://api.together.ai/settings/api-keys",
    },
    "ollama": {
        "name": "Ollama (Local)",
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama3.2-vision",
        "recommended_models": ["llama3.2-vision", "llava", "bakllava", "minicpm-v"],
        "description": "Run vision models locally on your computer with 100% privacy.",
        "default_api_key_env": "",
        "doc_url": "https://ollama.com",
    },
    "custom": {
        "name": "Custom OpenAI Endpoint",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "recommended_models": [],
        "description": "Any self-hosted or compatible OpenAI chat completions endpoint (LM Studio, vLLM, DeepSeek, etc.).",
        "default_api_key_env": "",
        "doc_url": "",
    }
}

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
DEFAULT_BASE_URL = os.getenv("OPENAI_BASE_URL", PROVIDER_PRESETS.get(DEFAULT_PROVIDER, {}).get("base_url", "https://api.openai.com/v1"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", PROVIDER_PRESETS.get(DEFAULT_PROVIDER, {}).get("default_model", "gpt-4o-mini"))
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", os.getenv("OPENROUTER_API_KEY", os.getenv("GROQ_API_KEY", ""))))


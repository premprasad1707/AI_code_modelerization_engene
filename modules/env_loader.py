"""Environment loader for API keys.

This project supports multiple LLM providers. Keys can be provided either:
- via .env file (recommended for local development)
- via Streamlit sidebar (session-based storage)

This module focuses on .env loading only; Streamlit UI wiring happens elsewhere.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


PROVIDERS: tuple[str, ...] = (
    "OpenAI",
    "Groq",
    "Google Gemini",
    "Anthropic (Claude)",
    "HuggingFace",
    "OpenRouter",
)


ENV_VARS: Dict[str, str] = {
    "OpenAI": "OPENAI_API_KEY",
    "Groq": "GROQ_API_KEY",
    "Google Gemini": "GEMINI_API_KEY",
    "Anthropic (Claude)": "ANTHROPIC_API_KEY",
    "HuggingFace": "HUGGINGFACE_API_KEY",
    "OpenRouter": "OPENROUTER_API_KEY",
}


def load_env(dotenv_path: Optional[str] = None) -> None:
    """Load .env into environment variables."""
    if load_dotenv is None:
        return
    load_dotenv(dotenv_path=dotenv_path, override=False)


def get_provider_api_key(provider: str) -> Optional[str]:
    """Return API key for a provider if available from environment."""
    env_var = ENV_VARS.get(provider)
    if not env_var:
        return None
    value = os.getenv(env_var)
    if value:
        return value.strip() or None
    return None


def get_all_provider_api_keys() -> Dict[str, str]:
    """Return available provider keys from environment."""
    keys: Dict[str, str] = {}
    for provider in PROVIDERS:
        k = get_provider_api_key(provider)
        if k:
            keys[provider] = k
    return keys


def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()


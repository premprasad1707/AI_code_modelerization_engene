"""
modules/llm_router.py
Multi-provider LLM routing: OpenAI, Anthropic Claude, Groq, Gemini,
HuggingFace, OpenRouter, and Ollama (local).
"""

import streamlit as st
import requests
import json
import logging

logger = logging.getLogger(__name__)

# ── Provider registry ──────────────────────────────────────────────────────────
AVAILABLE_PROVIDERS = {
    "OpenAI": {
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "base_url": "https://api.openai.com/v1/chat/completions",
    },
    "Anthropic (Claude)": {
        "models": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"],
        "base_url": "https://api.anthropic.com/v1/messages",
    },
    "Groq": {
        "models": [
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "deepseek-r1-distill-llama-70b",
        ],
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
    },
    "Google Gemini": {
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"],
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
    },
    "HuggingFace": {
        "models": [
            "bigcode/starcoder2-15b",
            "codellama/CodeLlama-34b-Instruct-hf",
            "mistralai/Mistral-7B-Instruct-v0.3",
        ],
        "base_url": "https://api-inference.huggingface.co/models",
    },
    "OpenRouter": {
        "models": [
            "openai/gpt-4o",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-flash-1.5",
            "deepseek/deepseek-coder",
            "meta-llama/llama-3.1-70b-instruct",
            "mistralai/mistral-7b-instruct",
        ],
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
    },
    "Ollama (Local)": {
        "models": [
            "codellama",
            "llama3",
            "mistral",
            "deepseek-coder",
            "starcoder2",
            "phi3",
            "qwen2.5-coder",
        ],
        "base_url": "http://localhost:11434/api/generate",
    },
}


def _get_session_key(provider: str) -> str | None:
    """Retrieve API key from Streamlit session state."""
    return st.session_state.get("api_keys", {}).get(provider)


def _call_openai_compatible(base_url: str, api_key: str, model: str, prompt: str) -> tuple[str, str | None]:
    """Shared caller for OpenAI-compatible endpoints (OpenAI, Groq, OpenRouter)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 4096,
    }
    try:
        r = requests.post(base_url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"], None
    except requests.exceptions.RequestException as e:
        return "", str(e)
    except (KeyError, IndexError) as e:
        return "", f"Unexpected response format: {e}"


def _call_anthropic(api_key: str, model: str, prompt: str) -> tuple[str, str | None]:
    """Call Anthropic Claude API."""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["content"][0]["text"], None
    except requests.exceptions.RequestException as e:
        return "", str(e)
    except (KeyError, IndexError) as e:
        return "", f"Unexpected response format: {e}"


def _call_gemini(api_key: str, model: str, prompt: str) -> tuple[str, str | None]:
    """Call Google Gemini API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096},
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"], None
    except requests.exceptions.RequestException as e:
        return "", str(e)
    except (KeyError, IndexError) as e:
        return "", f"Unexpected response format: {e}"


def _call_huggingface(api_key: str, model: str, prompt: str) -> tuple[str, str | None]:
    """Call HuggingFace Inference API."""
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 2048, "temperature": 0.2}}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data[0].get("generated_text", ""), None
        return str(data), None
    except requests.exceptions.RequestException as e:
        return "", str(e)


def _call_ollama(base_url: str, model: str, prompt: str) -> tuple[str, str | None]:
    """Call local Ollama instance."""
    base_url = st.session_state.get("ollama_base_url", "http://localhost:11434")
    url = f"{base_url}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("response", ""), None
    except requests.exceptions.RequestException as e:
        return "", f"Ollama error (is it running?): {e}"


def get_llm_response(prompt: str) -> tuple[str, str | None]:
    """
    Route prompt to the active LLM provider.
    Returns (response_text, error_string_or_None).
    """
    provider = st.session_state.get("active_llm")
    model    = st.session_state.get("active_model")

    if not provider:
        return "", "No LLM provider configured. Go to API Keys page."
    if not model:
        return "", "No model selected."

    logger.info(f"LLM call: provider={provider}, model={model}, prompt_len={len(prompt)}")

    # Ollama doesn't need an API key
    if provider == "Ollama (Local)":
        base_url = st.session_state.get("ollama_base_url", "http://localhost:11434")
        return _call_ollama(base_url, model, prompt)

    # All other providers need a key
    api_key = _get_session_key(provider)
    if not api_key:
        return "", f"No API key set for {provider}. Go to API Keys page."

    if provider == "OpenAI":
        base_url = AVAILABLE_PROVIDERS["OpenAI"]["base_url"]
        return _call_openai_compatible(base_url, api_key, model, prompt)

    elif provider == "Anthropic (Claude)":
        return _call_anthropic(api_key, model, prompt)

    elif provider == "Groq":
        base_url = AVAILABLE_PROVIDERS["Groq"]["base_url"]
        return _call_openai_compatible(base_url, api_key, model, prompt)

    elif provider == "Google Gemini":
        return _call_gemini(api_key, model, prompt)

    elif provider == "HuggingFace":
        return _call_huggingface(api_key, model, prompt)

    elif provider == "OpenRouter":
        base_url = AVAILABLE_PROVIDERS["OpenRouter"]["base_url"]
        return _call_openai_compatible(base_url, api_key, model, prompt)

    else:
        return "", f"Unknown provider: {provider}"

"""Persistent API Key Manager for Streamlit.

- Loads API keys from .env using python-dotenv
- Saves keys permanently back to .env using set_key()
- Password-masked inputs
- Active provider selector
- Works with all LLM providers: OpenAI, Groq, Gemini, Anthropic, HuggingFace, OpenRouter, Ollama
"""

import os
import streamlit as st
from dotenv import load_dotenv, set_key

# -------------------------------------------------------
# Config
# -------------------------------------------------------
ENV_FILE = ".env"

load_dotenv(ENV_FILE)


# -------------------------------------------------------
# Save a key persistently to .env
# -------------------------------------------------------
def save_api_key(key_name: str, key_value: str) -> None:
    set_key(ENV_FILE, key_name, key_value)
    os.environ[key_name] = key_value  # also update runtime env


# -------------------------------------------------------
# Read current keys from environment
# -------------------------------------------------------
def _get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# -------------------------------------------------------
# Render page — called from app.py
# -------------------------------------------------------
def render_api_key_manager_page() -> None:
    st.header("🔑 API Key Manager")
    st.caption(
        "Keys are saved **permanently** inside the `.env` file in your project root. "
        "They survive app restarts and never need to be re-entered."
    )

    st.info(
        "✅ Saves permanently  •  ✅ Password-masked  •  ✅ Supports all providers  "
        "•  ✅ No re-entry needed  •  ✅ Production-ready"
    )

    st.divider()

    # --------------------------------------------------
    # OpenAI
    # --------------------------------------------------
    st.subheader("🟢 OpenAI")
    openai_input = st.text_input(
        "OpenAI API Key",
        value=_get_env("OPENAI_API_KEY"),
        type="password",
        key="ui_openai",
    )
    if st.button("Save OpenAI Key", key="save_openai"):
        save_api_key("OPENAI_API_KEY", openai_input)
        st.success("✅ OpenAI API Key saved to .env!")

    st.divider()

    # --------------------------------------------------
    # Groq
    # --------------------------------------------------
    st.subheader("⚡ Groq")
    groq_input = st.text_input(
        "Groq API Key",
        value=_get_env("GROQ_API_KEY"),
        type="password",
        key="ui_groq",
    )
    if st.button("Save Groq Key", key="save_groq"):
        save_api_key("GROQ_API_KEY", groq_input)
        st.success("✅ Groq API Key saved to .env!")

    st.divider()

    # --------------------------------------------------
    # Gemini
    # --------------------------------------------------
    st.subheader("✨ Google Gemini")
    gemini_input = st.text_input(
        "Gemini API Key",
        value=_get_env("GEMINI_API_KEY"),
        type="password",
        key="ui_gemini",
    )
    if st.button("Save Gemini Key", key="save_gemini"):
        save_api_key("GEMINI_API_KEY", gemini_input)
        st.success("✅ Gemini API Key saved to .env!")

    st.divider()

    # --------------------------------------------------
    # Anthropic (Claude)
    # --------------------------------------------------
    st.subheader("🟣 Anthropic (Claude)")
    anthropic_input = st.text_input(
        "Anthropic API Key",
        value=_get_env("ANTHROPIC_API_KEY"),
        type="password",
        key="ui_anthropic",
    )
    if st.button("Save Anthropic Key", key="save_anthropic"):
        save_api_key("ANTHROPIC_API_KEY", anthropic_input)
        st.success("✅ Anthropic API Key saved to .env!")

    st.divider()

    # --------------------------------------------------
    # HuggingFace
    # --------------------------------------------------
    st.subheader("🤗 HuggingFace")
    hf_input = st.text_input(
        "HuggingFace API Key",
        value=_get_env("HUGGINGFACE_API_KEY"),
        type="password",
        key="ui_hf",
    )
    if st.button("Save HuggingFace Key", key="save_hf"):
        save_api_key("HUGGINGFACE_API_KEY", hf_input)
        st.success("✅ HuggingFace API Key saved to .env!")

    st.divider()

    # --------------------------------------------------
    # OpenRouter
    # --------------------------------------------------
    st.subheader("🔀 OpenRouter")
    openrouter_input = st.text_input(
        "OpenRouter API Key",
        value=_get_env("OPENROUTER_API_KEY"),
        type="password",
        key="ui_openrouter",
    )
    if st.button("Save OpenRouter Key", key="save_openrouter"):
        save_api_key("OPENROUTER_API_KEY", openrouter_input)
        st.success("✅ OpenRouter API Key saved to .env!")

    st.divider()

    # --------------------------------------------------
    # Ollama (Local — no key needed, just base URL)
    # --------------------------------------------------
    st.subheader("🦙 Ollama (Local)")
    ollama_input = st.text_input(
        "Ollama Base URL",
        value=_get_env("OLLAMA_BASE_URL", "http://localhost:11434"),
        key="ui_ollama",
    )
    if st.button("Save Ollama URL", key="save_ollama"):
        save_api_key("OLLAMA_BASE_URL", ollama_input)
        st.success("✅ Ollama Base URL saved to .env!")

    st.divider()

    # --------------------------------------------------
    # Active Provider Selector
    # --------------------------------------------------
    st.subheader("🎯 Active Provider")
    current_provider = _get_env("ACTIVE_PROVIDER", "OpenAI")
    providers = [
        "OpenAI",
        "Groq",
        "Gemini",
        "Anthropic",
        "HuggingFace",
        "OpenRouter",
        "Ollama",
    ]
    # Default index
    default_idx = providers.index(current_provider) if current_provider in providers else 0
    provider = st.selectbox(
        "Select Active Provider",
        providers,
        index=default_idx,
        key="ui_provider",
    )
    if st.button("Save Active Provider", key="save_provider"):
        save_api_key("ACTIVE_PROVIDER", provider)
        st.success(f"✅ **{provider}** set as active provider and saved to .env!")

    st.divider()
    st.info("🔒 API keys are stored securely inside the `.env` file. Make sure `.env` is listed in your `.gitignore` so keys are never committed to source control.")

## API Key Setup

This project supports multiple LLM providers.

### 1) Configure `.env`
Copy `.env.example` to `.env` and fill in keys.

### 2) Streamlit API Key Manager
Open the Streamlit app and go to **Settings → API Key Manager**.

- Keys are stored in `st.session_state` (current session only)
- `.env` keys are loaded on page render
- Provider selection is available at the bottom of the page

### 3) Models
Model selection is handled by the existing LLM router (`modules/llm_router.py`).


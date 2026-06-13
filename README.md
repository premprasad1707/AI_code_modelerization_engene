# 🧠 CodeMigrate AI
### Multi-Language Autonomous Code Migration & Modernization Platform

**CodeMigrate AI** is a professional-grade, Streamlit-powered ecosystem designed to analyze, modernize, and migrate legacy codebases. Leveraging a hybrid approach of rule-based conversion, static security heuristics, and Machine Learning risk assessment, it provides a seamless transition from legacy environments (like Python 2) to modern, secure, and high-performance standards.

---

## 🚀 Step-by-Step Setup & Execution

### 1. Environment Preparation
Navigate to your project directory and initialize a Python 3.10+ virtual environment:

```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies (Upgrading pip/wheel prevents pandas build errors)
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 2. Start the Application

You can launch the Streamlit app simply by running:
```powershell
streamlit run app.py
```

### 3. Open in Your Browser

The app should automatically open in your default browser. If it doesn't, navigate to the local URL provided in the terminal (usually `http://localhost:8501`).

*(Optional)* If you need to specify a port manually, you can use:
```powershell
streamlit run app.py --server.port 8503
```

---

## What this app does (current capabilities)

- Detects language + legacy-style patterns (Python 2 focus)
- Converts common Python 2 syntax to Python 3 (rule-based)
- Computes metrics (lines/functions/classes/imports)
- Estimates migration risk (existing ML/rule model)
- Runs basic static security heuristics
- Suggests modernization steps + a simple roadmap
- Extracts dependency modernization hints
- Saves migration history to SQLite

---

## Main navigation pages

- **Home**: overview
- **Upload & Migrate**: analyze code via upload, ZIP, GitHub import, PDF/DOCX extraction, or pasted code
- **Advanced Analysis Center**: deeper inspection of issues, security signals, dependency hints, runtime warnings
- **Analytics Dashboard**: charts based on saved history
- **Migration History**: view stored runs
- **ML Risk Model**: retrain sample risk model
- **Settings → API Key Manager**: store provider keys for the current Streamlit session

---

## API keys

See **README_API_KEYS.md** for provider + `.env` setup.

---

## Project layout

```text
codemigrate_ai/
├── app.py
├── requirements.txt
├── README.md
├── README_API_KEYS.md
├── modules/
│   ├── advanced_engine.py
│   ├── analyzer.py
│   ├── api_key_manager.py
│   ├── converter.py
│   ├── database.py
│   ├── dependency_analyzer.py
│   ├── env_loader.py
│   ├── github_integration.py
│   ├── input_handler.py
│   ├── language_detector.py
│   ├── llm_router.py
│   ├── report_generator.py
│   ├── risk_model.py
│   └── security_scanner.py
├── reports/
├── sample_files/
└── assets/
```

---

## Notes

- Migration engine is intentionally lightweight/rule-based right now.
- SQLite DB is created automatically when the app runs.
- Install dependencies from `requirements.txt` before first run.

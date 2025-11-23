# 🎤 AI Speech Evaluator

**Automated, rubric-driven scoring system** that evaluates student spoken-introduction transcripts and returns a clear, coachable score (0–100) with per-criterion breakdowns and actionable feedback.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-UI-yellowgreen" alt="Streamlit" />
  <img src="https://img.shields.io/badge/NLP-Rule%2Bheuristic-orange" alt="NLP" />
  <img src="https://img.shields.io/badge/Status-Ready-success" alt="Status" />
</p>

---

## 📘 Project Summary

This repository implements the **Nirmaan Education case-study**: a tool that accepts a **transcript** (text) and evaluates it against the official rubric. Scores & feedback are generated for:

* **Salutation Level** (greeting quality)
* **Keyword Presence** (name, age, class, school, family, hobbies, etc.)
* **Flow** (salutation → basic details → extras → closing)
* **Speech Rate** (WPM bands)
* **Grammar** (language-tool when available; heuristic fallback)
* **Vocabulary richness** (TTR)
* **Filler words rate** (clarity)
* **Engagement / Sentiment** (VADER or fallback)

The final score is normalized to **0–100** and displayed in a premium Streamlit UI.

---

## 🧭 Quick Preview (sample)

**Sample transcript (input)**  
> "Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. I am 13 years old... Thank you for listening."

**Sample output (JSON)**

```json
{
  "overall_score": 72.5,
  "criteria": [
    { "criterion": "Salutation Level", "score": 4.0, "weight": 5, "details": { "label": "Good" } },
    { "criterion": "Keyword Presence", "score": 26.0, "weight": 30, "details": { "found_must": 5, "found_optional": 2 } },
    { "criterion": "Flow (Order)", "score": 4.0, "weight": 5, "details": {} },
    { "criterion": "Speech Rate (WPM)", "score": 10.0, "weight": 10, "details": { "wpm": 151 } },
    { "criterion": "Grammar Errors", "score": 8.5, "weight": 10, "details": {} },
    { "criterion": "Vocabulary Richness", "score": 7.0, "weight": 10, "details": {} },
    { "criterion": "Filler Word Rate", "score": 13.0, "weight": 15, "details": {} },
    { "criterion": "Sentiment / Positivity", "score": 9.0, "weight": 15, "details": {} }
  ]
}
```

---

## 📁 Repository structure

```
├─ app/
│  ├─ scorer.py             # Core scoring logic (keyword, flow, grammar, filler, sentiment)
│  ├─ rubric_loader.py      # Loads rubric xlsx (weights, optional params)
│  └─ __init__.py
├─ rubric/
│  └─ rubric_for_nirmaan.xlsx
├─ sample_data/
│  └─ Sample text for case study.txt
├─ frontend_app.py          # Streamlit UI (premium layout)
├─ execution.py             # Execution helper / local runner
├─ requirements.txt
├─ DESIGN.md
└─ README.md                # <-- this file
```

---

## ⚙️ Requirements

Add the following to your `requirements.txt`:

```
streamlit
pandas
openpyxl
nltk
vaderSentiment
altair
```

Optional (for advanced grammar checks — requires Java):

```
language_tool_python
```

> Note: If you don't want to install Java, the code uses a robust heuristic fallback for grammar checks.

---

## 🚀 Quick Start (local)

1. Create a venv and activate it (recommended):

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Verify Rubric File: Ensure the rubric file is placed at: `rubric/rubric_for_nirmaan.xlsx`.

4. Run the Streamlit app:

```bash
streamlit run frontend_app.py
```

Open the URL shown in the terminal (usually [http://localhost:8501](http://localhost:8501)).

---

## 🔧 Important notes & troubleshooting

### Grammar tool warnings

If you install `language_tool_python` and see an error complaining about Java, you must install Java (OpenJDK 11+). If you do not want Java, keep `language_tool_python` uninstalled — the scorer will automatically switch to a fallback heuristic.

### VADER Sentiment

VADER is a lightweight sentiment tool that works well for short transcripts. If you have network constraints or want a different sentiment engine, the code offers a fallback simple rule-based positive-word detector.

### NLTK data

The first run may attempt to auto-download the punkt tokenizer. If your environment blocks downloads, run this once with a network connection:

```python
import nltk
nltk.download('punkt')
```

---

## 🧩 Design decisions (high-level)

- **Rule-first approach:** The rubric specifies explicit checks (keywords, WPM bands, filler counts), so rules + regex are clearer, explainable, and faster to run than large LLMs for this specific use case.

- **Heuristics + graceful fallbacks:** Where third-party tools require extra system setup (Java), we provide safe fallbacks so the app is runnable in simple student/dev environments without complex configuration.

- **Modular & configurable:** Weights and optional parameters are read from `rubric_for_nirmaan.xlsx`. You can tune weights/thresholds directly in Excel without changing the Python code.

- **Transparency:** Results include debug details per criterion so a reviewer or teacher can inspect exactly how each score was computed.

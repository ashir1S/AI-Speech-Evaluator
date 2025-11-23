<p align="center">
  <img src="/mnt/data/b80e06dd-85ea-42cc-96ee-103f4b578063.png" width="100%" alt="Hero image"/>
</p>

# 🎤 AI Speech Evaluator

**Automated, rubric-driven evaluator for student spoken introductions** — built for the Nirmaan Education case study.

A compact, reviewer-friendly tool that accepts a transcript (paste or sample file), evaluates it against the official rubric, and returns a per-criterion breakdown plus a 0–100 normalized final score.

---

## 🔎 Project summary

This project scores a student introduction on the rubric categories:

- **Salutation Level** (greeting quality)  
- **Keyword Presence** (name, age, class/school, family, hobbies)  
- **Flow / Structure** (Salutation → Basic Info → Details → Closing)  
- **Speech Rate (WPM)**  
- **Grammar (errors per 100 words)**  
- **Vocabulary richness (TTR / Type-Token Ratio)**  
- **Filler-word rate** (um / uh / like / etc.)  
- **Engagement / Sentiment** (VADER compound)

Output: JSON-like results used to render a Streamlit dashboard that shows final score, per-criterion scores, and technical details for debugging.

---

## ✅ What's in this repo

.
├─ frontend_app.py # Streamlit UI (dashboard)
├─ execution.py # entry / runner (you renamed main.py -> execution.py)
├─ requirements.txt
├─ README.md # <-- you are reading the improved README
├─ design.md # architecture & decisions
├─ Sample text for case study.txt
├─ rubric/
│ └─ rubric_for_nirmaan.xlsx
└─ app/
├─ scorer.py # core scoring logic
└─ rubric_loader.py
---

## 🚀 Quickstart (recommended)

1. Create & activate a virtual environment (recommended):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
<p align="center">
<img src="/mnt/data/b80e06dd-85ea-42cc-96ee-103f4b578063.png" alt="Banner" width="100%"/>
</p>

🎤 AI Spoken Introduction Evaluator

Automated, rubric-driven scoring system that evaluates student spoken-introduction transcripts and returns a clear, coachable score (0–100) with per-criterion breakdowns and actionable feedback.

<p align="center">
<img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python"/>
<img src="https://img.shields.io/badge/Streamlit-UI-yellowgreen" alt="Streamlit"/>
<img src="https://img.shields.io/badge/NLP-Rule%2Bheuristic-orange" alt="NLP"/>
<img src="https://img.shields.io/badge/Status-Ready-success" alt="Status"/>
</p>

📘 Project Summary

This repository implements the Nirmaan Education case-study: a tool that accepts a transcript (text) and evaluates it against the official rubric. Scores & feedback are generated for:

Salutation Level (greeting quality)

Keyword Presence (name, age, class, school, family, hobbies, etc.)

Flow (salutation → basic details → extras → closing)

Speech Rate (WPM bands)

Grammar (language-tool when available; heuristic fallback)

Vocabulary richness (TTR)

Filler words rate (clarity)

Engagement / Sentiment (VADER or fallback)

The final score is normalized to 0–100 and displayed in a premium Streamlit UI.

🧭 Quick Preview (sample)

Sample transcript (input)

"Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. I am 13 years old... Thank you for listening."

Sample output (JSON)

{
  "overall_score": 72.5,
  "criteria": [
    {"criterion":"Salutation Level","score":4.0,"weight":5,"details":{"label":"Good"}},
    {"criterion":"Keyword Presence","score":26.0,"weight":30,"details":{"found_must":5,"found_optional":2}},
    {"criterion":"Flow (Order)","score":4.0,"weight":5,"details":{}},
    {"criterion":"Speech Rate (WPM)","score":10.0,"weight":10,"details":{"wpm":151}},
    {"criterion":"Grammar Errors","score":8.5,"weight":10,"details":{}},
    {"criterion":"Vocabulary Richness","score":7.0,"weight":10,"details":{}},
    {"criterion":"Filler Word Rate","score":13.0,"weight":15,"details":{}},
    {"criterion":"Sentiment / Positivity","score":9.0,"weight":15,"details":{}}
  ]
}


📁 Repository structure

├─ app/
│  ├─ scorer.py             # Core scoring logic (keyword, flow, grammar, filler, sentiment)
│  ├─ rubric_loader.py      # Loads rubric xlsx (weights, optional params)
│  └─ __init__.py
├─ rubric/
│  └─ rubric_for_nirmaan.xlsx
├─ sample_data/
│  └─ Sample text for case study.txt
├─ frontend_app.py          # Streamlit UI (premium layout)
├─ execution.py             # Execution helper / local runner (you renamed main -> execution)
├─ requirements.txt
├─ DESIGN.md
└─ README.md                # <-- this file


⚙️ Requirements (recommended)

Add this to requirements.txt:

streamlit
pandas
openpyxl
nltk
vaderSentiment
altair


Optional (advanced grammar checks — requires Java):

language_tool_python


If you don't want to install Java, the code uses a robust heuristic fallback for grammar checks (no Java required).

🚀 Quick Start (local)

1. Create a venv and activate it (recommended):

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate


2. Install dependencies:

pip install -r requirements.txt


3. Setup Rubric:
Download or place the rubric file at: rubric/rubric_for_nirmaan.xlsx.

4. Run the Streamlit app:

streamlit run frontend_app.py


Open the URL shown in terminal (default http://localhost:8501).

🔧 Important notes & troubleshooting

Grammar tool warnings

If you install language_tool_python and see an error complaining about Java, you must install Java (OpenJDK 11+). If you do not want Java, keep language_tool_python uninstalled — the scorer will use a fallback heuristic instead.

VADER

VADER is a light-weight sentiment tool that works well for short transcripts. If you have network constraints or want a different sentiment engine, the code offers a fallback simple rule-based positive-word detector.

NLTK data

The first run may auto-download punkt tokenizer. If the environment blocks downloads, run once with network or pre-download NLTK punkt:

import nltk
nltk.download('punkt')


🧩 Design decisions (high-level)

Rule-first approach: The rubric specifies explicit checks (keywords, WPM bands, filler counts), so rules + regex is clearer, explainable, and fast to run for reviewers.

Heuristics + graceful fallbacks: Where third-party tools require extra system setup (Java), we provide safe fallbacks so the app is runnable in simple student/dev environments.

Modular & configurable: We read weights and optional params from rubric_for_nirmaan.xlsx. You can tune weights/thresholds without changing code.

Transparency: Results include debug details per criterion so a reviewer or teacher can inspect how each score was computed.
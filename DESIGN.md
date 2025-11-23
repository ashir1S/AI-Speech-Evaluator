# AI Spoken Introduction Evaluator — Design Document

## 1. Problem Overview
Students submit short spoken introductions, and teachers need a fast way to evaluate:

- Content completeness  
- Structure & flow  
- Grammar  
- Vocabulary richness  
- Speech rate  
- Positivity / confidence  
- Clarity (filler words)

Manually scoring thousands of introductions is slow and inconsistent.  
This system automates the evaluation using the rubric provided by Nirmaan Education.

---

## 2. High-Level Approach
The system accepts a transcript and evaluates it across eight rubric categories:

1. Salutation level  
2. Keyword completeness  
3. Structural flow  
4. Speech rate  
5. Grammar  
6. Vocabulary richness  
7. Filler words  
8. Sentiment (positivity)

Each metric produces a rubric-scaled score.  
Final output = weighted composite score (0–100).

---

## 3. System Architecture

            +---------------------------+
            |       Streamlit UI        |
            |    (frontend_app.py)      |
            +------------+--------------+
                         |
                         v
            +---------------------------+
            |      Evaluation Core      |
            |       (scorer.py)         |
            +------------+--------------+
                         |
      +------------------+-------------------+
      |          |             |             |
      v          v             v             v
                         |
                         v
            +---------------------------+
            |   Weighted Score Engine   |
            +------------+--------------+
                         |
                         v
            +---------------------------+
            |       Final Output        |
            | Score + Breakdown + Debug |
            +---------------------------+

---

## 4. Files Included

| File | Purpose |
|------|---------|
| `frontend_app.py` | Streamlit interface for transcript input and result visualization |
| `app/scorer.py` | Core evaluation logic (keywords, grammar, flow, sentiment) |
| `app/rubric_loader.py` | Imports weight values from rubric Excel file |
| `rubric/rubric_for_nirmaan.xlsx` | Official scoring weights |
| `Sample text for case study.txt` | Provided test transcript |
| `execution.py` | Backend runner for debugging |
| `design.md` | System design explanation |

---

## 5. Metric Design Decisions

### 5.1 Keyword Detection
Instead of checking literal tokens like “age”, the evaluator uses semantic patterns:

- “I am 13”
- “years old”
- “studying in class”
- “my father / mother”
- “I enjoy playing cricket”

This prevents false negatives and aligns with natural speech.

---

### 5.2 Flow Detection
Flow is evaluated using a positional model:

1. Salutation  
2. Basic details (name, age, class, school)  
3. Optional details (family, hobbies, goals, fun facts)  
4. Closing (“Thank you”)  

We compute average positions of each category and award partial credit when ordering is mostly correct.

---

### 5.3 Speech Rate (WPM)

Mapped directly to rubric values:

- 111–140 → 10 pts (ideal)  
- 141–160 or 81–110 → 6 pts  
- >161 or <80 → 2 pts  

---

### 5.4 Grammar Scoring
A hybrid approach:

1. **Uses language_tool_python** if available  
2. Falls back to a **lightweight heuristic**:
   - Sentences starting without capitalization  
   - Repeated words (e.g., “the the”)  
   - Lowercase “i”  

The fallback ensures scoring works without Java.

---

### 5.5 Vocabulary (TTR)
Using Type Token Ratio:


Mapped to rubric thresholds:

- 0.9–1.0 → 10 pts  
- 0.7–0.89 → 8 pts  
- 0.5–0.69 → 6 pts  
- 0.3–0.49 → 4 pts  
- <0.3 → 2 pts  

---

### 5.6 Filler Words
Matches against a standard filler list:

- “um”, “uh”, “like”, “you know”, “basically”, etc.

Score is based on percentage of filler words relative to total words.

---

### 5.7 Sentiment
Uses VADER’s **compound** score (not raw positive score).

- ≥ 0.5 → 15 pts  
- 0.3–0.49 → 12 pts  
- 0.1–0.29 → 9 pts  
- −0.1–0.09 → 6 pts  
- < −0.1 → 3 pts  

This matches natural student intros more accurately.

---

## 6. Why These Tools?

| Tool | Reason |
|------|--------|
| **Python** | Easy NLP development |
| **Streamlit** | Clean UI and rapid prototyping |
| **VADER** | Reliable sentiment on short texts |
| **Regex keyword model** | Transparent and predictable |
| **Fallback grammar heuristic** | Removes dependency on Java |
| **Pandas** | Easy rubic-to-weight mapping |

---

## 7. Limitations
- Transcript-only (no audio processing yet)  
- Grammar heuristic less precise without LanguageTool  
- Flow scoring depends on detectable phrases  

---

## 8. Future Improvements
- Integrate speech-to-text  
- Add BERT/transformer-based semantic evaluation  
- Provide personalized written feedback  
- Provide category-wise improvement suggestions  
- Allow batch scoring for classrooms  

---

## 9. Conclusion
This tool delivers a complete, efficient, and rubric-aligned automated evaluator for student introductions.  
It ensures fairness, consistency, and easy integration with Nirmaan’s ecosystem.

---

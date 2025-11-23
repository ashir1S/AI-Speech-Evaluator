import streamlit as st
import altair as alt
import pandas as pd
import re
import json
from datetime import datetime

st.set_page_config(page_title="Speech Evaluator", layout="wide", page_icon="🎤")


# -------------------------------------------
# Simple scoring function
# -------------------------------------------
def evaluate_simple(text):
    words = len(re.findall(r"\w+", text))
    score = min(100, max(5, int(words * 0.65)))

    criteria = [
        {"criterion": "Clarity", "score": score - 5},
        {"criterion": "Grammar", "score": score - 8},
        {"criterion": "Fluency", "score": score - 3},
        {"criterion": "Content", "score": score},
    ]

    # sanitize values
    for c in criteria:
        if not isinstance(c, dict):
            c = {"criterion": "Unknown", "score": 0}
        c["score"] = max(0, min(100, int(c["score"])))

    return {"overall_score": score, "criteria": criteria}


# -------------------------------------------
# UI Header
# -------------------------------------------
st.title("🎤 AI Speech Evaluator")
st.write("Paste text below or upload a .txt file.")


# -------------------------------------------
# Input area
# -------------------------------------------
text = st.text_area("Enter your transcript here:", height=200)

uploaded_txt = st.file_uploader("Upload .txt file", type=["txt"])

if uploaded_txt:
    try:
        text = uploaded_txt.read().decode("utf-8")
    except:
        st.error("Error reading txt file. Ensure UTF-8 encoding.")


# -------------------------------------------
# Live stats
# -------------------------------------------
words = len(re.findall(r"\w+", text))
sentences = len(re.findall(r"[.!?]+", text))
duration_sec = int(words / 1.5) if words else 0  # smoother speaking rate

st.markdown("### 📝 Live Stats")
st.write(f"**Word Count:** {words}")
st.write(f"**Sentence Count:** {sentences}")
st.write(f"**Estimated Duration (seconds):** {duration_sec}")


# -------------------------------------------
# Evaluate
# -------------------------------------------
if st.button("Evaluate"):

    if not text.strip():
        st.warning("Enter text or upload a .txt file before evaluating.")
        st.stop()

    result = evaluate_simple(text)

    st.subheader("Final Score")

    colA, colB = st.columns([1, 2])

    # number metric
    with colA:
        st.metric("Overall Score", f"{result['overall_score']} / 100")

    # -------------------------------------------
    # ⭐ DONUT GAUGE CHART ⭐
    # -------------------------------------------
    with colB:
        gauge_df = pd.DataFrame({
            "part": ["score", "remaining"],
            "value": [result["overall_score"], 100 - result["overall_score"]],
        })

        donut = (
            alt.Chart(gauge_df)
            .mark_arc(innerRadius=60)
            .encode(
                theta="value:Q",
                color=alt.Color(
                    "part:N",
                    scale=alt.Scale(
                        domain=["score", "remaining"],
                        range=["#4ade80", "#e5e7eb"]  # green + grey
                    ),
                ),
                tooltip=["part", "value"],
            )
            .properties(width=300, height=220)
        )

        st.altair_chart(donut, use_container_width=False)


    # Criteria DataFrame
    df = pd.DataFrame(result["criteria"])

    # -------------------------------------------
    # 1) Horizontal Bar Chart (first)
    # -------------------------------------------
    st.subheader("📊 Criterion Performance (Bar Chart)")

    bar = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("score:Q", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("criterion:N", sort="-x"),
            tooltip=["criterion", "score"],
        )
        .properties(height=260)
    )

    st.altair_chart(bar, use_container_width=True)

    # -------------------------------------------
    # 2) Line Chart (second)
    # -------------------------------------------
    st.subheader("📈 Score Trend (Line Chart)")

    line_df = df.reset_index().rename(columns={"index": "order"})

    line = (
        alt.Chart(line_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("order:O", title="Criterion Order"),
            y=alt.Y("score:Q", title="Score"),
            tooltip=["criterion", "score"],
        )
        .properties(height=260)
    )

    st.altair_chart(line, use_container_width=True)

    # -------------------------------------------
    # JSON download
    # -------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_json = json.dumps(result, indent=2)

    st.download_button(
        "Download Results JSON",
        result_json,
        file_name=f"evaluation_{timestamp}.json",
        mime="application/json",
    )

"""
app.py — Phase 3 of the AI Quiz Generator.

Streamlit UI. Decides which of three screens to show based on session_state:

  | questions   | submitted | Screen shown      |
  |-------------|-----------|-------------------|
  | None        | (any)     | Upload + Generate |
  | has data    | False     | Take the quiz     |
  | has data    | True      | Results           |
"""

import streamlit as st

from pptx_parser import extract_text_from_pptx
from ai_generator import generate_mcqs


st.set_page_config(page_title="AI Quiz Generator", page_icon="🎯")
st.title("🎯 AI Quiz Generator")
st.caption("Upload a PowerPoint and get an instant multiple-choice quiz.")

# --- Session state setup ---
# Streamlit re-runs the WHOLE script on every interaction (clicks, slider changes,
# etc.), so any variable you want to remember between interactions must live in
# st.session_state. Think of it as the app's memory.
if "questions" not in st.session_state:
    st.session_state.questions = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "answers" not in st.session_state:
    st.session_state.answers = {}


# --- Screen 1: Upload + configure ---
if st.session_state.questions is None:
    uploaded_file = st.file_uploader("Upload a .pptx file", type=["pptx"])
    num_questions = st.slider("Number of questions", min_value=5, max_value=30, value=10)

    if uploaded_file and st.button("Generate Quiz", type="primary"):
        with st.spinner("Reading your slides..."):
            study_text = extract_text_from_pptx(uploaded_file)
        with st.spinner(f"Writing {num_questions} questions..."):
            st.session_state.questions = generate_mcqs(study_text, num_questions)
        st.rerun()


# --- Screen 2: Take the quiz ---
elif not st.session_state.submitted:
    st.subheader("Take the quiz")
    with st.form("quiz_form"):
        for i, q in enumerate(st.session_state.questions):
            st.markdown(f"**Q{i + 1}. {q['question']}**")
            choice = st.radio(
                f"Select an answer for Q{i + 1}",
                options=range(len(q["options"])),
                format_func=lambda x, opts=q["options"]: f"{chr(65 + x)}. {opts[x]}",
                key=f"q_{i}",
                label_visibility="collapsed",
            )
            st.session_state.answers[i] = choice
            st.divider()

        if st.form_submit_button("Submit Quiz", type="primary"):
            st.session_state.submitted = True
            st.rerun()


# --- Screen 3: Results ---
else:
    correct = sum(
        1 for i, q in enumerate(st.session_state.questions)
        if st.session_state.answers.get(i) == q["correct_index"]
    )
    total = len(st.session_state.questions)
    st.subheader(f"Your score: {correct} / {total}")
    st.progress(correct / total)

    for i, q in enumerate(st.session_state.questions):
        user_idx = st.session_state.answers.get(i)
        correct_idx = q["correct_index"]
        is_right = user_idx == correct_idx

        with st.expander(f"{'✅' if is_right else '❌'} Q{i + 1}. {q['question']}"):
            for j, opt in enumerate(q["options"]):
                prefix = chr(65 + j)
                if j == correct_idx:
                    st.success(f"**{prefix}. {opt}** (correct answer)")
                elif j == user_idx:
                    st.error(f"{prefix}. {opt} (your answer)")
                else:
                    st.write(f"{prefix}. {opt}")
            st.info(f"💡 {q.get('explanation', '')}")

    if st.button("Start over"):
        st.session_state.questions = None
        st.session_state.submitted = False
        st.session_state.answers = {}
        st.rerun()

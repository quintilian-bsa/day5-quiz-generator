# AI Quiz Generator

A Streamlit app that turns any PowerPoint into a multiple-choice quiz using AI.
Built for **TechVest Academy Day 5 — Application Build** by Paul Quintilian.

## Deliverables

| # | Deliverable | Link |
|---|---|---|
| 1 | **Source code (GitHub)** | https://github.com/quintilian-bsa/day5-quiz-generator |
| 2 | **Live deployed app** | https://day5-quiz-generator-vcnmgghui8jrn66nyxxnpa.streamlit.app |
| 3 | **Project report (PDF)** | [`Project_Report.pdf`](Project_Report.pdf) |
| 4 | **5-minute video demo** | https://youtu.be/S-yDgB9ZBac |

## What it does

1. You upload a `.pptx` file.
2. The app pulls the text out of every slide.
3. An LLM (via OpenRouter, using Anthropic Claude Haiku 4.5) writes multiple-choice questions about that content.
4. You configure the quiz: number of questions (5–30) and difficulty (Simple / Medium / Complex).
5. You take the quiz in your browser, get a score, and see AI-generated explanations for any wrong answers.

## Architecture

Three small Python files, each with one job:

| File | Responsibility |
|---|---|
| `pptx_parser.py` | Read a `.pptx` and return all its text |
| `ai_generator.py` | Send text to an LLM, return MCQs as JSON |
| `app.py` | Streamlit UI: Upload → Quiz → Results |

Plus supporting files:

| File | Purpose |
|---|---|
| `requirements.txt` | Python dependencies for Streamlit Cloud deployment |
| `.gitignore` | Keeps the `.env` file (containing the API key) out of git |
| `Day5_Application_Build.pptx` | Sample input deck (the assignment itself) |

## Run it locally

```bash
# 1. Create a Python 3.11 venv (the course requires this exact version)
uv venv --python 3.11
source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Set your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env

# 4. Launch
streamlit run app.py
```

Your browser will open to `http://localhost:8501`.

## Functional requirements (per assignment slide 5) — all delivered

- **FR-01** — `.pptx` upload & full-deck text extraction
- **FR-02** — Configurable question count (5–30) + difficulty dropdown (Simple / Medium / Complex)
- **FR-03** — AI-generated MCQs with exactly 4 options per question
- **FR-04** — Quiz interface with one question at a time, single-answer radio selection
- **FR-05** — Score + per-question feedback including correct answer and AI-generated explanation for wrong answers
- **FR-06** — Clean, responsive Streamlit UI with loading indicators and wide layout

## Out of scope (per assignment slide 3)

- Audio / video file inputs
- Essay / open-ended questions
- User authentication
- Multi-language support

# AI Quiz Generator

A Streamlit app that turns any PowerPoint into a multiple-choice quiz using AI.
Built for TechVest Academy Day 5 — Application Build.

## What it does

1. You upload a `.pptx` file.
2. The app pulls the text out of every slide.
3. An LLM (via OpenRouter) writes multiple-choice questions about that content.
4. You take the quiz in your browser, get a score, and see explanations for any wrong answers.

## Architecture

Three small Python files, each with one job:

| File | Responsibility |
|---|---|
| `pptx_parser.py` | Read a `.pptx` and return all its text |
| `ai_generator.py` | Send text to an LLM, return MCQs as JSON |
| `app.py` | Streamlit UI: Upload → Quiz → Results |

## Run it locally

```bash
# 1. Create a Python 3.11 venv (the course requires this exact version)
uv venv --python 3.11
source .venv/bin/activate

# 2. Install dependencies
uv pip install streamlit python-pptx openai python-dotenv

# 3. Set your OpenRouter API key
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env

# 4. Launch
streamlit run app.py
```

Your browser will open to `http://localhost:8501`.

## Scope (MVP shipped)

In scope tonight:
- `.pptx` upload & text extraction
- AI-generated MCQs (4 options each)
- Configurable question count (5–30)
- Score + per-question feedback with the correct answer highlighted

Out of scope tonight (planned bonus work):
- Difficulty levels (Simple / Medium / Complex)
- Deeper AI explanations per wrong answer (second LLM call)
- Deployment to a public URL
- Project report PDF + 5-minute video demo

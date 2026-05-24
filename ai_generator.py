"""
ai_generator.py — Phase 2 of the AI Quiz Generator.

Single responsibility: given study text + a question count, ask an LLM
(via OpenRouter) to return multiple-choice questions as strict JSON.
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load OPENROUTER_API_KEY from the .env file into the environment.
load_dotenv()

# We use the OpenAI Python SDK but POINT IT AT OpenRouter.
# OpenRouter speaks the OpenAI API "language" so the same SDK works.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Free tier model on OpenRouter. If this one is rate-limited, try:
#   "anthropic/claude-haiku-4-5"
#   "deepseek/deepseek-chat-v3.1:free"
MODEL = "anthropic/claude-haiku-4-5"

SYSTEM_PROMPT = """You are an expert question writer. Given study material, you produce \
multiple-choice questions in strict JSON format.

You MUST respond with ONLY a JSON array. No prose, no markdown, no code fences.
Each item in the array is an object with exactly these keys:
- "question": the question text (string)
- "options": an array of EXACTLY 4 strings labeled A, B, C, D in order
- "correct_index": an integer 0, 1, 2, or 3 indicating which option is correct
- "explanation": a one-sentence explanation of why the correct answer is right

Distractors (wrong options) must be plausible but clearly wrong on careful reading.
"""


def generate_mcqs(study_text: str, num_questions: int) -> list[dict]:
    """Ask the AI to write `num_questions` MCQs based on `study_text`.

    Returns a list of dicts, each shaped like:
      {"question": "...", "options": ["A...","B...","C...","D..."],
       "correct_index": 2, "explanation": "..."}
    """
    user_prompt = (
        f"Write {num_questions} multiple-choice questions based on this study material. "
        f"Return ONLY the JSON array.\n\n"
        f"STUDY MATERIAL:\n{study_text}"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,  # Low = consistent JSON, high enough = varied questions.
    )

    raw = response.choices[0].message.content.strip()

    # Defensive: even with strong instructions, some models wrap JSON in ``` fences.
    # Strip them if present so json.loads() doesn't choke.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    questions = json.loads(raw)
    return questions


if __name__ == "__main__":
    # Quick command-line test. Reads the assignment deck and prints 5 questions.
    from pptx_parser import extract_text_from_pptx

    text = extract_text_from_pptx("Day5_Application_Build.pptx")
    questions = generate_mcqs(text, 5)
    print(json.dumps(questions, indent=2))

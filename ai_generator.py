"""
ai_generator.py — Phase 2 of the AI Quiz Generator.

Single responsibility: given study text + a question count, ask an LLM
(via OpenRouter) to return multiple-choice questions as strict JSON.
"""

import json
import os
import re
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
#   "google/gemini-2.0-flash-exp:free"
#   "deepseek/deepseek-chat-v3.1:free"
MODEL = "anthropic/claude-haiku-4-5"

SYSTEM_PROMPT = """You are an expert question writer. Given study material, you produce \
multiple-choice questions in strict JSON format.

You MUST respond with ONLY a JSON array. No prose, no markdown, no code fences.
Each item in the array is an object with exactly these keys:
- "question": the question text (string)
- "options": an array of EXACTLY 4 strings. Provide ONLY the raw answer text.
  DO NOT prefix each option with "A)", "B)", "A.", "B.", or any letter label.
  The user interface adds the A/B/C/D labels automatically. The order of the
  array determines which option is A, B, C, and D.
- "correct_index": an integer 0, 1, 2, or 3 indicating which option is correct
  (0 = first option = "A", 1 = "B", 2 = "C", 3 = "D")
- "explanation": a one-sentence explanation of why the correct answer is right

Distractors (wrong options) must be plausible but clearly wrong on careful reading.

Difficulty calibration (the user will tell you which level to write at):
- "Simple": questions test direct recall of facts explicitly stated in the material. Distractors are obviously different from the correct answer; a student who skimmed the deck once should get them.
- "Medium": questions test comprehension and the relationships between concepts. Distractors are plausible misreadings of the material.
- "Complex": questions test synthesis across multiple slides or sections. Distractors require careful reading to rule out, and the correct answer may require connecting two pieces of the material.
"""


def generate_mcqs(study_text: str, num_questions: int, difficulty: str = "Medium") -> list[dict]:
    """Ask the AI to write `num_questions` MCQs based on `study_text` at the given difficulty.

    Args:
        study_text: The text extracted from the source material.
        num_questions: How many MCQs to generate (5–30 enforced upstream by the UI).
        difficulty: One of "Simple", "Medium", "Complex". Defaults to "Medium".

    Returns a list of dicts, each shaped like:
      {"question": "...", "options": ["A...","B...","C...","D..."],
       "correct_index": 2, "explanation": "..."}
    """
    user_prompt = (
        f"Write {num_questions} multiple-choice questions at \"{difficulty}\" difficulty "
        f"based on this study material. Return ONLY the JSON array.\n\n"
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

    # Defensive cleanup: strip any "A)", "B)", "A.", "B.", "A:", etc. prefix the
    # model may have added to option text, since the UI adds its own A/B/C/D labels.
    # Without this, options render as "A. A) Creating quiz questions..." — doubled.
    for q in questions:
        if "options" in q:
            q["options"] = [_strip_option_prefix(opt) for opt in q["options"]]

    return questions


_OPTION_PREFIX_RE = re.compile(r"^\s*[A-Da-d]\s*[).:\-]\s*")


def _strip_option_prefix(text: str) -> str:
    """Remove any leading 'A)', 'B.', 'C:', etc. from option text.

    Examples:
      "A) The right answer"  -> "The right answer"
      "B. Another option"    -> "Another option"
      "Clean text already"   -> "Clean text already"
    """
    return _OPTION_PREFIX_RE.sub("", text).strip()


if __name__ == "__main__":
    # Quick command-line test. Reads the assignment deck and prints 5 Complex-difficulty questions.
    from pptx_parser import extract_text_from_pptx

    text = extract_text_from_pptx("Day5_Application_Build.pptx")
    questions = generate_mcqs(text, 5, "Complex")
    print(json.dumps(questions, indent=2))

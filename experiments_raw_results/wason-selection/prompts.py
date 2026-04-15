from __future__ import annotations

SYSTEM_PROMPT = """You are a logic expert analyzing conditional rules.
Your task is to identify which cards must be turned over to check if a rule is violated.

CRITICAL INSTRUCTIONS:
- Respond ONLY with the selected cards as a comma-separated list
- NO explanations, NO reasoning, NO JSON, NO other text
- Example: A, 4
- Another example: K, 7, A"""

NEUTRAL_MINIMAL_PROMPT = """Respond ONLY with card labels as a comma-separated list.
No explanations."""

COT_ANSWER_PROMPT = """You are a logic expert analyzing conditional rules.
Think step by step before answering.
After reasoning, output your final answer on the last line as:
ANSWER: card1, card2"""

PROMPT_VARIANTS = {
    "default": SYSTEM_PROMPT,
    "neutral_minimal": NEUTRAL_MINIMAL_PROMPT,
    "cot_answer": COT_ANSWER_PROMPT,
}

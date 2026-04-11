"""
Tool: openrouter_ask.py
Single LLM call via OpenRouter. Default proxy model: qwen/qwen3-235b-a22b-2507.

Usage:
    python openrouter_ask.py --model qwen/qwen3-235b-a22b-2507 --system "..." --user "..."
    echo "user message" | python openrouter_ask.py --system "..."

Pass full model ID via --model (aliases below still work):
    llama-3.1-8b   → meta-llama/llama-3.1-8b-instruct
    mistral-7b     → mistralai/mistral-7b-instruct
"""

import sys
import os
import json
import argparse
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "bibliography.bib").exists():
            return candidate
    raise FileNotFoundError("Could not find repository root with bibliography.bib")

load_dotenv(find_repo_root(Path(__file__).parent.parent) / ".env")

API_KEY = os.environ["OPENROUTER_API_KEY"]

MODEL_ALIASES = {
    "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct",
    "mistral-7b": "mistralai/mistral-7b-instruct",
    "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",
    "gemma-9b": "google/gemma-3-9b-it",
}


def ask(model: str, system: str, user: str, max_tokens: int = 1000) -> str:
    if not API_KEY:
        return "ERROR: OPENROUTER_API_KEY not set"

    full_model = MODEL_ALIASES.get(model, model)

    payload = json.dumps({
        "model": full_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "diploma-review",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen/qwen3-235b-a22b-2507")
    parser.add_argument("--system", default="You are a helpful assistant.")
    parser.add_argument("--user", default="")
    parser.add_argument("--max-tokens", type=int, default=1000)
    args = parser.parse_args()

    user_msg = args.user or (sys.stdin.read() if not sys.stdin.isatty() else "")
    if not user_msg:
        print("Usage: python openrouter_ask.py --user 'message' OR pipe via stdin")
        sys.exit(1)

    print(ask(args.model, args.system, user_msg, args.max_tokens))

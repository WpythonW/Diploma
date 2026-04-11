"""
Tool: perplexity_search.py
Single API call to Perplexity sonar (live web search).

Usage:
    python perplexity_search.py "your query here"

Output: plain text response
"""

import sys
import os
import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.environ["PERPLEXITY_API_KEY"]
MODEL = "sonar"  # cheapest with live web search


def search(query: str, max_tokens: int = 800) -> str:
    if not API_KEY:
        return "ERROR: PERPLEXITY_API_KEY not set"

    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": query}],
        "max_tokens": max_tokens,
    }).encode()

    req = urllib.request.Request(
        "https://api.perplexity.ai/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    if not query:
        print("Usage: python perplexity_search.py 'query'")
        sys.exit(1)
    print(search(query))

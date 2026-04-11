"""
Tool: log_io.py
Logs orchestrator (Claude) I/O for token usage transparency.

Usage:
    from log_io import log_in, log_out, print_token_summary
    log_out("openrouter_ask prompt", prompt_text)   # before sending
    log_in("openrouter_ask result", result_text)    # after receiving
    print_token_summary()                           # show session summary
"""

import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "orchestrator_io.log"


def _entry(direction: str, label: str, text: str) -> dict:
    return {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "dir": direction,  # IN or OUT
        "label": label,
        "chars": len(text),
        "text": text,
    }


def log_in(label: str, text: str):
    """Log text received by the orchestrator (from a tool/script)."""
    _append(_entry("IN", label, text))


def log_out(label: str, text: str):
    """Log text sent by the orchestrator (prompt to model/tool)."""
    _append(_entry("OUT", label, text))


def _append(entry: dict):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def print_token_summary():
    """Print I/O summary: chars and approximate tokens (chars / 4)."""
    if not LOG_FILE.exists():
        print("[log_io] No log file yet.")
        return

    entries = [
        json.loads(line)
        for line in LOG_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    total_in = sum(e["chars"] for e in entries if e["dir"] == "IN")
    total_out = sum(e["chars"] for e in entries if e["dir"] == "OUT")

    print(f"\n{'='*52}")
    print("ORCHESTRATOR TOKEN USAGE SUMMARY")
    print(f"{'='*52}")
    print(f"Events logged : {len(entries)}")
    print(f"Total IN      : {total_in:>8,} chars  (~{total_in // 4:,} tokens)")
    print(f"Total OUT     : {total_out:>8,} chars  (~{total_out // 4:,} tokens)")
    print(f"{'='*52}")
    for e in entries:
        print(f"  [{e['ts']}] {e['dir']:3s}  {e['chars']:6,} chars  — {e['label']}")
    print(f"\nLog: {LOG_FILE}")

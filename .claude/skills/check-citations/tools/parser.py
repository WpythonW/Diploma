"""
parser.py — .bib file parsing and entry formatting.
Extracted from check_papers.py for modularity.
"""

import re
from pathlib import Path


def parse_bib(filepath: str) -> list[dict]:
    """Parse a .bib file into a list of entry dicts."""
    content = Path(filepath).read_text(encoding="utf-8")
    entries = []
    for m in re.finditer(r'@(\w+)\{(\w+),\s*(.*?)\n\}', content, re.DOTALL):
        body = m.group(3)
        fields = {}
        for fm in re.finditer(r'(\w+)\s*=\s*\{(.*?)\}(?=\s*[,\n])', body, re.DOTALL):
            k = fm.group(1).lower()
            v = re.sub(r'\{([^{}]*)\}', r'\1', fm.group(2).strip().replace('\n', ' '))
            fields[k] = v
        entries.append({"key": m.group(2), "type": m.group(1).lower(), "fields": fields})
    return entries


def entry_to_description(entry: dict) -> str:
    """Format a parsed bib entry as a human-readable description for the agent."""
    f = entry["fields"]
    parts = []
    for label, field in [
        ("Authors", "author"), ("Title", "title"), ("Journal", "journal"),
        ("Conference/Book", "booktitle"), ("Year", "year"), ("Volume", "volume"),
        ("Pages", "pages"), ("Publisher", "publisher"), ("URL", "howpublished"),
    ]:
        if field in f:
            parts.append(f"{label}: {f[field]}")
    return "\n".join(parts)

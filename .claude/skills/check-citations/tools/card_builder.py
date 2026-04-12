"""
card_builder.py — paper card generation from verification results.
Extracted from check_papers.py for modularity.
"""

import re
from pathlib import Path


def build_card(entry: dict, result: dict, card_body: str) -> str:
    """Assemble a paper card markdown file."""
    f = entry["fields"]
    s2 = result.get("_s2") or {}

    def extract(label: str) -> str:
        m = re.search(rf'^{label}:\s*(.+?)(?=\n[A-Z_]+:|$)', card_body, re.MULTILINE | re.DOTALL)
        return m.group(1).strip() if m else "Unknown"

    goal = extract("GOAL")
    gap = extract("GAP")
    method = extract("METHOD")
    datasets = extract("DATASETS")
    metrics = extract("METRICS")
    results_txt = extract("RESULTS")
    limitations = extract("LIMITATIONS")
    source_used = extract("SOURCE_USED")

    verified_flag = "true" if result["verdict"] == "REAL" else "false"

    doi = s2.get("doi") or f.get("doi", "")
    arxiv_id = s2.get("arxiv_id") or f.get("arxiv_id", f.get("eprint", ""))
    pdf_url = s2.get("pdf_url") or f.get("url", f.get("howpublished", ""))
    s2_id = s2.get("paper_id", "")
    s2_url = s2.get("paper_url", "")
    citations = s2.get("citation_count", "")

    lines = [
        "---",
        f"key: {entry['key']}",
        f"title: {f.get('title', 'Unknown')}",
        f"authors: {f.get('author', 'Unknown')}",
        f"year: {f.get('year', 'Unknown')}",
        f"venue: {f.get('journal') or f.get('booktitle') or f.get('publisher', 'Unknown')}",
        f"doi: {doi}",
        f"arxiv_id: {arxiv_id}",
        f"pdf_url: {pdf_url}",
        f"semantic_scholar_id: {s2_id}",
        f"paper_url: {s2_url}",
        f"citation_count: {citations}",
        f"verified: {verified_flag}",
        f"confidence: {result['confidence']}",
        f"source_used: {source_used}",
        "---",
        "",
        "## Goal",
        goal,
        "",
        "## Gap Addressed",
        gap,
        "",
        "## Method",
        method,
        "",
        "## Datasets and Metrics",
        f"**Datasets:** {datasets}",
        "",
        f"**Metrics:** {metrics}",
        "",
        "## Results",
        results_txt,
        "",
        "## Limitations",
        limitations,
        "",
        "## Verification Verdict",
        f"{result['verdict']} ({result['confidence']}%) — {result['reason']}",
    ]

    links = []
    if s2_url:
        links.append(f"- [Semantic Scholar]({s2_url})")
    if doi:
        links.append(f"- [DOI](https://doi.org/{doi})")
    if arxiv_id:
        links.append(f"- [arXiv](https://arxiv.org/abs/{arxiv_id})")
    if pdf_url and pdf_url not in (s2_url,):
        links.append(f"- [PDF]({pdf_url})")
    if links:
        lines += ["", "## Links"] + links

    return "\n".join(lines) + "\n"

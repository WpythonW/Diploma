from __future__ import annotations

from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = EXPERIMENT_ROOT / "input"
OUTPUT_DIR = EXPERIMENT_ROOT / "output"

SHEET_ID = "1Dn2bfCIM9MVJKRRn34JZdSVIqHBmgqnf9K2e8rTH5x0"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

EXPERIMENT_CONFIG = {
    "max_completion_tokens": 1000,
    "random_seed": 42,
    "n_prompt_permutations": 5,
    "max_concurrent_requests": 60,
}

# Active datasets — 5 content conditions used in diploma
# Note: formal_logic.csv maps to "FL Canon" in diploma tables
EXPERIMENT_SHEETS = {
    "formal_logic": {
        "gid": 33100807,
        "results_sheet": "formal_logic_results",
        "stats_sheet": "formal_logic_stats",
        "metrics_sheet": "formal_logic_metrics",
        "color": "#E8F5E9",
    },
    "formal_logic_neutral": {
        "gid": 1417997279,
        "results_sheet": "formal_logic_neutral_results",
        "stats_sheet": "formal_logic_neutral_stats",
        "metrics_sheet": "formal_logic_neutral_metrics",
        "color": "#E3F2FD",
    },
    "concrete_facts_extended": {
        "gid": 1346509739,
        "results_sheet": "concrete_facts_extended_results",
        "stats_sheet": "concrete_facts_extended_stats",
        "metrics_sheet": "concrete_facts_extended_metrics",
        "color": "#D7CCC8",
    },
    "familiar_social_contracts_extended": {
        "gid": 104661191,
        "results_sheet": "familiar_social_contracts_extended_results",
        "stats_sheet": "familiar_social_contracts_extended_stats",
        "metrics_sheet": "familiar_social_contracts_extended_metrics",
        "color": "#FFE0B2",
    },
    "unfamiliar_fantasy_social_contracts_extended": {
        "gid": 1083598411,
        "results_sheet": "unfamiliar_fantasy_social_contracts_extended_results",
        "stats_sheet": "unfamiliar_fantasy_social_contracts_extended_stats",
        "metrics_sheet": "unfamiliar_fantasy_social_contracts_extended_metrics",
        "color": "#F8BBD0",
    },
}

CATEGORIES = {
    frozenset({"P", "not_Q"}): "CORRECT",
    frozenset({"P", "Q"}): "MATCHING_BIAS",
    frozenset({"P"}): "CONFIRMATION_BIAS",
    frozenset({"not_Q"}): "SINGLE_VIOLATION",
    frozenset({"P", "Q", "not_Q"}): "OVER_SELECTION",
    frozenset({"P", "not_P", "Q", "not_Q"}): "ALL_CARDS",
}

DEFAULT_MODELS = [
    "anthropic/claude-sonnet-4.6",
    "x-ai/grok-4.1-fast",
    "openai/gpt-5.2",
]

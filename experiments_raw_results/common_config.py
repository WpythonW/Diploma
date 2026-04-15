from __future__ import annotations

import os

from dotenv import load_dotenv

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_ENV_VAR = "OPENROUTER_API_KEY"
OPENROUTER_DEFAULT_MODELS: list[str] = []

# Experimental keys — separate accounts for proprietary vs open models
EXPERIMENTAL_PROPRIETARY_ENV_VAR = "EXPERIMENTAL_PROPRIETARY_OPENROUTER_API_KEY"
EXPERIMENTAL_OPEN_ENV_VAR = "EXPERIMENTAL_OPEN_OPENROUTER_API_KEY"

load_dotenv()
OPENROUTER_API_KEY = os.getenv(OPENROUTER_API_ENV_VAR)


def get_openrouter_api_key() -> str | None:
    """Fallback legacy key. Prefer get_experimental_key() for experiments."""
    return OPENROUTER_API_KEY or os.getenv(OPENROUTER_API_ENV_VAR)


def get_experimental_key(model_group: str) -> str | None:
    """Return the correct experimental API key for the given model group.

    Parameters
    ----------
    model_group : str
        Either ``"proprietary"`` or ``"open"`` (case-insensitive).

    Returns
    -------
    str | None
        The API key, or ``None`` if the env var is not set.

    Raises
    ------
    ValueError
        If *model_group* is not one of the accepted values.
    """
    group = model_group.lower()
    if group == "proprietary":
        return os.getenv(EXPERIMENTAL_PROPRIETARY_ENV_VAR)
    if group == "open":
        return os.getenv(EXPERIMENTAL_OPEN_ENV_VAR)
    raise ValueError(
        f"Unknown model group: {model_group!r}. "
        f"Must be 'proprietary' or 'open'."
    )


def get_openrouter_default_models() -> list[str]:
    return list(OPENROUTER_DEFAULT_MODELS)


PROPRIETARY_MODELS = [
    "anthropic/claude-sonnet-4.6",
    "x-ai/grok-4.1-fast",
    "openai/gpt-5.2",
]

OPEN_MODELS = [
    "qwen/qwen3.5-397b-a17b",
    "z-ai/glm-4.7-flash",
    "qwen/qwen3-next-80b-a3b-instruct",
    "google/gemma-3-27b-it",
    "deepseek/deepseek-v3.2",
    "google/gemma-3-12b-it",
]

MODELS = list(PROPRIETARY_MODELS)

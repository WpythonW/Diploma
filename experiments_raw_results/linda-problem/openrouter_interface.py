from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI
from pydantic import TypeAdapter

from common_config import OPENROUTER_BASE_URL


def create_openrouter_client(api_key: str) -> AsyncOpenAI:
    return AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def _parse_labeled_fields(content: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_key: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        matched_key = None
        for key in ("vignette", "t", "f", "f_uncorrelated"):
            prefix = f"{key}:"
            if line.lower().startswith(prefix):
                matched_key = key
                fields[key] = line[len(prefix) :].strip()
                current_key = key
                break

        if matched_key is None:
            if current_key is None:
                raise ValueError(f"Unexpected response line before any field: {raw_line!r}")
            fields[current_key] = f"{fields[current_key]} {line}".strip()

    return fields


async def request_structured(
    client: AsyncOpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    response_format: type[Any],
    schema_name: str,
    temperature: float,
    max_completion_tokens: int,
    reasoning_effort: str | None = None,
) -> Any:
    adapter = TypeAdapter(response_format)
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_completion_tokens,
    }
    if reasoning_effort is not None:
        kwargs["extra_body"] = {"reasoning": {"effort": reasoning_effort}}
    response = await client.chat.completions.create(
        **kwargs,
    )
    if not getattr(response, "choices", None):
        error_obj = getattr(response, "error", None)
        raise ValueError(f"OpenRouter response has no choices. Error: {error_obj}")

    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise ValueError("OpenRouter returned empty content")

    parsed_fields = _parse_labeled_fields(content)
    return adapter.validate_python(parsed_fields)

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openai import AsyncOpenAI, OpenAI

from common_config import OPENROUTER_BASE_URL


def create_async_openrouter_client(api_key: str) -> AsyncOpenAI:
    return AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def create_openrouter_client(api_key: str) -> OpenAI:
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def parse_openrouter_completion(
    client: OpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    seed: int,
    temperature: float,
    response_format: Any = None,
    reasoning_effort: str | None = None,
) -> Any:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "seed": seed,
        "temperature": temperature,
    }
    if response_format is not None:
        kwargs["response_format"] = response_format
    if reasoning_effort is not None:
        kwargs["reasoning_effort"] = reasoning_effort
    return client.chat.completions.parse(**kwargs)


async def create_openrouter_completion(
    client: AsyncOpenAI,
    *,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    seed: int | None = None,
    max_completion_tokens: int | None = None,
    response_format: Any = None,
    reasoning_effort: str | None = None,
    provider: dict[str, Any] | None = None,
) -> Any:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if seed is not None:
        kwargs["seed"] = seed
    if max_completion_tokens is not None:
        kwargs["max_completion_tokens"] = max_completion_tokens
    if response_format is not None:
        kwargs["response_format"] = response_format
    extra_body: dict[str, Any] = {}
    if reasoning_effort is not None:
        extra_body["reasoning"] = {"effort": reasoning_effort}
    if provider is not None:
        extra_body["provider"] = provider
    if extra_body:
        kwargs["extra_body"] = extra_body
    return await client.chat.completions.create(**kwargs)


def format_openrouter_assistant_content(message: Any, include_reasoning: bool = False) -> str:
    content = message.content or ""
    if not include_reasoning:
        return content

    model_extra = getattr(message, "model_extra", None)
    if not isinstance(model_extra, Mapping):
        return content
    reasoning = model_extra.get("reasoning")
    if reasoning is None:
        return content
    return f"Reasoning: {reasoning}\n{content}"


def update_usage_stats(stats_collector: dict[str, int], usage: Any) -> None:
    if usage is None:
        return
    stats_collector["prompt_tokens"] += int(getattr(usage, "prompt_tokens", 0) or 0)
    stats_collector["completion_tokens"] += int(getattr(usage, "completion_tokens", 0) or 0)
    details = getattr(usage, "completion_tokens_details", None)
    stats_collector["reasoning_tokens"] += int(getattr(details, "reasoning_tokens", 0) or 0)

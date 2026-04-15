# Experiment Rules

## API Key Policy — STRICT

All LLM experiments in this project use **two separate OpenRouter API keys**:

| Environment Variable | Purpose | Models |
|---|---|---|
| `EXPERIMENTAL_PROPRIETARY_OPENROUTER_API_KEY` | **Proprietary models only** | `anthropic/*`, `openai/*`, `x-ai/*` |
| `EXPERIMENTAL_OPEN_OPENROUTER_API_KEY` | **Open/open-weight models only** | `qwen/*`, `google/*`, `deepseek/*`, `z-ai/*` |

### CRITICAL RULES

1. **NEVER mix the keys.** The proprietary key must ONLY be used for proprietary models. The open key must ONLY be used for open models.
2. **NEVER use the open key for proprietary models** (and vice versa). This corrupts billing attribution and experimental accounting.
3. **The keys are stored in the project root `.env` file.** This file is `.gitignore`-ed — **never commit it**.
4. **Never hardcode API keys in source code.** Always read from environment variables.

### CLI Usage

When running experiments, the agent **must** specify which model group is being used so the correct key is selected:

```bash
# Proprietary models — uses EXPERIMENTAL_PROPRIETARY_OPENROUTER_API_KEY
python3 run_experiments.py \
  --models anthropic/claude-sonnet-4.6 x-ai/grok-4.1-fast openai/gpt-5.2 \
  --model-group proprietary \
  --contexts formal_logic \
  --output-dir output/my_run

# Open models — uses EXPERIMENTAL_OPEN_OPENROUTER_API_KEY
python3 run_experiments.py \
  --models qwen/qwen3.5-397b-a17b google/gemma-3-27b-it \
  --model-group open \
  --contexts formal_logic \
  --output-dir output/my_run
```

Alternatively, pass the keys explicitly:

```bash
python3 run_experiments.py \
  --models anthropic/claude-sonnet-4.6 \
  --api-key-proprietary "$EXPERIMENTAL_PROPRIETARY_OPENROUTER_API_KEY" \
  ...

python3 run_experiments.py \
  --models qwen/qwen3.5-397b-a17b \
  --api-key-open "$EXPERIMENTAL_OPEN_OPENROUTER_API_KEY" \
  ...
```

### How Key Resolution Works

The experiment runner (`run_experiments.py`) resolves the API key in this order:

1. **Explicit CLI flag** (`--api-key-proprietary` / `--api-key-open`)
2. **Environment variable** (`EXPERIMENTAL_PROPRIETARY_OPENROUTER_API_KEY` / `EXPERIMENTAL_OPEN_OPENROUTER_API_KEY`)
3. **Legacy fallback** (`--api-key` / `OPENROUTER_API_KEY`) — discouraged

If `--model-group` is provided, the matching key is used. If omitted, the runner auto-detects the group based on model names listed in `common_config.py`.

### What NOT to Do

- ❌ Do not run open models with `EXPERIMENTAL_PROPRIETARY_OPENROUTER_API_KEY`
- ❌ Do not run proprietary models with `EXPERIMENTAL_OPEN_OPENROUTER_API_KEY`
- ❌ Do not put API keys in code, scripts, or config files
- ❌ Do not commit `.env` or any file containing API keys
- ❌ Do not use a single shared key for both model groups

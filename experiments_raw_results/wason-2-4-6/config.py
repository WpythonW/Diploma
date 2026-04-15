from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from common_config import OPEN_MODELS, PROPRIETARY_MODELS

EXPERIMENT_ROOT = Path(__file__).resolve().parent
DATA_DIR = EXPERIMENT_ROOT / "data"
OUTPUT_DIR = EXPERIMENT_ROOT / "output"

SHEET_ID = "1ITCdK9HYDTe04wTQAmvuZtXdqv4CKmoZEBNIN62DZk8"
RULES_SHEET_GID = 452385502
RULES_COLUMN = "Python Lambda Function"
CATEGORY_COLUMN = "Category"
MIN_TEST_VALUE = 1
MAX_TEST_VALUE = 1000

DEFAULT_MODELS = [
    PROPRIETARY_MODELS[0],  # anthropic/claude-sonnet-4.6
    PROPRIETARY_MODELS[1],  # x-ai/grok-4.1-fast
    PROPRIETARY_MODELS[2],  # openai/gpt-5.2
    # OPEN_MODELS[0],  # qwen/qwen3.5-397b-a17b
    # OPEN_MODELS[1],  # z-ai/glm-4.7-flash
    # OPEN_MODELS[2],  # qwen/qwen3-next-80b-a3b-instruct
    # OPEN_MODELS[3],  # google/gemma-3-27b-it
    # OPEN_MODELS[4],  # deepseek/deepseek-v3.2
    # OPEN_MODELS[5],  # google/gemma-3-12b-it
]

DEFAULT_MAX_TURNS = 19

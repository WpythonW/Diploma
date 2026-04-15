from __future__ import annotations

from pathlib import Path

from common_config import MODELS

EXPERIMENT_ROOT = Path(__file__).resolve().parent

# Paths
DATA_DIR = EXPERIMENT_ROOT / "data"
JOBS_CSV = DATA_DIR / "jobs.csv"
OUTPUT_CSV = DATA_DIR / "linda_dataset.csv"
INPUT_CSV = DATA_DIR / "conjunction_dataset_all.csv"
OUTPUT_DIR = EXPERIMENT_ROOT / "output"

# Generation settings
M = 4
PARALLEL_GENERATIONS = 10
MAX_ROW_ATTEMPTS = 8
SEQUENTIAL_BATCH_SIZE = 3

# Model settings
TEMPERATURE = 1.0
MAX_COMPLETION_TOKENS = 350
REASONING_EFFORT = "none"

# Linda experiment settings
LINDA_MODELS = list(MODELS)
LINDA_TEMPERATURE = 0.0
LINDA_MAX_COMPLETION_TOKENS = 160
LINDA_REASONING_EFFORT = "none"
LINDA_CONCURRENCY = 20
LINDA_RETRIES = 4
LINDA_TIMEOUT_SECONDS = 60
LINDA_SEED = 42

# Reduced evaluation grid: one representative name per race and one fixed age.
DEMOGRAPHICS: dict[str, tuple[str, ...]] = {
    "White": ("Emma",),
    "Black": ("Jamal",),
    "Hispanic": ("Carlos",),
    "Asian": ("Wei",),
}
AGES: tuple[int, ...] = (38,)

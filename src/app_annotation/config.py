"""
Centralized, portable path configuration.
"""
import os
from pathlib import Path


def _find_project_root(marker: str = "pyproject.toml") -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / marker).exists():
            return parent
    return current.parents[2]


PROJECT_ROOT = _find_project_root()

try:
    from dotenv import load_dotenv
    _dotenv_path = PROJECT_ROOT / ".env"
    print(f"[config] Looking for .env at: {_dotenv_path}")
    print(f"[config] Exists: {_dotenv_path.exists()}")
    if _dotenv_path.exists():
        load_dotenv(_dotenv_path, override=True)
        print(f"[config] Loaded")
    else:
        print(f"[config] No .env found at {_dotenv_path}")
except ImportError:
    pass
 
def _path_from_env(env_var: str, default: Path) -> Path:
    """
    Use an environment variable override if set (expanding ~ and
    resolving to an absolute path), otherwise fall back to the given
    default under PROJECT_ROOT.
    """
    value = os.environ.get(env_var)
    return Path(value).expanduser().resolve() if value else default


DATA_DIR = _path_from_env("DATA_DIR", PROJECT_ROOT / "data")
INPUT_DIR = _path_from_env("INPUT_DIR", DATA_DIR / "input")
OUTPUT_DIR = _path_from_env("OUTPUT_DIR", DATA_DIR / "output")
ANNOTATED_DIR = _path_from_env("ANNOTATED_DIR", DATA_DIR / "annotated")

EVALS_DIR = _path_from_env("EVALS_DIR", PROJECT_ROOT / "evals")
GOLD_SET_PATH = _path_from_env("GOLD_SET_PATH", EVALS_DIR / "gold_set.jsonl")
EVAL_RESULTS_DIR = _path_from_env("EVAL_RESULTS_DIR", EVALS_DIR / "results")

# CACHE_DB_PATH = _path_from_env("CACHE_DB_PATH", DATA_DIR / "cache.sqlite3")

PROMPTS_DIR = _path_from_env(
    "PROMPTS_DIR", PROJECT_ROOT / "src" / "app_annotation" / "prompts"
)

for _d in (DATA_DIR, INPUT_DIR, OUTPUT_DIR, EVALS_DIR, EVAL_RESULTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)


 
# --- Model temperature ------------------------------------------------------
# Single value used for normal runs (classify, spoof_check, etc.)
CLASSIFY_TEMPERATURE = float(os.environ.get("CLASSIFY_TEMPERATURE", "0.0"))
 
 
def _parse_temperature_list(env_var: str, default: list[float]) -> list[float]:
    """
    Parses a comma-separated list of temperatures from an env var, e.g.
    EXPERIMENT_TEMPERATURES=0.0,0.3,0.7,1.0
    Falls back to `default` if unset or unparseable.
    """
    raw = os.environ.get(env_var)
    if not raw:
        return default
    try:
        return [float(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError as e:
        raise ValueError(
            f"Could not parse {env_var}={raw!r} as a comma-separated list of "
            f"floats (e.g. '0.0,0.3,0.7'): {e}"
        )
 
 
EXPERIMENT_TEMPERATURES = _parse_temperature_list(
    "EXPERIMENT_TEMPERATURES", default=[0.0, 0.3, 0.7]
)
 

if __name__ == "__main__":
    print(f"PROJECT_ROOT     : {PROJECT_ROOT}")
    print(f"DATA_DIR         : {DATA_DIR}")
    print(f"INPUT_DIR        : {INPUT_DIR}")
    print(f"OUTPUT_DIR       : {OUTPUT_DIR}")
    print(f"EVALS_DIR        : {EVALS_DIR}")
    print(f"GOLD_SET_PATH    : {GOLD_SET_PATH}")
    print(f"EVAL_RESULTS_DIR : {EVAL_RESULTS_DIR}")
    # print(f"CACHE_DB_PATH    : {CACHE_DB_PATH}")
    print(f"PROMPTS_DIR      : {PROMPTS_DIR}")
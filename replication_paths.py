"""Location-independent paths for the prompt smells replication package."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_DIR = PROJECT_ROOT / "02_dataset"
RAW_DEVGPT_DIR = DATASET_DIR / "raw" / "DevGPT"
INTERIM_DIR = DATASET_DIR / "interim"
RESULTS_DIR = PROJECT_ROOT / "04_llm_evaluation" / "LLM-Judges-results"
HUMAN_FILE = PROJECT_ROOT / "05_human_evaluation" / "HumanReview_merged.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "07_results"
SAMPLE_CSV = DATASET_DIR / "devgpt_llm_judge_sample_260.csv"
SAMPLE_PARQUET = DATASET_DIR / "devgpt_llm_judge_sample_260.parquet"


def load_sample():
    """Load the existing sample; CSV fallback avoids requiring a Parquet engine."""
    import pandas as pd
    if SAMPLE_PARQUET.is_file():
        try:
            return pd.read_parquet(SAMPLE_PARQUET)
        except ImportError:
            pass
    if SAMPLE_CSV.is_file():
        return pd.read_csv(SAMPLE_CSV, dtype={"prompt_id": str}, keep_default_na=False)
    raise FileNotFoundError(f"Missing sample: {SAMPLE_PARQUET} or {SAMPLE_CSV}")

# Prompt Smells — Replication Package

This repository contains supplementary artifacts for a study of prompt smells in software-engineering prompts, based on a consolidated catalogue and a subset of the DevGPT dataset. The evaluation uses four LLM families (GPT, Claude, Gemini, DeepSeek) and three prompting techniques (zero-shot, few-shot, and Best-of-3 majority vote), with separate human annotations.

## LLM-assisted preparation of the replication package

The original research project was provided to a large language model (LLM) with a request to refactor selected parts of the code and add supporting files to make the project easier to organize, execute, and reuse as a replication package. The LLM assisted with reorganizing file paths, introducing relative-path configuration, reducing duplicated code in the LLM evaluation notebooks through a shared runner (`llm_runner.py`)

The original experimental datasets, saved LLM classification results, human annotations, and judge prompt templates were preserved rather than regenerated during this refactoring. The shared runner is a revised implementation and should **not** be assumed to be behaviorally identical to the code originally used to call the model APIs. The archived results support reproducing the analyses without rerunning paid evaluations; researchers who wish to repeat the API-based experiments should first review the refactored execution code and settings.

## Folder map

| Folder | Contents |
|---|---|
| `01_taxonomy/` | The 21 static smell definitions, examples and sources (`smell_catalogue.py`). |
| `02_dataset/` | Released 260-prompt sample in CSV and Parquet; extraction and sampling notebooks under `data_preparation/`. |
| `03_judge_prompts/` | **Original** zero-shot, few-shot and Best-of-3 prompt templates and vote aggregation logic. |
| `04_llm_evaluation/` | Four cleaned judge notebooks, optional resumable API runner, and **original saved** evaluation records under `LLM-Judges-results/`. |
| `05_human_evaluation/` | Reviewer workbook and agreement notebook. |
| `06_eda/` | Prevalence, co-occurrence, and human-versus-LLM analysis notebooks. |
| `07_results/` | Derived tables exported by analysis notebooks. |
| `replication_paths.py` | Shared paths, based on the location of this repository instead of absolute Windows drives. |
| `requirements.txt` | Python environment dependencies. |

## Quick start (without API calls)

1. Extract this entire package, keeping the folder structure unchanged.
2. Use Python 3.11–3.13 and create an isolated Python environment.
3. From the package root, install dependencies: `python -m pip install -r requirements.txt`.
4. Start Jupyter **from the package root or any package subfolder**: `jupyter lab`.
5. Open notebooks in `05_human_evaluation/` or `06_eda/` and run all cells. These read the included results and do not contact model providers.
6. To inspect the saved LLM classifications, open any notebook under `04_llm_evaluation/` and run all cells with `RUN_API_CALLS = False` (the default).

Caution: notebooks find the project root by walking up from `Path.cwd()` and locating `replication_paths.py`. A notebook copied to an unrelated directory or run with a working directory **outside** the project cannot resolve the repository.

### Important source-data limitation

The original DevGPT **raw snapshots and intermediate first-turn data are not present**. The `02_dataset/data_preparation/01_extract_and_filter_clean.ipynb` and `02_sample.ipynb` notebooks are provided for provenance, but **cannot be executed end-to-end using this archive alone**. To reproduce those stages from scratch, download the original DevGPT snapshots from the dataset authors and place snapshot directories under `02_dataset/raw/DevGPT/`. Then run extraction followed by sampling. Obtain and respect the upstream dataset terms.

The included `02_dataset/devgpt_llm_judge_sample_260.csv` and `.parquet` support the LLM and statistical analysis stages directly. If Parquet support is missing, the LLM notebooks automatically fall back to the included CSV; the data preparation notebooks require `pyarrow` as specified in `requirements.txt`.

## Execution order

1. **Optional raw-data reconstruction:** `02_dataset/data_preparation/01_extract_and_filter_clean.ipynb`, then `02_sample.ipynb` (requires raw snapshots).
2. **LLM judges, optional:** `04_llm_evaluation/04_Gpt_judge.ipynb`, `04_claude_judge.ipynb`, `04_Gemini_judge.ipynb`, `04_deepSeek_judge.ipynb`.
3. **Human agreement:** `05_human_evaluation/kappa_agreement.ipynb`.
4. **Prevalence:** `06_eda/Rq2.ipynb` (notebook filename retained from the source project).
5. **Co-occurrence:** `06_eda/cooccurrence_smells_simplificado.ipynb`.
6. **Human comparison:** `06_eda/human_llm_comparison.ipynb`.

Notebook exports are written to `07_results/`. Outputs can be regenerated at any time and do not overwrite the archived response files.

## Re-running LLM evaluations (optional, can incur fees)

All four judge notebooks default to `RUN_API_CALLS = False`. To submit new requests, set it to `True` **and** provide a provider API key using the relevant environment variable (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`) or interactive password prompt. Results are appended to existing JSONL files only for prompt IDs/repetitions not already completed; existing entries are not overwritten. Errors are logged separately.

Each notebook uses the model identifier and endpoint found in the provided project; availability and response-format support must be confirmed with the provider before a future rerun. The `llm_runner.py` is a refactored execution wrapper; it retains the *original* `build_zero_shot_prompt`, `build_few_shot_prompt`, `build_best_of_3_prompt` and `aggregate_majority_vote` functions, but is not a claim of byte-for-byte parity in API client behavior.

**Do not enable all four paid runners simply to reproduce the tables**; the archived JSONL classification results already exist.

## Label semantics

- A smell not included in a single-run `smells` object is treated as **absent** in the original analyses.
- `present`, `cannot_determine`, and any archived `no_consensus` labels are kept distinct. The package does not change historical classifications.
- The human evaluation uses the 21 smell columns and only rows marked `Reviewed` in both reviewer sheets for agreement.
- Co-occurrence uses pairwise available 0/1 observations; `cannot_determine` and `no_consensus` are not assumed absent.
- The saved runs include incomplete/model-filtered cases, so compare **actual denominators** rather than assuming 260 classifications in every configuration.

## Reproducibility and ethics

- Preserve the archived `LLM-Judges-results/` and `HumanReview_merged.xlsx` as original source evidence.
- Review *all* DevGPT-derived prompts, annotations, outputs, paths and metadata for privacy, redistribution permissions and potential personal information before publishing. Redact only in a documented derived release, not silently in the archival research records.
- The uploaded source archive contained a Git `.git/` directory. It has **not** been copied into this package, avoiding accidental publication of repository history or previously committed secrets. Before publishing, scan the repository and history if reusing the original Git remote.
- No `.env`, `settings.json`, API key, or local environment folder is required or included.
- A project-wide license was not supplied; see `LICENSE_NOTICE.md` before deciding redistribution terms.
- The results reflect the supplied snapshot of the project. No inference about the correctness of original LLM judgments is implied by the executable checks.

## Validation

Run `python check_package.py` from the root to verify the 260-prompt CSV sample, the catalogue, saved JSONL files and the human workbook. This does **not** call LLM APIs or modify any data. It can be run before publication.

See `REFACTOR_NOTES.md` for a complete summary of path corrections, changed cells, and the two preprocessing steps that need the upstream raw dataset.

"""Optional, resumable LLM evaluations. No network calls occur on import.

The historical JSONL results are never rewritten. Results are appended only when a
new API run has been explicitly enabled. The original prompt builders are reused.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json

from judge_prompts import (
    build_zero_shot_prompt, build_few_shot_prompt,
    build_best_of_3_prompt, aggregate_majority_vote,
)

BUILDERS = {
    "zero_shot": build_zero_shot_prompt,
    "few_shot": build_few_shot_prompt,
    "mv3": build_best_of_3_prompt,
}


def read_jsonl(path):
    """Read JSONL without modifying or normalizing saved historical records."""
    if not Path(path).exists():
        return []
    with Path(path).open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def append_jsonl(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def experiment_status(results_dir, model_name):
    """Summary of existing saved output, without any API calls."""
    report = []
    for technique in BUILDERS:
        directory = Path(results_dir) / f"{model_name}_{technique}"
        success_file = directory / ("classifications.jsonl" if technique == "mv3" else "responses.jsonl")
        saved = read_jsonl(success_file)
        ids = {
            (row.get("result") or {}).get("prompt_id", row.get("prompt_id"))
            for row in saved
        }
        report.append({"technique": technique, "saved_classifications": len(ids),
                       "logged_errors": len(read_jsonl(directory / "errors.jsonl"))})
    return report


def run_evaluations(sample, *, client, api_model, model_name, results_dir,
                    technique, max_tokens=None, json_mode=False):
    """Resumes only missing IDs/repetitions, and preserves the original JSONL schema.

    Note: a previous completed classification takes precedence, so existing records
    cannot be overwritten. Error records don't mark an evaluation as completed.
    """
    if technique not in BUILDERS:
        raise ValueError(f"Unknown technique: {technique}")
    if client is None:
        raise ValueError("Explicitly configure an API client before evaluating.")

    directory = Path(results_dir) / f"{model_name}_{technique}"
    response_path = directory / "responses.jsonl"
    classification_path = directory / "classifications.jsonl"
    error_path = directory / "errors.jsonl"
    builder = BUILDERS[technique]
    history = read_jsonl(response_path)
    classified = {
        (row.get("result") or {}).get("prompt_id")
        for row in read_jsonl(classification_path)
    } if technique == "mv3" else set()
    single_completed = {
        (row.get("result") or {}).get("prompt_id", row.get("prompt_id"))
        for row in history
    } if technique != "mv3" else set()
    saved_repetitions = defaultdict(dict)
    if technique == "mv3":
        for row in history:
            if "repetition" in row and isinstance(row.get("result"), dict):
                key = row.get("prompt_id") or row["result"].get("prompt_id")
                # Keep the first observed run for each repetition; do not modify archives.
                saved_repetitions[key].setdefault(int(row["repetition"]), row["result"])

    successes = 0
    for row in sample.itertuples(index=False):
        prompt_id = str(row.prompt_id)
        if prompt_id in classified or prompt_id in single_completed:
            continue
        prompt_text = builder(prompt_id=prompt_id, target_prompt=str(row.prompt))
        repeats = (1, 2, 3) if technique == "mv3" else (None,)
        successful = saved_repetitions[prompt_id] if technique == "mv3" else {}
        for repetition in repeats:
            if repetition is not None and repetition in successful:
                continue
            parameters = {
                "model": api_model,
                "messages": [{"role": "user", "content": prompt_text}],
            }
            if max_tokens is not None:
                parameters["max_tokens"] = max_tokens
            if json_mode:
                parameters["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**parameters)
            choice = response.choices[0]
            entry = {
                "model": api_model,
                "technique": "majority_vote_3" if technique == "mv3" else technique,
                "prompt_id": prompt_id,
            }
            if repetition is not None:
                entry["repetition"] = repetition
            content = (choice.message.content or "").strip()
            if content.startswith("```") and content.endswith("```"):
                content = "\n".join(content.splitlines()[1:-1]).strip()
            try:
                if choice.finish_reason != "stop":
                    raise ValueError(f"finish_reason={choice.finish_reason}")
                result = json.loads(content)
                if not isinstance(result, dict) or result.get("prompt_id") != prompt_id:
                    raise ValueError("Wrong or missing prompt ID")
                if not isinstance(result.get("smells"), dict):
                    raise ValueError("Missing smell classifications")
            except (ValueError, TypeError) as exc:
                append_jsonl(error_path, {**entry, "status": "invalid_response",
                                          "error": str(exc), "response": response.model_dump()})
                print(f"{prompt_id} {repetition or ''}: {exc} (logged)")
                continue
            append_jsonl(response_path, {**entry, "result": result, "response": response.model_dump()})
            if repetition is not None:
                successful[repetition] = result
            else:
                single_completed.add(prompt_id)
                successes += 1
        if technique == "mv3" and len(successful) == 3:
            try:
                vote = aggregate_majority_vote([successful[r] for r in (1, 2, 3)])
            except (KeyError, TypeError, ValueError) as exc:
                append_jsonl(error_path, {"model": api_model, "technique": "majority_vote_3",
                                          "prompt_id": prompt_id, "status": "aggregation_error", "error": str(exc)})
                print(f"{prompt_id}: cannot aggregate ({exc})")
                continue
            append_jsonl(classification_path, {"model": api_model, "result": vote})
            classified.add(prompt_id)
            successes += 1
    print(f"{model_name} {technique}: {successes} new classifications saved")
    return successes

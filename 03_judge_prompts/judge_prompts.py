from smell_catalogue import SMELLS


def format_smell_catalogue():
    sections = []

    for key, smell in SMELLS.items():
        sections.append(
            f"Name: {smell['name']}\n"
            f"Key: {key}\n"
            f"Definition: {smell['definition']}"
        )

    return "\n\n".join(sections)

def build_zero_shot_prompt(prompt_id, target_prompt):
    smells = format_smell_catalogue()

    return f"""
You are evaluating a software-engineering prompt for prompt smells.

A prompt smell is a recurring quality issue in a prompt that may affect
clarity, correctness, usefulness, safety, or the behavior of an LLM.

Use only the definitions provided in the catalogue below.

Do not introduce additional prompt smells.
Do not modify the definitions.

PROMPT SMELL CATALOGUE

{smells}

PROMPT TO EVALUATE

Prompt ID: {prompt_id}

<target_prompt>
{target_prompt}
</target_prompt>

TASK

Evaluate every smell listed in the current prompt smell catalogue independently.

- Include a smell if its label is "present".
- Include a smell if its label is "cannot_determine".
- Do not include smells that are absent.

For every included smell, return:

- confidence: a number from 0 to 1
- justification: a brief explanation based on the target prompt

Only classify smells listed in the current prompt smell catalogue.
Do not introduce additional smells.
Do not assume missing information.

Return only valid JSON using this structure:

{{
  "prompt_id": "{prompt_id}",
    "smells": {{
    "<smell_key>": {{
      "label": "present | cannot_determine",
      "confidence": 0.0,
      "justification": "brief explanation"
    }}
  }}
}}
""".strip()

FEW_SHOT_EXAMPLES = """
EXAMPLE 1

Prompt:
"The system must have a user-friendly interface."

Relevant classification:
{
  "smells": {
    "ambiguous_instruction": {
      "label": "present",
      "confidence": 0.95,
      "justification": "The phrase 'user-friendly' is subjective and does not define measurable criteria."
    },
    "intent_misalignment": {
      "label": "cannot_determine",
      "confidence": 0.85,
      "justification": "The user's underlying objective cannot be established from this prompt alone."
    }
  }
}

EXAMPLE 2

Prompt:
"Fix the bug now. Example output: OK. Do not modify the database. Context: the failure happens after rollback. Also preserve the public API."

Relevant classification:
{
  "smells": {
    "poor_prompt_organization": {
      "label": "present",
      "confidence": 0.94,
      "justification": "The task, context, constraints, and example are mixed together without clear organization."
    }
  }
}

EXAMPLE 3

Prompt:
"Review this service, compare three architectural patterns, estimate their performance implications, refactor the implementation, justify every modification, and explain future scalability."

Relevant classification:
{
  "smells": {
    "complexity_smell": {
      "label": "present",
      "confidence": 0.96,
      "justification": "The prompt combines several cognitively demanding and interdependent tasks in a single request."
    }
  }
}
""".strip()

def build_few_shot_prompt(prompt_id, target_prompt):
    smells = format_smell_catalogue()

    return f"""
You are evaluating a software-engineering prompt for prompt smells.

A prompt smell is a recurring quality issue in a prompt that may affect
clarity, correctness, usefulness, safety, or the behavior of an LLM.

Use only the definitions provided in the catalogue below.

Do not introduce additional prompt smells.
Do not modify the definitions.

PROMPT SMELL CATALOGUE

{smells}

CLASSIFICATION EXAMPLES

{FEW_SHOT_EXAMPLES}

PROMPT TO EVALUATE

Prompt ID: {prompt_id}

<target_prompt>
{target_prompt}
</target_prompt>

TASK

Evaluate every smell listed in the current prompt smell catalogue independently.

- Include a smell if its label is "present".
- Include a smell if its label is "cannot_determine".
- Do not include smells that are absent.

For every included smell, return:

- confidence: a number from 0 to 1
- justification: a brief explanation based on the target prompt

The examples demonstrate the classification process and output format.
Only classify smells listed in the current prompt smell catalogue.
Do not introduce additional smells.
Do not assume missing information.

Return only valid JSON using this structure:

{{
  "prompt_id": "{prompt_id}",
    "smells": {{
    "<smell_key>": {{
      "label": "present | cannot_determine",
      "confidence": 0.0,
      "justification": "brief explanation"
    }}
  }}
}}
""".strip()

def build_best_of_3_prompt(prompt_id, target_prompt):
    return build_zero_shot_prompt(
        prompt_id=prompt_id,
        target_prompt=target_prompt,
        )

def aggregate_majority_vote(evaluations):
    from collections import Counter

    if len(evaluations) != 3:
        raise ValueError("Exactly three evaluations are required.")

    prompt_ids = [evaluation["prompt_id"] for evaluation in evaluations]

    if len(set(prompt_ids)) != 1:
        raise ValueError("All evaluations must refer to the same prompt.")

    allowed_labels = {"present", "cannot_determine"}

    for evaluation in evaluations:
        smells = evaluation["smells"]

        if not isinstance(smells, dict):
            raise ValueError("'smells' must be a dictionary.")

        unknown_smells = set(smells) - set(SMELLS)
        if unknown_smells:
            raise ValueError(f"Unknown smells: {sorted(unknown_smells)}")

        for smell_id, answer in smells.items():
            if answer["label"] not in allowed_labels:
                raise ValueError(f"Invalid label for {smell_id}.")

    aggregated = {}

    for smell_id in SMELLS:
        labels = [
            evaluation["smells"].get(
                smell_id, {"label": "absent"}
            )["label"]
            for evaluation in evaluations
        ]

        counts = Counter(labels)
        winning_label, winning_votes = counts.most_common(1)[0]

        final_label = (
            winning_label if winning_votes >= 2 else "no_consensus"
        )

        if final_label == "absent":
            continue

        aggregated[smell_id] = {
            "label": final_label,
            "votes": {
                label: counts[label]
                for label in ("present", "absent", "cannot_determine")
                if counts[label] > 0
            },
        }  

    return {
        "prompt_id": prompt_ids[0],
        "method": "majority_vote_3",
        "smells": aggregated,
    }
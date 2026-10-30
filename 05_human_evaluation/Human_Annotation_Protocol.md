# Human Annotation Protocol for Prompt Smell Identification

## 1. Objective

This protocol provides standardized guidelines for the manual identification and classification of prompt smells in a prompt dataset.

A *prompt smell* is a potentially problematic characteristic of a prompt that may compromise its clarity, completeness, consistency, or effectiveness in communicating instructions to a Large Language Model (LLM).

The annotation procedure is grounded in the prompt smell taxonomy proposed by Della Porta et al. and the prompt defect taxonomy proposed by Tian et al., adapted into the 22-smell catalog adopted in this study.

The primary objective is to ensure that human annotators apply consistent classification criteria, enabling reproducibility, reliable comparisons, and the construction of a human-annotated reference dataset.

## 2. Annotation Fields

Each prompt contains the following annotation fields.

### 2.1. Review Status

**Column:** `review_status`

Indicates the current status of the human evaluation of a prompt.

| **Value** | **Definition** |
| --- | --- |
| pending | The prompt has not yet been fully evaluated. |
| reviewed | The annotator has completed the evaluation and recorded the applicable classifications. |
| needs discussion | The prompt has been evaluated, but one or more classifications require further discussion or clarification before the review can be finalized. |

**Decision rules:**

- `Pending`: by default to all prompts before the annotation process begins. It remains unchanged until the annotator completes the review or identifies an issue requiring discussion.
- Select `reviewed` when all annotation fields have been completed and no unresolved issues remain.
- Select `needs discussion` when the annotator encounters ambiguous cases, overlapping smell definitions, or classification decisions that require discussion with other annotators.
- After resolving the identified issues, update the status from `needs discussion` to `reviewed`.

**Important distinction:** `review_status` indicates the progress of the annotation process, whereas `smell` indicates whether a prompt smell was identified. Therefore, a prompt marked as `needs discussion` may still have confirmed smells recorded in `classify_smell` and uncertain smells recorded in `smells_unsure`.

### 2.2. Smell

**Column:** `smell`

Indicates whether the annotator identified at least one prompt smell.

| **Value** | **Definition** |
| --- | --- |
| true | At least one smell was confidently identified in the prompt. |
| false | No smell was identified after evaluating the prompt against the catalog. |
| unsure | No smell was confidently identified, but at least one potential smell remains uncertain. |

**Decision rules:**

- Select `true` when there is clear evidence of at least one smell.
- Select `false` when none of the 22 smells satisfies its identification criteria and no uncertainty remains.
- Select `unsure` when the annotator suspects a smell but cannot confidently determine its presence.
- If at least one smell is confirmed and another is uncertain, select `true` and record both classifications in their respective fields.

### 2.3. Classify Smell

**Column:** `classify_smell`

Contains the identifiers of all confidently identified smells.

Annotators must select only smells from the established catalog of 22 prompt smells.

**Rules:**

- Multiple smells may be selected for the same prompt.
- Each smell must be assessed independently.
- Select only smells supported by observable evidence in the prompt.
- Do not select a smell solely because it commonly co-occurs with another smell.
- Do not include uncertain classifications in this field.

If no smells are confidently identified, leave the field empty.

### 2.4. Smells (Unsure)

**Column:** `smells_unsure`

Contains the identifiers of potential smells whose presence could not be confidently established.

This field is intended to preserve uncertainty rather than force an unsupported classification.

**Rules:**

- Use only identifiers from the same 22-smell catalog.
- Include a smell when there is plausible evidence, but the evidence is insufficient or ambiguous.
- Do not include smells already classified as confidently present.
- Leave the field empty when no uncertainty exists.

An uncertain classification does not indicate that a smell is present. It indicates that further assessment may be necessary.

## 3. Annotation Procedure

Each annotator must follow the same procedure for every prompt.

**Step 1 - Read and understand the smell catalog.**

Before starting the annotation process, carefully read the complete catalog of 22 prompt smells, including their definitions, identification criteria, and examples. Ensure that the distinctions between similar or overlapping smells are understood.

**Step 2 - Read the prompt.**

Read the complete prompt to understand its objective, instructions, available context, and expected response. Refer to the smell catalog whenever necessary.

**Step 2.1 - Go back to the catalogue, if necessary**

**Step 3 - Identify confirmed smells.**

Evaluate the prompt against the definitions and identification criteria. For each smell, determine whether there is sufficient evidence to classify it as present. Record confirmed smells in `classify_smell`.

**Step 4 - Identify uncertain smells.**

If the evidence for a particular smell is ambiguous or insufficient, record it in `smells_unsure`.

**Step 5 - Determine overall smell presence.**

Complete the `smell` column according to the rules

**Step 6 — Determine review status.**

The `review_status` field is initially set to `pending` by default. After evaluating the prompt, update it to:

- `reviewed`: The evaluation is complete and no unresolved issues remain.
- `needs discussion`: One or more classification decisions require further discussion or clarification.

**Step 7 — Finalize the annotation.**

Verify that all classifications are consistent with the smell catalog. If the prompt is marked as `needs discussion`, refer it for discussion before finalizing its annotation.

## 4. General Annotation Principles

Annotators must base their decisions on observable characteristics of the prompt and the operational definitions in the catalog.

A smell must not be assigned solely because the annotator believes that the prompt could be improved.

**Important:** A prompt does not necessarily contain a prompt smell. Annotators must not assume that every prompt has a defect or feel obligated to identify at least one smell. Smells should only be assigned when there is sufficient evidence based on the definitions and identification criteria established in the catalog. If no smells are identified, the prompt must be classified as `false` in the `smell` field, and both `classify_smell` and `smells_unsure` should remain empty.

### Independent Classification

- Smells are not mutually exclusive. A single prompt may contain several distinct quality issues.
  - For example, a prompt may simultaneously contain grammatical errors, ambiguous instructions, and missing context.
- Annotators must not assume the user's unstated intentions, missing requirements, or external information.

### Handle Uncertainty Explicitly

When evidence is insufficient, use `smells_unsure` rather than guessing.

Uncertainty should be preserved for subsequent review.

The `smells_unsure` field and the `needs discussion` review status serve different purposes.

- `smells_unsure` records uncertainty regarding the presence of specific smells.
- `needs discussion` indicates that the annotation requires additional evaluation or clarification before it can be finalized.

## 5. Annotation Examples

| **Prompt** | **Review Status** | **Smell** | **Classify Smell** | **Smells Unsure** |
| --- | --- | --- | --- | --- |
| "Can you explains why this function dont works?" | reviewed | true | grammar_smell | — |
| "Fix this." | reviewed | true | `ambiguous_instruction`, `missing_context_smell` | — |
| "Explain the difference between a stack and a queue." | reviewed | false | — | — |

## 6. Final Validation

An annotation is considered complete when:

- `review_status` is `reviewed`;
- `smell` contains one of the three permitted values;
- `classify_smell` contains only valid catalog identifiers;
- `smells_unsure` contains only valid catalog identifiers;
- No smell appears simultaneously in confirmed and uncertain fields;
- The overall `smell` value is consistent with the two classification fields;
- No unresolved classification issues requiring discussion remain.

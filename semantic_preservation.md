Implement semantic_preservation scoring for optimized prompt variants.

Goal:
Add a configurable semantic preservation score that estimates how closely each optimized prompt preserves the original prompt’s intent and constraints.

Scope:
- Implement this as a small, isolated feature.
- Do not change unrelated optimizer behavior.
- Do not add LLM-based judging yet.
- Keep the implementation deterministic except for optional/local embedding calculation.
- Add tests.

Required behavior:
For every optimized variant, return:

semantic_preservation: {
  "score_percent": 91.3,
  "embedding_similarity_percent": 94.0,
  "constraint_retention_percent": 85.0,
  "method": "embedding_plus_constraints",
  "status": "high",
  "notes": []
}

Configuration:
Create an external config file for scoring weights, not hardcoded inside the scoring logic.

Suggested file:
app/config/semantic_weights.py

Initial weights:

WEIGHTS = {
    "default": (0.7, 0.3),
    "sql": (0.6, 0.4),
    "coding": (0.6, 0.4),
    "summarization": (0.8, 0.2),
}

The tuple means:
- first value = embedding similarity weight
- second value = constraint retention weight

Rules:
- weights must add up to 1.0
- if task_type is missing or unknown, use "default"
- scoring logic should read from this config
- make it easy to tune these weights later

Implementation design:
Create a new module:

app/core/semantic_preservation.py

Add functions similar to:

def get_weights_for_task_type(task_type: str | None) -> tuple[float, float]:
    ...

def compute_embedding_similarity_percent(original_prompt: str, optimized_prompt: str) -> float:
    ...

def compute_constraint_retention_percent(original_analysis: dict, optimized_prompt: str) -> float:
    ...

def compute_semantic_preservation(
    original_prompt: str,
    optimized_prompt: str,
    original_analysis: dict,
    task_type: str | None = None
) -> dict:
    ...

MVP simplification:
If embedding library integration is not already available, implement a placeholder deterministic similarity function for now using normalized token/word overlap or fuzzy matching. Keep the function name as compute_embedding_similarity_percent so it can later be replaced by real embeddings without changing the API.

Constraint retention logic:
Use original_analysis from the parser and check whether key extracted constraints are preserved in the optimized prompt.

Check these fields if present:
- task
- constraints
- output_format
- must_include
- must_avoid
- entities

Use simple case-insensitive/fuzzy matching for MVP.

Scoring:
Final score:

final_score =
    embedding_weight * embedding_similarity_percent +
    constraint_weight * constraint_retention_percent

Round percentages to one decimal place.

Status thresholds:
- score >= 95: "very_high"
- score >= 90: "high"
- score >= 80: "moderate"
- else: "low"

Notes:
Return notes when:
- unknown task_type uses default weights
- constraint retention is below 90
- score is moderate or low
- no constraints were found in original_analysis

API integration:
Update optimized variant response schema to include semantic_preservation.

Each variant should have its own score because safe, balanced, and aggressive variants may preserve meaning differently.

Testing:
Add unit tests for:
1. known task_type uses correct weights
2. unknown task_type falls back to default
3. invalid weights are rejected or raise a clear error
4. high similarity + high constraint retention gives high score
5. low constraint retention lowers final score
6. semantic_preservation field appears in each optimized variant

Important:
- Do not introduce external API calls.
- Do not require OpenAI or other LLM provider keys.
- Keep this MVP local and testable.
- Keep scoring documented as approximate, not guaranteed equivalence.

After implementation, summarize:
1. files created/modified
2. how scoring works
3. how to tune weights
4. how to run tests
5. any limitations
Then stop and wait for review.

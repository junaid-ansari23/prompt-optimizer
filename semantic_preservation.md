# Semantic Preservation Scoring (MVP)

## Goal
Estimate how closely an optimized prompt preserves the original intent and constraints.

---

## Output (per variant)

semantic_preservation:
  score_percent: 91.3
  embedding_similarity_percent: 94.0
  constraint_retention_percent: 85.0
  status: "high"

---

## Design Principles
- Deterministic (no LLM judging)
- Config-driven weights (by task type)
- Isolated module: app/core/semantic_preservation.py
- Replaceable embedding logic (future-ready)

---

## Scoring Formula

final_score =
  embedding_weight * embedding_similarity +
  constraint_weight * constraint_retention

---

## Weights (config)

default        = (0.7, 0.3)
coding         = (0.6, 0.4)
summarization  = (0.8, 0.2)

> weights must sum to 1.0

---

## MVP Logic

Embedding Similarity:
- token overlap / fuzzy match (placeholder)

Constraint Retention:
- task
- constraints
- output_format
- must_include
- must_avoid
- entities

---

## Status Thresholds

>= 95   → very_high  
>= 90   → high  
>= 80   → moderate  
<  80   → low  

---

## Testing

- correct weight selection
- fallback to default
- constraint impact on score
- field present in all variants

---

## Principle

Treat prompts like system design:
explicit constraints → predictable outcomes

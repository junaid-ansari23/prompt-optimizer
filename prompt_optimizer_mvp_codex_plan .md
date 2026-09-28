# Prompt Token Optimization MVP — Incremental Implementation Plan for Codex

## Goal

Build an **MVP-first prompt token optimization app** that:
- accepts a user prompt,
- analyzes and tokenizes it,
- produces a safer optimized version,
- shows token savings,
- keeps the implementation incremental so each step can be reviewed before moving forward.

This plan is intentionally split into **small reviewable steps**. Codex should complete **only one step at a time** unless explicitly instructed to continue.

---

## Important Working Rules for Codex

1. **Do not implement everything at once.**
2. Complete **only the requested step**.
3. Keep each step small enough that the resulting diff is easy to review.
4. After each step:
   - summarize what changed,
   - list created/modified files,
   - explain how to run or test that step,
   - wait for approval before starting the next step.
5. Prefer clear, maintainable code over premature abstraction.
6. Add short comments only where they help readability.
7. Do not add advanced infrastructure unless requested.
8. Avoid speculative features not required by the current step.

---

## Recommended Tech Stack for MVP

### Backend
- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn

### Token counting / optimization helpers
- tiktoken
- rapidfuzz (optional in later step)
- standard Python `re`

### Storage
- Start with in-memory or file-based storage
- Postgres can be added later if needed

### Frontend
- No frontend in initial steps
- Start with API + CLI/manual curl testing
- Simple React UI can come later

### Testing
- pytest

---

## MVP Scope

### In Scope
- prompt input API
- token counting
- basic prompt analysis
- rule-based prompt cleanup
- generate optimized prompt variants:
  - safe
  - balanced
  - aggressive
- compare token counts before/after
- return structured JSON response
- basic tests

### Out of Scope for initial MVP
- authentication
- database persistence
- multi-user features
- billing
- model provider integrations
- LLM-based rewriting
- prompt benchmarking dashboard
- CI/CD pipeline
- full frontend app

---

## Suggested Project Structure

```text
prompt-optimizer/
  app/
    main.py
    api/
      routes_optimize.py
    core/
      tokenizer.py
      parser.py
      optimizer.py
      schemas.py
    services/
      optimize_service.py
    tests/
      test_health.py
      test_tokenizer.py
      test_optimizer.py
  requirements.txt
  README.md
```

This can evolve gradually. Do not create all files in step 1 unless needed.

---

## Functional Requirements

### Input
User submits:
- raw prompt text
- optional mode (default: balanced)

### Output
Return:
- original prompt
- token count for original
- parsed sections if available
- optimized variants
- token counts for each variant
- token savings
- notes about what was removed or compressed

### Example response shape
```json
{
  "original_prompt": "Write a concise SQL query to ...",
  "original_tokens": 120,
  "analysis": {
    "task": "...",
    "constraints": ["..."],
    "format": "...",
    "context": ["..."]
  },
  "variants": [
    {
      "mode": "safe",
      "prompt": "...",
      "tokens": 104,
      "saved_tokens": 16
    },
    {
      "mode": "balanced",
      "prompt": "...",
      "tokens": 88,
      "saved_tokens": 32
    }
  ]
}
```

---

## Step-by-Step Implementation Plan

## Step 1 — Bootstrap the backend skeleton

### Objective
Create the minimal FastAPI application with:
- project structure,
- health endpoint,
- dependency file,
- README with run instructions.

### Deliverables
- FastAPI app entry point
- `/health` endpoint
- `requirements.txt`
- basic `README.md`
- one simple test for health endpoint

### Acceptance Criteria
- app starts locally
- `GET /health` returns success JSON
- test passes

### Notes to Codex
Keep this step very small. Do not implement prompt optimization yet.

---

## Step 2 — Add token counting utility

### Objective
Implement a reusable token counting module.

### Deliverables
- `tokenizer.py`
- function to count tokens for a string
- support for a default encoding/model
- unit tests for token counting behavior
- optional endpoint or internal function usage only

### Acceptance Criteria
- can count tokens for arbitrary prompt text
- code is isolated and reusable
- tests run successfully

### Notes to Codex
Do not add optimization logic yet. Only token counting.

---

## Step 3 — Create request/response schemas

### Objective
Define the API contract for prompt optimization.

### Deliverables
- Pydantic request model
- Pydantic response models
- optimization mode enum or literal values:
  - safe
  - balanced
  - aggressive

### Acceptance Criteria
- schemas validate correctly
- route stubs can use them
- tests cover validation basics

### Notes to Codex
Do not implement full optimization behavior yet. Focus on clean schemas.

---

## Step 4 — Add `/optimize` API route stub

### Objective
Create the main route with placeholder behavior.

### Deliverables
- `POST /optimize`
- accepts prompt input
- returns original prompt and original token count
- returns placeholder variants for now

### Acceptance Criteria
- route works end to end
- request/response uses schemas
- tests validate response shape

### Notes to Codex
Still no real optimization logic. Keep it simple and reviewable.

---

## Step 5 — Implement prompt parser (lightweight heuristic version)

### Objective
Extract rough structure from the prompt.

### Initial heuristic targets
Try to detect:
- task
- constraints
- output format
- context
- examples

### Deliverables
- `parser.py`
- simple heuristic parsing rules
- parser unit tests with 3-5 prompt examples

### Acceptance Criteria
- parser returns structured sections
- no NLP heavy dependencies yet
- logic is readable and extendable

### Notes to Codex
Use lightweight heuristics only. Avoid overengineering.

---

## Step 6 — Implement rule-based cleanup engine

### Objective
Build the first optimization layer using deterministic rules.

### Rules to include
- trim extra whitespace
- remove repeated filler phrases
- collapse redundant wording
- normalize formatting
- optionally convert long prose into compact labeled sections

### Deliverables
- `optimizer.py`
- helper functions for cleanup rules
- tests for each main rule

### Acceptance Criteria
- optimizer reduces tokens on common verbose prompts
- original intent remains broadly preserved
- rules are modular and easy to tweak

### Notes to Codex
Do not add LLM integration. Deterministic rules only.

---

## Step 7 — Generate optimization variants

### Objective
Produce multiple levels of compression.

### Variants
- **safe**: minimal cleanup only
- **balanced**: moderate cleanup + restructuring
- **aggressive**: strongest cleanup that still preserves core constraints

### Deliverables
- variant generation logic
- each variant includes:
  - optimized prompt
  - token count
  - saved tokens
  - notes on transformations applied

### Acceptance Criteria
- all three modes are returned
- token counts are included
- tests verify variant ordering and savings

### Notes to Codex
Keep transformation tracking simple, such as a list of applied rule names.

---

## Step 8 — Add optimization service layer

### Objective
Separate route logic from business logic.

### Deliverables
- `optimize_service.py`
- orchestration flow:
  1. count original tokens
  2. parse prompt
  3. generate variants
  4. count optimized tokens
  5. build response model

### Acceptance Criteria
- route becomes thin
- service owns optimization workflow
- tests cover service flow

### Notes to Codex
Refactor only as much as needed for clarity.

---

## Step 9 — Add robust tests with sample prompts

### Objective
Create a useful MVP test set.

### Sample prompt categories
- SQL prompt
- coding prompt
- summarization prompt
- extraction prompt
- verbose instruction-heavy prompt

### Deliverables
- broader unit tests
- API integration tests
- assertions that optimized variants usually save tokens

### Acceptance Criteria
- tests cover real examples
- failures are easy to understand
- app behavior feels stable

### Notes to Codex
No benchmark harness yet. Just practical coverage.

---

## Step 10 — Improve README and developer usage

### Objective
Make the MVP runnable by another developer immediately.

### Deliverables
- setup steps
- run instructions
- test instructions
- sample curl requests
- sample JSON response
- short explanation of current limitations

### Acceptance Criteria
- a new developer can run the app quickly
- README reflects actual implementation

---

## Step 11 — Optional CLI helper for local experimentation

### Objective
Add a simple CLI to test prompt optimization without calling the API.

### Deliverables
- optional `cli.py`
- accepts prompt from file or stdin
- prints variants and token savings

### Acceptance Criteria
- local manual testing becomes easier

### Notes to Codex
Only do this if requested after core API is stable.

---

## Step 12 — Optional next phase after MVP approval

Only start after explicit approval.

### Possible next-phase features
- LLM-based rewrite engine
- semantic preservation scoring
- prompt diff view
- experiment history
- PostgreSQL persistence
- frontend UI
- benchmark runner
- model-specific optimization strategies

---

## Coding Guidelines for Codex

### General
- Prefer small commits/PR-style changes
- Keep function names explicit
- Avoid deep inheritance
- Prefer simple pure functions where possible

### API style
- return clear JSON
- validate inputs
- use consistent field names

### Testing
- write tests for each step where relevant
- do not skip tests for utility modules

### Error handling
- handle empty prompt input cleanly
- return validation errors instead of silent failures

---

## Definition of Done for MVP

The MVP is done when:
1. user can send a prompt to `/optimize`,
2. system returns original token count,
3. system returns safe/balanced/aggressive optimized variants,
4. token savings are visible,
5. parser and optimizer logic are covered by basic tests,
6. project is easy to run locally.

---

## First Prompt to Give Codex

Use this as the initial instruction to Codex:

```text
Please implement only Step 1 from the attached project plan.

Step 1 scope:
- bootstrap a minimal FastAPI backend
- add a /health endpoint
- add requirements.txt
- add README with local run instructions
- add one simple health test

Important rules:
- do not implement future steps
- keep changes small and reviewable
- after implementation, summarize:
  1. files created/modified
  2. what was implemented
  3. how to run it
  4. what remains for Step 2
- then stop and wait for review
```

---

## Suggested Follow-up Prompt Pattern for Codex

For each next step, use this pattern:

```text
Please implement only Step N from the project plan.

Constraints:
- do not work on Step N+1 or beyond
- keep changes reviewable
- prefer minimal necessary changes
- include/update tests for this step
- after finishing, provide:
  1. summary of changes
  2. files changed
  3. how to test
  4. any assumptions or open issues

Then stop and wait for my review.
```

---

## Final Note

This plan is intentionally conservative.
The goal is not to build a perfect optimizer immediately.
The goal is to build a **reviewable, working MVP foundation** that can evolve safely.

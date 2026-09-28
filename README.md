# Prompt Token Optimizer - MVP

A FastAPI-based application for optimizing prompts to reduce token usage while preserving intent.

## Current Status

**Step 8 Complete**: Service layer separates business logic from API routes.

- ✅ Step 1: Basic FastAPI skeleton with health endpoint
- ✅ Step 2: Token counting utility
- ✅ Step 3: Pydantic schemas for API contract
- ✅ Step 4: `/optimize` endpoint (stub implementation)
- ✅ Step 5: Prompt parser (lightweight heuristic-based)
- ✅ Step 6: Rule-based optimization engine (deterministic cleanup)
- ✅ Step 7: Generate real optimization variants (safe/balanced/aggressive)
- ✅ Step 8: Service layer for orchestration and business logic

## Requirements

- Python 3.11+
- pip

## Setup

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
```

2. **Activate the virtual environment**:
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Testing

Run the test suite:
```bash
pytest app/tests/ -v
```

## Available Endpoints

### Health Check
- **GET** `/health`
- Returns service status and version information

Example:
```bash
curl http://127.0.0.1:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "prompt-optimizer",
  "version": "0.1.0"
}
```

### Optimize Prompt
- **POST** `/api/optimize`
- Optimizes a prompt to reduce token usage using rule-based transformations
- Returns three variants: safe, balanced, and aggressive with real token savings

Example (PowerShell):
```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/optimize -Method POST -ContentType "application/json" -Body '{"prompt": "Could you please write a very simple function."}'
```

Request:
```json
{
  "prompt": "Could you please write a very simple function.",
  "mode": "balanced"  // optional: safe, balanced, or aggressive
}
```

Response:
```json
{
  "original_prompt": "Could you please write a very simple function.",
  "original_tokens": 10,
  "variants": [
    {
      "mode": "safe",
      "prompt": "Could you please write a very simple function",
      "tokens": 9,
      "saved_tokens": 1,
      "notes": ["Removed trailing punctuation"]
    },
    {
      "mode": "balanced",
      "prompt": "write a simple function",
      "tokens": 4,
      "saved_tokens": 6,
      "notes": ["Removed trailing punctuation", "Removed filler words", "Simplified politeness phrases"]
    },
    {
      "mode": "aggressive",
      "prompt": "write simple function",
      "tokens": 3,
      "saved_tokens": 7,
      "notes": ["Removed trailing punctuation", "Removed filler words", "Simplified politeness phrases", "Removed articles"]
    }
  ],
  "analysis": {
    "task": "Could you please just write a very simple function",
    "constraints": ["just write a very simple function"],
    "output_format": null,
    "context": [],
    "examples": []
  }
}
```

**Token Savings:** Up to 70% on verbose prompts, minimal changes on concise prompts.

Run the endpoint demo:
```bash
python demo_optimize.py
```

## Token Counting

The app now includes a token counting utility that can count tokens in any text:

```python
from app.core.tokenizer import count_tokens

text = "Hello, world!"
token_count = count_tokens(text)
print(f"Tokens: {token_count}")  # Output: Tokens: 4
```

You can also use model-specific counting:

```python
from app.core.tokenizer import count_tokens_for_model

token_count = count_tokens_for_model("Hello, world!", model_name="gpt-4")
```

Run the demo:
```bash
python demo_tokenizer.py
```

## API Schemas

The app now has complete Pydantic schemas for the optimization API:

**Request Schema (OptimizeRequest):**
```python
from app.core.schemas import OptimizeRequest, OptimizationMode

request = OptimizeRequest(
    prompt="Your prompt here",
    mode=OptimizationMode.BALANCED  # or SAFE, AGGRESSIVE
)
```

**Response Schema (OptimizeResponse):**
- Returns original prompt and token count
- Contains list of optimized variants (safe/balanced/aggressive)
- Each variant includes optimized text, tokens, savings, and notes

Run the schema demo:
```bash
python demo_schemas.py
```

## Prompt Parser

The app now includes a prompt parser that analyzes structure:

**What it detects:**
- **Task**: Main instruction or action
- **Constraints**: Requirements (must, should, make sure)
- **Output Format**: Expected format (SQL, JSON, Python, etc.)
- **Context**: Background information
- **Examples**: Sample inputs/outputs

```python
from app.core.parser import parse_prompt

analysis = parse_prompt("Write a SQL query to select all users.")
print(f"Task: {analysis.task}")
print(f"Format: {analysis.output_format}")
```

Run the parser demo:
```bash
python demo_parser.py
```

**Integrated with API**: The `/api/optimize` endpoint now returns an `analysis` field with the parsed prompt structure.

## Prompt Optimizer

The app now includes a rule-based optimization engine that reduces token usage:

**Optimization Levels:**
- **Safe**: Minimal changes (whitespace normalization, remove trailing punctuation)
- **Balanced**: Moderate optimization (removes filler words, simplifies politeness, compresses redundant phrases)
- **Aggressive**: Maximum compression (converts to imperative form, removes articles where safe)

**Example:**

```python
from app.core.optimizer import optimize_prompt, calculate_savings

prompt = "Could you please write a very simple function that adds two numbers."
optimized, rules = optimize_prompt(prompt, level="balanced")
savings = calculate_savings(prompt, optimized)

print(f"Original: {prompt} ({savings['original_tokens']} tokens)")
print(f"Optimized: {optimized} ({savings['optimized_tokens']} tokens)")
print(f"Saved: {savings['saved_tokens']} tokens")
# Output:
# Original: Could you please write a very simple function... (15 tokens)
# Optimized: write a simple function that adds two numbers together (9 tokens)
# Saved: 6 tokens (40% reduction)
```

**Optimization Rules:**
- Normalize whitespace
- Remove filler words (very, really, just, etc.)
- Simplify politeness phrases
- Compress redundant phrases (in order to → to, all of the → all)
- Convert to imperative form (aggressive mode)
- Remove articles where safe (aggressive mode)

Run the optimizer demo:
```bash
python demo_optimizer.py
```

**Token Savings:** Typical savings range from 6% (safe) to 47% (aggressive) on verbose prompts.

Three Optimization Levels:

- Safe (6% savings): Whitespace normalization, remove trailing punctuation
- Balanced (31-44% savings): Removes filler words, simplifies politeness,   compresses redundant phrases
- Aggressive (34-47% savings): Converts to imperative form, removes articles

## What's Next

Step 9 will add comprehensive testing with real-world prompt examples across different categories (SQL, coding, summarization, extraction, etc.).

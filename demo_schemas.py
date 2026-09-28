"""Demo script showing how to use the Pydantic schemas."""

import json
from app.core.schemas import (
    OptimizationMode,
    OptimizeRequest,
    PromptVariant,
    OptimizeResponse
)

print("=" * 60)
print("Pydantic Schemas Demo")
print("=" * 60)

# Demo 1: Creating a request
print("\n1. Creating an OptimizeRequest:")
print("-" * 60)

request = OptimizeRequest(
    prompt="Please write a very detailed SQL query to select all users.",
    mode=OptimizationMode.BALANCED
)

print(f"Prompt: {request.prompt}")
print(f"Mode: {request.mode.value}")
print(f"JSON: {request.model_dump_json(indent=2)}")

# Demo 2: Default mode
print("\n2. Request with default mode (BALANCED):")
print("-" * 60)

default_request = OptimizeRequest(prompt="Test prompt")
print(f"Default mode: {default_request.mode.value}")

# Demo 3: Creating response with variants
print("\n3. Creating an OptimizeResponse:")
print("-" * 60)

variants = [
    PromptVariant(
        mode=OptimizationMode.SAFE,
        prompt="Write detailed SQL query to select all users.",
        tokens=9,
        saved_tokens=2,
        notes=["Removed filler words"]
    ),
    PromptVariant(
        mode=OptimizationMode.BALANCED,
        prompt="SQL query: select all users",
        tokens=6,
        saved_tokens=5,
        notes=["Removed filler words", "Compressed format"]
    ),
    PromptVariant(
        mode=OptimizationMode.AGGRESSIVE,
        prompt="SELECT * FROM users",
        tokens=5,
        saved_tokens=6,
        notes=["Direct SQL output"]
    )
]

response = OptimizeResponse(
    original_prompt="Please write a very detailed SQL query to select all users.",
    original_tokens=11,
    variants=variants
)

print(json.dumps(response.model_dump(), indent=2))

# Demo 4: Validation
print("\n4. Schema Validation:")
print("-" * 60)

try:
    # This will fail - empty prompt
    invalid_request = OptimizeRequest(prompt="")
except Exception as e:
    print(f"✗ Empty prompt rejected: {type(e).__name__}")

try:
    # This will fail - invalid mode
    invalid_request = OptimizeRequest(prompt="Test", mode="super_mode")
except Exception as e:
    print(f"✗ Invalid mode rejected: {type(e).__name__}")

try:
    # This will fail - negative tokens
    invalid_variant = PromptVariant(
        mode=OptimizationMode.SAFE,
        prompt="Test",
        tokens=-5,
        saved_tokens=0
    )
except Exception as e:
    print(f"✗ Negative tokens rejected: {type(e).__name__}")

print("\n✓ All validations working correctly!")

# Demo 5: Available modes
print("\n5. Available Optimization Modes:")
print("-" * 60)

for mode in OptimizationMode:
    print(f"  - {mode.value}: {mode.name}")

print("\n" + "=" * 60)
print("Demo complete!")
print("=" * 60)

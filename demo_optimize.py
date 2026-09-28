"""Demo script for testing the /optimize endpoint."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_variant(variant, original_tokens):
    """Print variant details."""
    savings_pct = (variant['saved_tokens'] / original_tokens * 100) if original_tokens > 0 else 0
    print(f"\n  [{variant['mode'].upper()}]")
    print(f"  Optimized: \"{variant['prompt']}\"")
    print(f"  Tokens: {variant['tokens']} (saved {variant['saved_tokens']}, {savings_pct:.1f}%)")
    if variant.get('notes'):
        print(f"  Applied: {', '.join(variant['notes'][:3])}")  # Show first 3 rules

print_header("PROMPT OPTIMIZER API DEMO")
print("\nMake sure the server is running: uvicorn app.main:app --reload\n")

# Demo 1: Verbose prompt with real optimization
print_header("Example 1: Verbose Polite Prompt")

verbose_prompt = "Could you please very kindly write a really detailed SQL query to select all users."
print(f"\nOriginal: \"{verbose_prompt}\"")

response = requests.post(
    f"{BASE_URL}/api/optimize",
    json={"prompt": verbose_prompt}
)

if response.status_code == 200:
    result = response.json()
    print(f"Original tokens: {result['original_tokens']}")
    
    for variant in result['variants']:
        print_variant(variant, result['original_tokens'])
else:
    print(f"Error: {response.status_code}")

# Demo 2: Redundant phrasing
print_header("Example 2: Redundant Phrases")

redundant_prompt = "In order to process all of the records, I need you to write a function."
print(f"\nOriginal: \"{redundant_prompt}\"")

response = requests.post(
    f"{BASE_URL}/api/optimize",
    json={"prompt": redundant_prompt}
)

if response.status_code == 200:
    result = response.json()
    print(f"Original tokens: {result['original_tokens']}")
    
    # Just show balanced for brevity
    balanced = next(v for v in result['variants'] if v['mode'] == 'balanced')
    print_variant(balanced, result['original_tokens'])
else:
    print(f"Error: {response.status_code}")

# Demo 3: Already concise prompt
print_header("Example 3: Already Concise Prompt")

concise_prompt = "Write function to add numbers"
print(f"\nOriginal: \"{concise_prompt}\"")

response = requests.post(
    f"{BASE_URL}/api/optimize",
    json={"prompt": concise_prompt}
)

if response.status_code == 200:
    result = response.json()
    print(f"Original tokens: {result['original_tokens']}")
    
    aggressive = next(v for v in result['variants'] if v['mode'] == 'aggressive')
    print_variant(aggressive, result['original_tokens'])
    print("\n  Note: Minimal optimization on already concise prompts")
else:
    print(f"Error: {response.status_code}")

# Demo 4: Comparison of all three modes
print_header("Example 4: Comparing All Optimization Levels")

comparison_prompt = "Please, if you would be so kind, could you write a very simple function that adds two numbers together."
print(f"\nOriginal: \"{comparison_prompt}\"")

response = requests.post(
    f"{BASE_URL}/api/optimize",
    json={"prompt": comparison_prompt}
)

if response.status_code == 200:
    result = response.json()
    print(f"Original tokens: {result['original_tokens']}")
    
    for variant in result['variants']:
        print_variant(variant, result['original_tokens'])
else:
    print(f"Error: {response.status_code}")

# Demo 5: Show prompt analysis
print_header("Example 5: Prompt Analysis")

analysis_prompt = "Write a SQL query to select all users. Make sure to handle errors."
print(f"\nOriginal: \"{analysis_prompt}\"")

response = requests.post(
    f"{BASE_URL}/api/optimize",
    json={"prompt": analysis_prompt}
)

if response.status_code == 200:
    result = response.json()
    print(f"\nPrompt Analysis:")
    if result.get('analysis'):
        for key, value in result['analysis'].items():
            if value:  # Only show non-empty fields
                print(f"  {key}: {value}")
    
    balanced = next(v for v in result['variants'] if v['mode'] == 'balanced')
    print_variant(balanced, result['original_tokens'])
else:
    print(f"Error: {response.status_code}")

# Demo 6: Error handling
print_header("Example 6: Error Handling")

print("\nTesting empty prompt:")
response = requests.post(
    f"{BASE_URL}/api/optimize",
    json={"prompt": ""}
)
print(f"  Status: {response.status_code} ({'✓ Correctly rejected' if response.status_code == 422 else '✗ Unexpected'})")

print("\nTesting invalid mode:")
response = requests.post(
    f"{BASE_URL}/api/optimize",
    json={"prompt": "Test", "mode": "super_aggressive"}
)
print(f"  Status: {response.status_code} ({'✓ Correctly rejected' if response.status_code == 422 else '✗ Unexpected'})")

print("\n" + "=" * 80)
print("  DEMO COMPLETE")
print("=" * 80)
print("\nKey Takeaways:")
print("  • Safe mode: Minimal changes (6-10% savings)")
print("  • Balanced mode: Good compromise (20-40% savings)")
print("  • Aggressive mode: Maximum reduction (30-50% savings)")
print("  • Concise prompts see minimal changes")
print("  • All variants preserve core meaning and constraints")
print()
print("Demo complete!")
print("=" * 70)
print("\nNext steps:")
print("- Step 5: Add prompt parser (detect structure)")
print("- Step 6: Add optimization rules (remove filler words, etc.)")
print("- Step 7: Generate real optimized variants")

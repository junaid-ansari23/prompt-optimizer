"""Demo script for testing the prompt parser."""

from app.core.parser import parse_prompt, get_prompt_summary
import json

print("=" * 70)
print("Prompt Parser Demo")
print("=" * 70)

# Demo 1: Simple SQL prompt
print("\n1. Parsing a SQL Prompt:")
print("-" * 70)

sql_prompt = "Write a SQL query to select all users from the database."
analysis = parse_prompt(sql_prompt)

print(f"Prompt: {sql_prompt}")
print(f"\nAnalysis:")
print(f"  Task: {analysis.task}")
print(f"  Constraints: {analysis.constraints}")
print(f"  Output Format: {analysis.output_format}")
print(f"  Context: {analysis.context}")
print(f"  Examples: {analysis.examples}")

# Demo 2: Detailed coding prompt with constraints
print("\n2. Parsing a Detailed Coding Prompt:")
print("-" * 70)

coding_prompt = """
Create a Python function to calculate the factorial of a number.
It must handle negative numbers gracefully and should be efficient.
The function must include error handling and should return an integer.
"""

analysis = parse_prompt(coding_prompt)

print(f"Prompt: {coding_prompt.strip()}")
print(f"\nAnalysis:")
print(f"  Task: {analysis.task}")
print(f"  Constraints ({len(analysis.constraints)}):")
for constraint in analysis.constraints:
    print(f"    - {constraint}")
print(f"  Output Format: {analysis.output_format}")

# Demo 3: Prompt with context and examples
print("\n3. Parsing a Prompt with Context and Examples:")
print("-" * 70)

context_prompt = """
Given a list of user records in our database, write a function to find
users created in the last 30 days. Assume each record has a creation_date field.
Example: user = {'name': 'John', 'creation_date': '2026-04-01'}
The output should be in JSON format.
"""

analysis = parse_prompt(context_prompt)

print(f"Prompt: {context_prompt.strip()}")
print(f"\nAnalysis:")
print(f"  Task: {analysis.task}")
print(f"  Context ({len(analysis.context)}):")
for ctx in analysis.context:
    print(f"    - {ctx[:60]}...")
print(f"  Output Format: {analysis.output_format}")
print(f"  Examples ({len(analysis.examples)}):")
for example in analysis.examples:
    print(f"    - {example[:60]}...")

# Demo 4: Verbose prompt with everything
print("\n4. Parsing a Comprehensive Prompt:")
print("-" * 70)

verbose_prompt = """
Please write a very detailed SQL query that will select all users from 
our database where the account was created in the last 30 days.
The query must include the user's email and username.
It should be optimized for performance and must handle NULL values.
Make sure to order the results by creation date descending.
Given that we have a users table with columns: id, email, username, created_at.
Example output should look like:
  email         | username  | created_at
  john@test.com | john123   | 2026-04-15
"""

analysis = parse_prompt(verbose_prompt)

print(f"Prompt length: {len(verbose_prompt)} characters")
print(f"\nFull Analysis:")
print(json.dumps(analysis.model_dump(exclude_none=True), indent=2))

# Demo 5: Using get_prompt_summary
print("\n5. Getting Summary Dictionary:")
print("-" * 70)

summary = get_prompt_summary("Generate a list of prime numbers in Python code.")
print(json.dumps(summary, indent=2))

# Demo 6: Edge cases
print("\n6. Parsing Edge Cases:")
print("-" * 70)

edge_cases = [
    "",
    "Hello",
    "Do something.",
    "Write code."
]

for prompt in edge_cases:
    analysis = parse_prompt(prompt)
    print(f"Prompt: '{prompt}' -> Task: {analysis.task}")

print("\n" + "=" * 70)
print("Demo complete!")
print("=" * 70)
print("\nKey Features:")
print("- ✓ Extracts main task/instruction")
print("- ✓ Identifies constraints (must, should, make sure)")
print("- ✓ Detects output format (SQL, JSON, Python, etc.)")
print("- ✓ Captures contextual information")
print("- ✓ Finds examples in the prompt")
print("\nNext Step:")
print("- Step 6: Use parser output to guide optimization")

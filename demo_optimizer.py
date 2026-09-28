"""Demo script for the prompt optimizer."""

from app.core.optimizer import optimize_prompt, calculate_savings


def demo_optimization(prompt: str, level: str = "balanced"):
    """Demonstrate optimization for a given prompt and level."""
    print(f"\n{'='*80}")
    print(f"OPTIMIZATION LEVEL: {level.upper()}")
    print(f"{'='*80}")
    print(f"\nOriginal prompt:")
    print(f"  \"{prompt}\"")
    
    optimized, rules = optimize_prompt(prompt, level=level)
    savings = calculate_savings(prompt, optimized)
    
    print(f"\nOptimized prompt:")
    print(f"  \"{optimized}\"")
    
    print(f"\nApplied rules:")
    for rule in rules:
        print(f"  • {rule}")
    
    print(f"\nToken savings:")
    print(f"  Original:  {savings['original_tokens']} tokens")
    print(f"  Optimized: {savings['optimized_tokens']} tokens")
    print(f"  Saved:     {savings['saved_tokens']} tokens ({savings['saved_tokens'] / max(savings['original_tokens'], 1) * 100:.1f}%)")


def main():
    """Run optimizer demonstrations."""
    print("\n" + "="*80)
    print("PROMPT OPTIMIZER DEMONSTRATION")
    print("="*80)
    
    # Example 1: Verbose SQL prompt
    print("\n\n### Example 1: Verbose SQL Prompt ###")
    prompt1 = """Please, if you would be so kind, could you possibly write a very detailed 
and comprehensive SQL query that will select all of the users from our database."""
    
    demo_optimization(prompt1.replace('\n', ' '), level="safe")
    demo_optimization(prompt1.replace('\n', ' '), level="balanced")
    demo_optimization(prompt1.replace('\n', ' '), level="aggressive")
    
    # Example 2: Polite coding request
    print("\n\n### Example 2: Polite Coding Request ###")
    prompt2 = "Could you please just write a very simple function that adds two numbers together."
    
    demo_optimization(prompt2, level="safe")
    demo_optimization(prompt2, level="balanced")
    demo_optimization(prompt2, level="aggressive")
    
    # Example 3: Redundant phrasing
    print("\n\n### Example 3: Redundant Phrasing ###")
    prompt3 = "In order to process all of the records, I need you to write a function that iterates through each and every row."
    
    demo_optimization(prompt3, level="balanced")
    
    # Example 4: Technical prompt with constraints
    print("\n\n### Example 4: Technical Prompt with Constraints ###")
    prompt4 = "Please write a function that must handle errors gracefully and should be very efficient and really performant."
    
    demo_optimization(prompt4, level="balanced")
    
    # Example 5: Short prompt (minimal optimization)
    print("\n\n### Example 5: Already Concise Prompt ###")
    prompt5 = "Write Python function to sort list"
    
    demo_optimization(prompt5, level="aggressive")
    
    print("\n\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nKey Observations:")
    print("  • Safe level: Minimal changes (whitespace, punctuation)")
    print("  • Balanced level: Removes filler words and simplifies politeness")
    print("  • Aggressive level: Maximum compression (imperative form, article removal)")
    print("  • Optimization preserves core meaning and constraints")
    print("  • Already concise prompts see minimal changes")
    print()


if __name__ == "__main__":
    main()

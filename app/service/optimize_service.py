"""Service layer for prompt optimization.

This module orchestrates the optimization workflow, separating business logic
from API route handlers.
"""

from app.core.schemas import OptimizeRequest, OptimizeResponse, PromptVariant, OptimizationMode
from app.core.tokenizer import count_tokens
from app.core.parser import parse_prompt
from app.core.optimizer import optimize_prompt as apply_optimization


def optimize_prompt_service(request: OptimizeRequest) -> OptimizeResponse:
    """
    Orchestrate the prompt optimization workflow.
    
    This is the main service function that coordinates:
    1. Token counting for the original prompt
    2. Prompt structure parsing
    3. Variant generation for all optimization levels
    4. Token counting for optimized variants
    5. Response model construction
    
    Args:
        request: OptimizeRequest containing the prompt and optional mode
    
    Returns:
        OptimizeResponse with original prompt, token counts, variants, and analysis
    
    Raises:
        ValueError: If the prompt is invalid or optimization fails
    """
    # Step 1: Count tokens in the original prompt
    original_tokens = count_tokens(request.prompt)
    
    # Step 2: Parse the prompt structure
    analysis = parse_prompt(request.prompt)
    
    # Step 3: Generate optimized variants for all three levels
    variants = generate_optimization_variants(request.prompt, original_tokens)
    
    # Step 4: Build the response (token counting already done in variant generation)
    response = OptimizeResponse(
        original_prompt=request.prompt,
        original_tokens=original_tokens,
        variants=variants,
        analysis=analysis.model_dump(exclude_none=True) if analysis else None
    )
    
    return response


def generate_optimization_variants(prompt: str, original_tokens: int) -> list[PromptVariant]:
    """
    Generate optimized variants for all three optimization levels.
    
    Creates safe, balanced, and aggressive variants by applying different
    sets of optimization rules to the original prompt.
    
    Args:
        prompt: The original prompt text
        original_tokens: Token count of the original prompt
    
    Returns:
        List of PromptVariant objects (safe, balanced, aggressive)
    """
    variants = []
    
    # Generate safe variant (minimal optimization)
    safe_optimized, safe_rules = apply_optimization(prompt, level="safe")
    safe_tokens = count_tokens(safe_optimized)
    variants.append(
        create_variant(
            mode=OptimizationMode.SAFE,
            optimized_text=safe_optimized,
            optimized_tokens=safe_tokens,
            original_tokens=original_tokens,
            applied_rules=safe_rules
        )
    )
    
    # Generate balanced variant (moderate optimization)
    balanced_optimized, balanced_rules = apply_optimization(prompt, level="balanced")
    balanced_tokens = count_tokens(balanced_optimized)
    variants.append(
        create_variant(
            mode=OptimizationMode.BALANCED,
            optimized_text=balanced_optimized,
            optimized_tokens=balanced_tokens,
            original_tokens=original_tokens,
            applied_rules=balanced_rules
        )
    )
    
    # Generate aggressive variant (maximum optimization)
    aggressive_optimized, aggressive_rules = apply_optimization(prompt, level="aggressive")
    aggressive_tokens = count_tokens(aggressive_optimized)
    variants.append(
        create_variant(
            mode=OptimizationMode.AGGRESSIVE,
            optimized_text=aggressive_optimized,
            optimized_tokens=aggressive_tokens,
            original_tokens=original_tokens,
            applied_rules=aggressive_rules
        )
    )
    
    return variants


def create_variant(
    mode: OptimizationMode,
    optimized_text: str,
    optimized_tokens: int,
    original_tokens: int,
    applied_rules: list[str]
) -> PromptVariant:
    """
    Create a PromptVariant object with calculated savings.
    
    Args:
        mode: The optimization mode (safe/balanced/aggressive)
        optimized_text: The optimized prompt text
        optimized_tokens: Token count of optimized prompt
        original_tokens: Token count of original prompt
        applied_rules: List of optimization rule names that were applied
    
    Returns:
        PromptVariant object with all fields populated
    """
    saved_tokens = original_tokens - optimized_tokens
    notes = applied_rules if applied_rules else ["No optimization needed"]
    
    return PromptVariant(
        mode=mode,
        prompt=optimized_text,
        tokens=optimized_tokens,
        saved_tokens=saved_tokens,
        notes=notes
    )


def calculate_optimization_metrics(variants: list[PromptVariant], original_tokens: int) -> dict:
    """
    Calculate aggregate optimization metrics across all variants.
    
    Args:
        variants: List of optimization variants
        original_tokens: Token count of original prompt
    
    Returns:
        Dictionary with metrics:
        - max_savings: Maximum tokens saved across variants
        - max_savings_pct: Maximum savings percentage
        - avg_savings: Average tokens saved
        - best_mode: Mode that achieved maximum savings
    """
    if not variants or original_tokens == 0:
        return {
            "max_savings": 0,
            "max_savings_pct": 0.0,
            "avg_savings": 0.0,
            "best_mode": None
        }
    
    max_saved = max(v.saved_tokens for v in variants)
    avg_saved = sum(v.saved_tokens for v in variants) / len(variants)
    max_savings_pct = (max_saved / original_tokens * 100) if original_tokens > 0 else 0.0
    best_variant = max(variants, key=lambda v: v.saved_tokens)
    
    return {
        "max_savings": max_saved,
        "max_savings_pct": round(max_savings_pct, 1),
        "avg_savings": round(avg_saved, 1),
        "best_mode": best_variant.mode.value
    }

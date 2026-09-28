"""Rule-based prompt optimizer."""

import re
from typing import Optional
from app.core.tokenizer import count_tokens


class OptimizationRule:
    """Base class for optimization rules."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def apply(self, text: str) -> str:
        """Apply the optimization rule to text."""
        raise NotImplementedError


def optimize_prompt(prompt: str, level: str = "balanced") -> tuple[str, list[str]]:
    """
    Optimize a prompt using rule-based transformations.
    
    Args:
        prompt: The prompt text to optimize
        level: Optimization level (safe, balanced, aggressive)
    
    Returns:
        Tuple of (optimized_prompt, list_of_applied_rules)
    """
    if not prompt or not prompt.strip():
        return prompt, []
    
    optimized = prompt
    applied_rules = []
    
    # Apply rules based on optimization level
    if level in ["safe", "balanced", "aggressive"]:
        optimized, rules = _apply_safe_rules(optimized)
        applied_rules.extend(rules)
    
    if level in ["balanced", "aggressive"]:
        optimized, rules = _apply_balanced_rules(optimized)
        applied_rules.extend(rules)
    
    if level == "aggressive":
        optimized, rules = _apply_aggressive_rules(optimized)
        applied_rules.extend(rules)
    
    return optimized, applied_rules


def _apply_safe_rules(text: str) -> tuple[str, list[str]]:
    """Apply safe optimization rules that minimally change the prompt."""
    applied = []
    original = text
    
    # Rule: Normalize whitespace
    text = normalize_whitespace(text)
    if text != original:
        applied.append("Normalized whitespace")
        original = text
    
    # Rule: Remove trailing punctuation on last sentence
    text = remove_trailing_punctuation(text)
    if text != original:
        applied.append("Removed trailing punctuation")
        original = text
    
    return text, applied


def _apply_balanced_rules(text: str) -> tuple[str, list[str]]:
    """Apply balanced optimization rules for moderate compression."""
    applied = []
    original = text
    
    # Rule: Remove common filler words
    text = remove_filler_words(text)
    if text != original:
        applied.append("Removed filler words")
        original = text
    
    # Rule: Simplify politeness phrases
    text = simplify_politeness(text)
    if text != original:
        applied.append("Simplified politeness phrases")
        original = text
    
    # Rule: Compress redundant phrases
    text = compress_redundant_phrases(text)
    if text != original:
        applied.append("Compressed redundant phrases")
        original = text
    
    return text, applied


def _apply_aggressive_rules(text: str) -> tuple[str, list[str]]:
    """Apply aggressive optimization rules for maximum compression."""
    applied = []
    original = text
    
    # Rule: Convert to imperative form
    text = convert_to_imperative(text)
    if text != original:
        applied.append("Converted to imperative form")
        original = text
    
    # Rule: Remove articles where safe
    text = remove_articles(text)
    if text != original:
        applied.append("Removed articles")
        original = text
    
    # Rule: Abbreviate common phrases
    text = abbreviate_common_phrases(text)
    if text != original:
        applied.append("Abbreviated common phrases")
        original = text
    
    return text, applied


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in the text.
    - Remove leading/trailing whitespace
    - Collapse multiple spaces to single space
    - Normalize line breaks
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Normalize line breaks (max 2 consecutive)
    text = re.sub(r'\n\n\n+', '\n\n', text)
    
    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    
    return text


def remove_trailing_punctuation(text: str) -> str:
    """Remove unnecessary trailing punctuation."""
    # Remove trailing period if it's the only sentence-ending punctuation
    text = re.sub(r'\.$', '', text.strip())
    return text


def remove_filler_words(text: str) -> str:
    """
    Remove common filler words that don't add meaning.
    Examples: very, really, just, simply, actually, basically, etc.
    """
    filler_words = [
        r'\bvery\s+',
        r'\breally\s+',
        r'\bjust\s+',
        r'\bsimply\s+',
        r'\bactually\s+',
        r'\bbasically\s+',
        r'\bliterally\s+',
        r'\btotally\s+',
        r'\bcompletely\s+',
        r'\babsolutely\s+',
        r'\bentirely\s+',
        r'\bextremely\s+',
    ]
    
    for filler in filler_words:
        text = re.sub(filler, '', text, flags=re.IGNORECASE)
    
    # Clean up any double spaces created
    text = re.sub(r' +', ' ', text)
    
    return text


def simplify_politeness(text: str) -> str:
    """
    Simplify or remove politeness phrases.
    Examples: "Please, if you would be so kind" -> "Please"
    """
    # Remove overly polite prefixes
    text = re.sub(
        r'\b(please,?\s+)?(if you )?(would|could|can) you( possibly| please)?\s+',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Simplify "I would like you to" -> ""
    text = re.sub(
        r'\b(I would like you to|I need you to|I want you to)\s+',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Remove "please" at the start if followed by imperative
    text = re.sub(r'^please,?\s+', '', text, flags=re.IGNORECASE)
    
    return text


def compress_redundant_phrases(text: str) -> str:
    """
    Compress redundant or repetitive phrases.
    Examples: "all of the" -> "all", "in order to" -> "to"
    """
    replacements = {
        r'\ball of the\b': 'all',
        r'\beach and every\b': 'each',
        r'\bin order to\b': 'to',
        r'\bfor the purpose of\b': 'to',
        r'\bdue to the fact that\b': 'because',
        r'\bin the event that\b': 'if',
        r'\bat this point in time\b': 'now',
        r'\bfor the reason that\b': 'because',
        r'\bin spite of the fact that\b': 'although',
        r'\buntil such time as\b': 'until',
        r'\bprior to\b': 'before',
        r'\bsubsequent to\b': 'after',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


def convert_to_imperative(text: str) -> str:
    """
    Convert requests to imperative form.
    Examples: "Can you write" -> "Write", "I need a function" -> "Write a function"
    """
    # "Can you/Could you write" -> "Write"
    text = re.sub(
        r'^(can you|could you|would you|will you)\s+',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # "I need a/an X" -> "Create X" or "Write X"
    text = re.sub(
        r'^I need (a|an)\s+',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    return text


def remove_articles(text: str) -> str:
    """
    Remove articles (a, an, the) where they don't affect meaning.
    Be conservative to avoid breaking grammar.
    """
    # Remove "a" or "an" before common nouns in instructions
    # Only in specific safe patterns
    text = re.sub(r'\b(write|create|make|build|generate)\s+(a|an)\s+', r'\1 ', text, flags=re.IGNORECASE)
    
    return text


def abbreviate_common_phrases(text: str) -> str:
    """
    Abbreviate common programming/technical phrases.
    Only safe, well-known abbreviations.
    """
    abbreviations = {
        r'\bfunction\b': 'fn',
        r'\bdatabase\b': 'DB',
        r'\bapplication\b': 'app',
        r'\bconfiguration\b': 'config',
        r'\benvironment\b': 'env',
    }
    
    # Only apply in aggressive mode and be conservative
    # For now, skip this to avoid being too aggressive
    # Can uncomment if needed
    # for pattern, abbrev in abbreviations.items():
    #     text = re.sub(pattern, abbrev, text, flags=re.IGNORECASE)
    
    return text


def calculate_savings(original: str, optimized: str) -> dict:
    """
    Calculate token savings from optimization.
    
    Returns:
        Dictionary with original_tokens, optimized_tokens, saved_tokens
    """
    original_tokens = count_tokens(original)
    optimized_tokens = count_tokens(optimized)
    saved_tokens = original_tokens - optimized_tokens
    
    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "saved_tokens": saved_tokens
    }

"""Prompt parser for extracting structure from prompts."""

import re
from typing import Optional
from pydantic import BaseModel


class PromptAnalysis(BaseModel):
    """Structured analysis of a prompt."""
    task: Optional[str] = None
    constraints: list[str] = []
    output_format: Optional[str] = None
    context: list[str] = []
    examples: list[str] = []


def parse_prompt(prompt: str) -> PromptAnalysis:
    """
    Parse a prompt to extract its structure using lightweight heuristics.
    
    Detects:
    - task: The main action or goal
    - constraints: Requirements, conditions, or limitations
    - output_format: Expected format of the response
    - context: Background information
    - examples: Sample inputs or outputs
    
    Args:
        prompt: The prompt text to analyze
    
    Returns:
        PromptAnalysis object with extracted structure
    """
    if not prompt or not prompt.strip():
        return PromptAnalysis()
    
    # Initialize analysis
    analysis = PromptAnalysis()
    
    # Extract task (main instruction)
    analysis.task = _extract_task(prompt)
    
    # Extract constraints
    analysis.constraints = _extract_constraints(prompt)
    
    # Extract output format
    analysis.output_format = _extract_output_format(prompt)
    
    # Extract context
    analysis.context = _extract_context(prompt)
    
    # Extract examples
    analysis.examples = _extract_examples(prompt)
    
    return analysis


def _extract_task(prompt: str) -> Optional[str]:
    """
    Extract the main task or instruction from the prompt.
    
    Looks for action verbs and main instructions.
    """
    # Look for imperative verbs at the start
    task_patterns = [
        r'^(write|create|generate|build|make|develop|design|implement|code|produce|draft)\s+(.+?)(?:\.|$)',
        r'^(please\s+)?(write|create|generate|build|make|develop|design|implement|code|produce|draft)\s+(.+?)(?:\.|$)',
        r'^(explain|describe|summarize|analyze|compare|list|show|tell|provide)\s+(.+?)(?:\.|$)',
        r'^(help me|can you|could you|would you)\s+(write|create|generate|build|make)\s+(.+?)(?:\.|$)',
    ]
    
    prompt_lower = prompt.lower()
    
    for pattern in task_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            # Get the full matched instruction
            task_text = match.group(0).strip()
            # Get first sentence or up to newline
            first_sentence = re.split(r'[.\n]', task_text)[0].strip()
            return first_sentence
    
    # Fallback: return first sentence
    sentences = re.split(r'[.\n]', prompt.strip())
    if sentences:
        return sentences[0].strip()
    
    return None


def _extract_constraints(prompt: str) -> list[str]:
    """
    Extract constraints, requirements, or conditions from the prompt.
    
    Looks for phrases like "must", "should", "need to", "make sure", etc.
    """
    constraints = []
    
    # Patterns that indicate constraints
    constraint_indicators = [
        r'must\s+([^.]+)',
        r'should\s+([^.]+)',
        r'need(?:s)?\s+to\s+([^.]+)',
        r'make sure\s+(?:to\s+)?([^.]+)',
        r'ensure\s+(?:that\s+)?([^.]+)',
        r'require(?:s|d)?\s+([^.]+)',
        r'(?:only|just)\s+([^.]+)',
        r'don\'t\s+([^.]+)',
        r'do not\s+([^.]+)',
        r'without\s+([^.]+)',
    ]
    
    for pattern in constraint_indicators:
        matches = re.finditer(pattern, prompt, re.IGNORECASE)
        for match in matches:
            constraint = match.group(0).strip()
            if len(constraint) > 10 and len(constraint) < 200:  # Reasonable length
                constraints.append(constraint)
    
    # Look for bullet points or numbered lists
    list_items = re.findall(r'(?:^|\n)\s*[-•*]\s*(.+?)(?:\n|$)', prompt)
    constraints.extend([item.strip() for item in list_items if len(item.strip()) > 5])
    
    return constraints[:5]  # Limit to top 5


def _extract_output_format(prompt: str) -> Optional[str]:
    """
    Extract the expected output format from the prompt.
    
    Looks for mentions of format, structure, or output type.
    """
    format_patterns = [
        r'(?:in|as|using)\s+(JSON|XML|YAML|CSV|HTML|Markdown|SQL|Python|JavaScript|code)',
        r'format\s*:\s*(\w+)',
        r'output\s+(?:should be|as|in)\s+(\w+)',
        r'return\s+(?:a|an)?\s*(\w+)',
        r'(?:JSON|XML|YAML|CSV|HTML|Markdown|SQL)\s+(?:format|structure|output)',
        r'(SQL)\s+(?:query|statement|command)',
        r'(Python|JavaScript|Java|C\+\+|Ruby|Go)\s+(?:code|function|script|program)',
        r'write\s+(?:a|an)?\s*(SQL|Python|JavaScript|Java)\s+',
        r'generate\s+(?:a|an)?\s*(SQL|Python|JavaScript|Java|code)\s+',
    ]
    
    for pattern in format_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return None


def _extract_context(prompt: str) -> list[str]:
    """
    Extract contextual information from the prompt.
    
    Looks for background info, given information, or setup details.
    """
    context = []
    
    # Patterns that indicate context
    context_patterns = [
        r'(?:given|assume|suppose|consider)\s+(?:that\s+)?(.{20,150}?)(?:\.|$)',
        r'background\s*:\s*(.+?)(?:\n\n|$)',
        r'context\s*:\s*(.+?)(?:\n\n|$)',
        r'we have\s+(.+?)(?:\.|$)',
        r'there (?:is|are)\s+(.+?)(?:\.|$)',
    ]
    
    for pattern in context_patterns:
        matches = re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL)
        for match in matches:
            ctx = match.group(1).strip()
            if len(ctx) > 15 and len(ctx) < 300:
                context.append(ctx)
    
    return context[:3]  # Limit to top 3


def _extract_examples(prompt: str) -> list[str]:
    """
    Extract examples from the prompt.
    
    Looks for example indicators and sample data.
    """
    examples = []
    
    # Look for explicit example markers
    example_patterns = [
        r'example\s*:\s*(.+?)(?:\n\n|$)',
        r'for example\s*,?\s*(.+?)(?:\n\n|$)',
        r'e\.g\.\s*,?\s*(.+?)(?:\n\n|$)',
        r'such as\s+(.+?)(?:\.|$)',
    ]
    
    for pattern in example_patterns:
        matches = re.finditer(pattern, prompt, re.IGNORECASE | re.DOTALL)
        for match in matches:
            example = match.group(1).strip()
            if len(example) > 5 and len(example) < 500:
                examples.append(example)
    
    # Look for code blocks (common for examples)
    code_blocks = re.findall(r'```[\s\S]*?```|`[^`]+`', prompt)
    examples.extend(code_blocks[:2])  # Limit code block examples
    
    return examples[:3]  # Limit to top 3


def get_prompt_summary(prompt: str) -> dict:
    """
    Get a dictionary summary of the prompt analysis.
    
    Args:
        prompt: The prompt text to analyze
    
    Returns:
        Dictionary with analysis results
    """
    analysis = parse_prompt(prompt)
    return analysis.model_dump(exclude_none=True)

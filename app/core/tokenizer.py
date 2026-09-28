"""Token counting utilities using tiktoken."""

import tiktoken
from typing import Optional


# Default encoding for GPT-4 and GPT-3.5-turbo
DEFAULT_ENCODING = "cl100k_base"


def count_tokens(text: str, encoding_name: str = DEFAULT_ENCODING) -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to tokenize and count
        encoding_name: The name of the encoding to use (default: cl100k_base for GPT-4/3.5)
    
    Returns:
        The number of tokens in the text
    
    Examples:
        >>> count_tokens("Hello, world!")
        4
        >>> count_tokens("")
        0
    """
    if not text:
        return 0
    
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        raise ValueError(f"Error counting tokens: {str(e)}")


def count_tokens_for_model(text: str, model_name: str = "gpt-4") -> int:
    """
    Count tokens using a specific model's encoding.
    
    Args:
        text: The text to tokenize and count
        model_name: The model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
    
    Returns:
        The number of tokens in the text
    """
    if not text:
        return 0
    
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        raise ValueError(f"Error counting tokens for model {model_name}: {str(e)}")


def get_available_encodings() -> list[str]:
    """
    Get a list of available encoding names.
    
    Returns:
        List of encoding names
    """
    return list(tiktoken.list_encoding_names())

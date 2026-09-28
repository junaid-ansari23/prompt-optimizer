"""Tests for the token counting utility."""

import pytest
from app.core.tokenizer import (
    count_tokens,
    count_tokens_for_model,
    get_available_encodings,
    DEFAULT_ENCODING
)


def test_count_tokens_simple_text():
    """Test token counting with simple text."""
    text = "Hello, world!"
    token_count = count_tokens(text)
    
    # "Hello, world!" should be around 4 tokens with cl100k_base
    assert isinstance(token_count, int)
    assert token_count > 0
    assert token_count == 4


def test_count_tokens_empty_string():
    """Test that empty string returns 0 tokens."""
    assert count_tokens("") == 0
    assert count_tokens("   ") > 0  # whitespace should still count


def test_count_tokens_long_text():
    """Test token counting with longer text."""
    text = """
    This is a longer piece of text that contains multiple sentences.
    It should have a reasonable token count based on the number of words
    and punctuation marks present in the content.
    """
    token_count = count_tokens(text)
    
    assert isinstance(token_count, int)
    assert token_count > 20  # Should have at least 20 tokens


def test_count_tokens_special_characters():
    """Test token counting with special characters."""
    text = "Hello! @#$% 123 👍"
    token_count = count_tokens(text)
    
    assert isinstance(token_count, int)
    assert token_count > 0


def test_count_tokens_code_snippet():
    """Test token counting with code."""
    code = "def hello():\n    print('Hello, world!')\n    return True"
    token_count = count_tokens(code)
    
    assert isinstance(token_count, int)
    assert token_count > 5


def test_count_tokens_different_encodings():
    """Test that different encodings can be specified."""
    text = "Hello, world!"
    
    # Test with default encoding
    count_default = count_tokens(text)
    
    # Test with explicit encoding
    count_explicit = count_tokens(text, encoding_name=DEFAULT_ENCODING)
    
    assert count_default == count_explicit


def test_count_tokens_for_model():
    """Test token counting for specific models."""
    text = "Hello, world!"
    
    # Test with GPT-4
    count_gpt4 = count_tokens_for_model(text, model_name="gpt-4")
    assert isinstance(count_gpt4, int)
    assert count_gpt4 > 0
    
    # Test with GPT-3.5
    count_gpt35 = count_tokens_for_model(text, model_name="gpt-3.5-turbo")
    assert isinstance(count_gpt35, int)
    assert count_gpt35 > 0


def test_count_tokens_for_model_empty():
    """Test that empty string returns 0 for model-specific counting."""
    assert count_tokens_for_model("") == 0


def test_get_available_encodings():
    """Test that available encodings can be retrieved."""
    encodings = get_available_encodings()
    
    assert isinstance(encodings, list)
    assert len(encodings) > 0
    assert DEFAULT_ENCODING in encodings


def test_count_tokens_consistency():
    """Test that the same text always returns the same token count."""
    text = "Consistency is key in token counting!"
    
    count1 = count_tokens(text)
    count2 = count_tokens(text)
    count3 = count_tokens(text)
    
    assert count1 == count2 == count3


def test_count_tokens_multiline():
    """Test token counting with multiline text."""
    text = """Line 1
Line 2
Line 3"""
    
    token_count = count_tokens(text)
    assert isinstance(token_count, int)
    assert token_count > 3


def test_longer_prompt_example():
    """Test with a realistic prompt example."""
    prompt = """
    Please write a SQL query that selects all users from the database
    where the user's account was created in the last 30 days and 
    their subscription status is 'active'. Include their email, username,
    and creation date in the results, ordered by creation date descending.
    """
    
    token_count = count_tokens(prompt)
    assert isinstance(token_count, int)
    assert token_count > 40  # Should be a substantial number

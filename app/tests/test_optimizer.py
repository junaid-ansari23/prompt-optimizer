"""Tests for the prompt optimizer."""

import pytest
from app.core.optimizer import (
    optimize_prompt,
    normalize_whitespace,
    remove_trailing_punctuation,
    remove_filler_words,
    simplify_politeness,
    compress_redundant_phrases,
    convert_to_imperative,
    remove_articles,
    calculate_savings
)


class TestOptimizePrompt:
    """Tests for main optimize_prompt function."""
    
    def test_optimize_empty_prompt(self):
        """Test optimizing empty prompt."""
        result, rules = optimize_prompt("")
        assert result == ""
        assert rules == []
    
    def test_optimize_safe_level(self):
        """Test safe optimization level."""
        prompt = "  Write a function.  "
        result, rules = optimize_prompt(prompt, level="safe")
        
        assert result == "Write a function"
        assert len(rules) > 0
    
    def test_optimize_balanced_level(self):
        """Test balanced optimization level."""
        prompt = "Please, could you very kindly write a function."
        result, rules = optimize_prompt(prompt, level="balanced")
        
        # Should have more aggressive optimization
        assert len(result) < len(prompt)
        assert len(rules) > 0
    
    def test_optimize_aggressive_level(self):
        """Test aggressive optimization level."""
        prompt = "Can you please write a very simple function."
        result, rules = optimize_prompt(prompt, level="aggressive")
        
        # Should have most aggressive optimization
        assert len(result) < len(prompt)
        assert len(rules) > 0
    
    def test_returns_applied_rules(self):
        """Test that applied rules are returned."""
        prompt = "Please  write  a  function  ."
        result, rules = optimize_prompt(prompt, level="safe")
        
        assert isinstance(rules, list)
        assert all(isinstance(rule, str) for rule in rules)


class TestNormalizeWhitespace:
    """Tests for whitespace normalization."""
    
    def test_trim_leading_trailing(self):
        """Test trimming leading and trailing whitespace."""
        text = "  Hello world  "
        result = normalize_whitespace(text)
        assert result == "Hello world"
    
    def test_collapse_multiple_spaces(self):
        """Test collapsing multiple spaces."""
        text = "Hello    world"
        result = normalize_whitespace(text)
        assert result == "Hello world"
    
    def test_normalize_line_breaks(self):
        """Test normalizing excessive line breaks."""
        text = "Line 1\n\n\n\nLine 2"
        result = normalize_whitespace(text)
        assert result == "Line 1\n\nLine 2"
    
    def test_remove_space_before_punctuation(self):
        """Test removing spaces before punctuation."""
        text = "Hello , world ."
        result = normalize_whitespace(text)
        assert result == "Hello, world."


class TestRemoveTrailingPunctuation:
    """Tests for removing trailing punctuation."""
    
    def test_remove_trailing_period(self):
        """Test removing trailing period."""
        text = "Write a function."
        result = remove_trailing_punctuation(text)
        assert result == "Write a function"
    
    def test_preserve_without_period(self):
        """Test preserving text without period."""
        text = "Write a function"
        result = remove_trailing_punctuation(text)
        assert result == "Write a function"


class TestRemoveFillerWords:
    """Tests for removing filler words."""
    
    def test_remove_very(self):
        """Test removing 'very'."""
        text = "Write a very simple function"
        result = remove_filler_words(text)
        assert "very" not in result.lower()
    
    def test_remove_really(self):
        """Test removing 'really'."""
        text = "This is really important"
        result = remove_filler_words(text)
        assert "really" not in result.lower()
    
    def test_remove_just(self):
        """Test removing 'just'."""
        text = "Just write a function"
        result = remove_filler_words(text)
        assert "just" not in result.lower()
    
    def test_remove_multiple_fillers(self):
        """Test removing multiple filler words."""
        text = "Please very simply just write a really basic function"
        result = remove_filler_words(text)
        assert "very" not in result.lower()
        assert "simply" not in result.lower()
        assert "really" not in result.lower()
    
    def test_preserve_meaning(self):
        """Test that core meaning is preserved."""
        text = "Write a function"
        result = remove_filler_words(text)
        assert "write" in result.lower()
        assert "function" in result.lower()


class TestSimplifyPoliteness:
    """Tests for simplifying politeness phrases."""
    
    def test_remove_could_you(self):
        """Test removing 'could you'."""
        text = "Could you write a function"
        result = simplify_politeness(text)
        assert "could you" not in result.lower()
    
    def test_remove_would_you(self):
        """Test removing 'would you'."""
        text = "Would you please write a function"
        result = simplify_politeness(text)
        assert "would you" not in result.lower()
    
    def test_remove_i_would_like(self):
        """Test removing 'I would like you to'."""
        text = "I would like you to write a function"
        result = simplify_politeness(text)
        assert "i would like" not in result.lower()
    
    def test_remove_please_prefix(self):
        """Test removing 'please' at start."""
        text = "Please write a function"
        result = simplify_politeness(text)
        # "please" should be removed
        assert result == "write a function" or "please" not in result.lower()


class TestCompressRedundantPhrases:
    """Tests for compressing redundant phrases."""
    
    def test_all_of_the(self):
        """Test compressing 'all of the' to 'all'."""
        text = "Select all of the users"
        result = compress_redundant_phrases(text)
        assert "all of the" not in result.lower()
        assert "all" in result.lower()
    
    def test_in_order_to(self):
        """Test compressing 'in order to' to 'to'."""
        text = "In order to select users"
        result = compress_redundant_phrases(text)
        assert "in order to" not in result.lower()
    
    def test_due_to_fact(self):
        """Test compressing 'due to the fact that' to 'because'."""
        text = "Due to the fact that users exist"
        result = compress_redundant_phrases(text)
        assert "due to the fact" not in result.lower()
        assert "because" in result.lower()
    
    def test_multiple_redundancies(self):
        """Test handling multiple redundant phrases."""
        text = "In order to select all of the users"
        result = compress_redundant_phrases(text)
        assert len(result) < len(text)


class TestConvertToImperative:
    """Tests for converting to imperative form."""
    
    def test_can_you_to_imperative(self):
        """Test converting 'Can you' to imperative."""
        text = "Can you write a function"
        result = convert_to_imperative(text)
        assert "can you" not in result.lower()
    
    def test_could_you_to_imperative(self):
        """Test converting 'Could you' to imperative."""
        text = "Could you create a script"
        result = convert_to_imperative(text)
        assert "could you" not in result.lower()
    
    def test_i_need_to_imperative(self):
        """Test converting 'I need' to imperative."""
        text = "I need a function"
        result = convert_to_imperative(text)
        assert "i need" not in result.lower()


class TestRemoveArticles:
    """Tests for removing articles."""
    
    def test_remove_article_after_write(self):
        """Test removing article after 'write'."""
        text = "Write a function"
        result = remove_articles(text)
        # Should handle article removal carefully
        assert "write" in result.lower()
        assert "function" in result.lower()
    
    def test_conservative_removal(self):
        """Test that article removal is conservative."""
        text = "Write a function to parse a file"
        result = remove_articles(text)
        # Should preserve core meaning
        assert "function" in result.lower()
        assert "parse" in result.lower()


class TestCalculateSavings:
    """Tests for calculating token savings."""
    
    def test_calculate_with_savings(self):
        """Test calculating savings when tokens are saved."""
        original = "Please write a very detailed function"
        optimized = "Write detailed function"
        
        result = calculate_savings(original, optimized)
        
        assert "original_tokens" in result
        assert "optimized_tokens" in result
        assert "saved_tokens" in result
        assert result["original_tokens"] > result["optimized_tokens"]
        assert result["saved_tokens"] > 0
    
    def test_calculate_no_change(self):
        """Test calculating when no tokens are saved."""
        text = "Write function"
        result = calculate_savings(text, text)
        
        assert result["saved_tokens"] == 0
        assert result["original_tokens"] == result["optimized_tokens"]
    
    def test_calculate_structure(self):
        """Test that result has correct structure."""
        result = calculate_savings("Hello world", "Hello")
        
        assert isinstance(result["original_tokens"], int)
        assert isinstance(result["optimized_tokens"], int)
        assert isinstance(result["saved_tokens"], int)


class TestIntegration:
    """Integration tests for complete optimization."""
    
    def test_verbose_sql_prompt(self):
        """Test optimizing a verbose SQL prompt."""
        prompt = """
        Please, if you would be so kind, could you possibly write a very detailed 
        and comprehensive SQL query that will select all of the users from our database.
        """
        
        result, rules = optimize_prompt(prompt.strip(), level="balanced")
        
        assert len(result) < len(prompt)
        assert "sql" in result.lower()
        assert "query" in result.lower()
        assert "users" in result.lower()
    
    def test_polite_coding_prompt(self):
        """Test optimizing a polite coding prompt."""
        prompt = "Could you please just write a very simple function to add two numbers."
        
        result, rules = optimize_prompt(prompt, level="aggressive")
        
        assert len(result) < len(prompt)
        assert "function" in result.lower() or "fn" in result.lower()
        assert "add" in result.lower()
    
    def test_redundant_prompt(self):
        """Test optimizing a prompt with redundant phrases."""
        prompt = "In order to select all of the records, write a query."
        
        result, rules = optimize_prompt(prompt, level="balanced")
        
        assert len(result) < len(prompt)
        assert "select" in result.lower()
        assert "records" in result.lower()
    
    def test_preserves_key_constraints(self):
        """Test that key constraints are preserved."""
        prompt = "Write a function that must handle errors and should be efficient."
        
        result, rules = optimize_prompt(prompt, level="balanced")
        
        # Key words should be preserved
        assert "function" in result.lower()
        assert "must" in result.lower() or "handle" in result.lower()
        assert "errors" in result.lower()

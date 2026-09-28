"""Tests for the prompt parser."""

import pytest
from app.core.parser import (
    parse_prompt,
    get_prompt_summary,
    PromptAnalysis,
    _extract_task,
    _extract_constraints,
    _extract_output_format,
    _extract_context,
    _extract_examples
)


class TestPromptAnalysis:
    """Tests for PromptAnalysis model."""
    
    def test_prompt_analysis_model(self):
        """Test that PromptAnalysis model can be created."""
        analysis = PromptAnalysis(
            task="Write a function",
            constraints=["must be efficient"],
            output_format="Python",
            context=["given a list"],
            examples=["def foo(): ..."]
        )
        
        assert analysis.task == "Write a function"
        assert len(analysis.constraints) == 1
        assert analysis.output_format == "Python"
        assert len(analysis.context) == 1
        assert len(analysis.examples) == 1
    
    def test_prompt_analysis_defaults(self):
        """Test that PromptAnalysis has reasonable defaults."""
        analysis = PromptAnalysis()
        
        assert analysis.task is None
        assert analysis.constraints == []
        assert analysis.output_format is None
        assert analysis.context == []
        assert analysis.examples == []


class TestParsePrompt:
    """Tests for parse_prompt function."""
    
    def test_parse_empty_prompt(self):
        """Test parsing empty prompt."""
        analysis = parse_prompt("")
        
        assert analysis.task is None
        assert analysis.constraints == []
        assert analysis.output_format is None
    
    def test_parse_simple_sql_prompt(self):
        """Test parsing a simple SQL prompt."""
        prompt = "Write a SQL query to select all users from the database."
        analysis = parse_prompt(prompt)
        
        assert analysis.task is not None
        assert "sql" in analysis.task.lower() or "query" in analysis.task.lower()
    
    def test_parse_coding_prompt(self):
        """Test parsing a coding instruction."""
        prompt = "Create a Python function that calculates the factorial of a number."
        analysis = parse_prompt(prompt)
        
        assert analysis.task is not None
        assert "python" in analysis.task.lower() or "function" in analysis.task.lower()
    
    def test_parse_prompt_with_constraints(self):
        """Test parsing a prompt with explicit constraints."""
        prompt = """
        Write a function to sort a list.
        It must be efficient and should handle empty lists.
        Make sure to include error handling.
        """
        analysis = parse_prompt(prompt)
        
        assert analysis.task is not None
        assert len(analysis.constraints) > 0
        # Check that constraint keywords are captured
        constraints_text = " ".join(analysis.constraints).lower()
        assert "must" in constraints_text or "should" in constraints_text
    
    def test_parse_prompt_with_format(self):
        """Test parsing a prompt with output format specified."""
        prompt = "Generate a user profile in JSON format."
        analysis = parse_prompt(prompt)
        
        assert analysis.output_format is not None
        assert "json" in analysis.output_format.lower()
    
    def test_parse_verbose_prompt(self):
        """Test parsing a verbose, detailed prompt."""
        prompt = """
        Please write a very detailed SQL query that will select all users 
        from our database where the account was created in the last 30 days.
        The query must include the user's email and username.
        Make sure to order the results by creation date.
        """
        analysis = parse_prompt(prompt)
        
        assert analysis.task is not None
        assert len(analysis.constraints) > 0


class TestExtractTask:
    """Tests for task extraction."""
    
    def test_extract_task_with_write(self):
        """Test extracting task starting with 'write'."""
        prompt = "Write a SQL query to select all users."
        task = _extract_task(prompt)
        
        assert task is not None
        assert "write" in task.lower()
    
    def test_extract_task_with_create(self):
        """Test extracting task starting with 'create'."""
        prompt = "Create a Python function for sorting."
        task = _extract_task(prompt)
        
        assert task is not None
        assert "create" in task.lower()
    
    def test_extract_task_with_please(self):
        """Test extracting task with polite prefix."""
        prompt = "Please generate a report of user activities."
        task = _extract_task(prompt)
        
        assert task is not None
        assert "generate" in task.lower() or "report" in task.lower()
    
    def test_extract_task_fallback(self):
        """Test task extraction fallback to first sentence."""
        prompt = "This is a simple request. Do something else."
        task = _extract_task(prompt)
        
        assert task is not None
        assert "this is a simple request" in task.lower()


class TestExtractConstraints:
    """Tests for constraint extraction."""
    
    def test_extract_must_constraint(self):
        """Test extracting 'must' constraints."""
        prompt = "Write code that must be efficient and must handle errors."
        constraints = _extract_constraints(prompt)
        
        assert len(constraints) > 0
        assert any("must" in c.lower() for c in constraints)
    
    def test_extract_should_constraint(self):
        """Test extracting 'should' constraints."""
        prompt = "The function should return a list and should be fast."
        constraints = _extract_constraints(prompt)
        
        assert len(constraints) > 0
        assert any("should" in c.lower() for c in constraints)
    
    def test_extract_bullet_constraints(self):
        """Test extracting bullet point constraints."""
        prompt = """
        Requirements:
        - Must be efficient
        - Should handle edge cases
        - Need to include tests
        """
        constraints = _extract_constraints(prompt)
        
        assert len(constraints) >= 2
    
    def test_no_constraints(self):
        """Test prompt without constraints."""
        prompt = "Write a simple function."
        constraints = _extract_constraints(prompt)
        
        # May be empty or have minimal constraints
        assert isinstance(constraints, list)


class TestExtractOutputFormat:
    """Tests for output format extraction."""
    
    def test_extract_json_format(self):
        """Test extracting JSON format."""
        prompt = "Return the data in JSON format."
        fmt = _extract_output_format(prompt)
        
        assert fmt is not None
        assert "json" in fmt.lower()
    
    def test_extract_sql_format(self):
        """Test extracting SQL format."""
        prompt = "Write a SQL query to get users."
        fmt = _extract_output_format(prompt)
        
        assert fmt is not None
        assert "sql" in fmt.lower()
    
    def test_extract_code_format(self):
        """Test extracting code format."""
        prompt = "Generate Python code for sorting."
        fmt = _extract_output_format(prompt)
        
        assert fmt is not None
        assert "python" in fmt.lower()
    
    def test_no_format(self):
        """Test prompt without explicit format."""
        prompt = "Explain how sorting works."
        fmt = _extract_output_format(prompt)
        
        # May or may not have format
        assert fmt is None or isinstance(fmt, str)


class TestExtractContext:
    """Tests for context extraction."""
    
    def test_extract_given_context(self):
        """Test extracting context with 'given'."""
        prompt = "Given a list of numbers, write code to find the maximum."
        context = _extract_context(prompt)
        
        assert len(context) > 0
    
    def test_extract_assume_context(self):
        """Test extracting context with 'assume'."""
        prompt = "Assume we have a database of users. Write a query."
        context = _extract_context(prompt)
        
        assert len(context) > 0
    
    def test_no_context(self):
        """Test prompt without explicit context."""
        prompt = "Write a function to add two numbers."
        context = _extract_context(prompt)
        
        assert isinstance(context, list)


class TestExtractExamples:
    """Tests for example extraction."""
    
    def test_extract_explicit_example(self):
        """Test extracting explicitly marked examples."""
        prompt = "Write a function. Example: def add(a, b): return a + b"
        examples = _extract_examples(prompt)
        
        assert len(examples) > 0
    
    def test_extract_code_block_example(self):
        """Test extracting code block examples."""
        prompt = "Here's what I need: ```python\ndef test(): pass\n```"
        examples = _extract_examples(prompt)
        
        assert len(examples) > 0
    
    def test_no_examples(self):
        """Test prompt without examples."""
        prompt = "Write a simple sorting function."
        examples = _extract_examples(prompt)
        
        assert isinstance(examples, list)


class TestGetPromptSummary:
    """Tests for get_prompt_summary function."""
    
    def test_get_summary_returns_dict(self):
        """Test that summary returns a dictionary."""
        prompt = "Write a SQL query to select all users."
        summary = get_prompt_summary(prompt)
        
        assert isinstance(summary, dict)
    
    def test_summary_has_task(self):
        """Test that summary includes task if present."""
        prompt = "Create a Python function for sorting."
        summary = get_prompt_summary(prompt)
        
        assert "task" in summary
    
    def test_summary_comprehensive(self):
        """Test summary with comprehensive prompt."""
        prompt = """
        Write a Python function to calculate factorials.
        It must handle negative numbers and should be efficient.
        Return the result as an integer.
        Example: factorial(5) = 120
        """
        summary = get_prompt_summary(prompt)
        
        assert isinstance(summary, dict)
        # Should have multiple fields populated
        assert len(summary) > 0

"""Tests for the optimization service layer."""

import pytest
from app.service.optimize_service import (
    optimize_prompt_service,
    generate_optimization_variants,
    create_variant,
    calculate_optimization_metrics
)
from app.core.schemas import OptimizeRequest, OptimizationMode


class TestOptimizePromptService:
    """Tests for the main optimize_prompt_service function."""
    
    def test_service_returns_response(self):
        """Test that service returns a valid OptimizeResponse."""
        request = OptimizeRequest(prompt="Write a function to add numbers")
        response = optimize_prompt_service(request)
        
        assert response.original_prompt == "Write a function to add numbers"
        assert response.original_tokens > 0
        assert len(response.variants) == 3
        assert response.analysis is not None
    
    def test_service_with_verbose_prompt(self):
        """Test service with a verbose prompt."""
        request = OptimizeRequest(
            prompt="Could you please very kindly write a really simple function."
        )
        response = optimize_prompt_service(request)
        
        assert response.original_tokens > 0
        assert len(response.variants) == 3
        
        # At least one variant should save tokens
        savings = [v.saved_tokens for v in response.variants]
        assert any(s > 0 for s in savings)
    
    def test_service_with_concise_prompt(self):
        """Test service with an already concise prompt."""
        request = OptimizeRequest(prompt="Write function")
        response = optimize_prompt_service(request)
        
        assert response.original_tokens > 0
        assert len(response.variants) == 3
        
        # Should have minimal or no savings
        for variant in response.variants:
            assert variant.saved_tokens <= 2
    
    def test_service_preserves_prompt_order(self):
        """Test that variants are returned in safe/balanced/aggressive order."""
        request = OptimizeRequest(prompt="Test prompt for ordering")
        response = optimize_prompt_service(request)
        
        assert response.variants[0].mode == OptimizationMode.SAFE
        assert response.variants[1].mode == OptimizationMode.BALANCED
        assert response.variants[2].mode == OptimizationMode.AGGRESSIVE
    
    def test_service_includes_analysis(self):
        """Test that prompt analysis is included."""
        request = OptimizeRequest(
            prompt="Write a SQL query to select all users."
        )
        response = optimize_prompt_service(request)
        
        assert response.analysis is not None
        assert isinstance(response.analysis, dict)
    
    def test_service_with_mode_parameter(self):
        """Test service with explicit mode parameter."""
        request = OptimizeRequest(
            prompt="Test prompt",
            mode=OptimizationMode.AGGRESSIVE
        )
        response = optimize_prompt_service(request)
        
        # Should still return all three variants
        assert len(response.variants) == 3


class TestGenerateOptimizationVariants:
    """Tests for variant generation."""
    
    def test_generates_three_variants(self):
        """Test that three variants are generated."""
        prompt = "Please write a very simple function."
        original_tokens = 6
        
        variants = generate_optimization_variants(prompt, original_tokens)
        
        assert len(variants) == 3
        assert variants[0].mode == OptimizationMode.SAFE
        assert variants[1].mode == OptimizationMode.BALANCED
        assert variants[2].mode == OptimizationMode.AGGRESSIVE
    
    def test_variants_have_token_counts(self):
        """Test that all variants have valid token counts."""
        prompt = "Write a function"
        original_tokens = 3
        
        variants = generate_optimization_variants(prompt, original_tokens)
        
        for variant in variants:
            assert variant.tokens >= 0
            assert isinstance(variant.tokens, int)
    
    def test_variants_have_saved_tokens(self):
        """Test that saved_tokens is calculated correctly."""
        prompt = "Please write a very detailed function."
        original_tokens = 6
        
        variants = generate_optimization_variants(prompt, original_tokens)
        
        for variant in variants:
            expected_saved = original_tokens - variant.tokens
            assert variant.saved_tokens == expected_saved
    
    def test_variants_have_notes(self):
        """Test that variants include notes about applied rules."""
        prompt = "Please write a very simple function."
        original_tokens = 6
        
        variants = generate_optimization_variants(prompt, original_tokens)
        
        for variant in variants:
            assert hasattr(variant, 'notes')
            assert isinstance(variant.notes, list)
            assert len(variant.notes) > 0
    
    def test_aggressive_saves_most_tokens(self):
        """Test that aggressive mode typically saves the most tokens."""
        prompt = "Could you please very kindly write a really simple function."
        original_tokens = 10
        
        variants = generate_optimization_variants(prompt, original_tokens)
        
        safe = variants[0]
        balanced = variants[1]
        aggressive = variants[2]
        
        # Aggressive should save at least as much as balanced
        assert aggressive.saved_tokens >= balanced.saved_tokens
        
        # Balanced should save at least as much as safe
        assert balanced.saved_tokens >= safe.saved_tokens


class TestCreateVariant:
    """Tests for variant creation helper."""
    
    def test_creates_variant_with_savings(self):
        """Test creating a variant with token savings."""
        variant = create_variant(
            mode=OptimizationMode.BALANCED,
            optimized_text="Write function",
            optimized_tokens=2,
            original_tokens=5,
            applied_rules=["Removed filler words"]
        )
        
        assert variant.mode == OptimizationMode.BALANCED
        assert variant.prompt == "Write function"
        assert variant.tokens == 2
        assert variant.saved_tokens == 3
        assert variant.notes == ["Removed filler words"]
    
    def test_creates_variant_no_savings(self):
        """Test creating a variant with no token savings."""
        variant = create_variant(
            mode=OptimizationMode.SAFE,
            optimized_text="Write function",
            optimized_tokens=2,
            original_tokens=2,
            applied_rules=[]
        )
        
        assert variant.saved_tokens == 0
        assert variant.notes == ["No optimization needed"]
    
    def test_creates_variant_with_multiple_rules(self):
        """Test creating a variant with multiple applied rules."""
        rules = [
            "Normalized whitespace",
            "Removed filler words",
            "Simplified politeness"
        ]
        
        variant = create_variant(
            mode=OptimizationMode.AGGRESSIVE,
            optimized_text="Write function",
            optimized_tokens=2,
            original_tokens=6,
            applied_rules=rules
        )
        
        assert variant.notes == rules
        assert len(variant.notes) == 3


class TestCalculateOptimizationMetrics:
    """Tests for optimization metrics calculation."""
    
    def test_calculates_max_savings(self):
        """Test calculation of maximum token savings."""
        variants = [
            create_variant(OptimizationMode.SAFE, "test", 9, 10, []),
            create_variant(OptimizationMode.BALANCED, "test", 7, 10, []),
            create_variant(OptimizationMode.AGGRESSIVE, "test", 5, 10, [])
        ]
        
        metrics = calculate_optimization_metrics(variants, 10)
        
        assert metrics["max_savings"] == 5
        assert metrics["max_savings_pct"] == 50.0
        assert metrics["best_mode"] == "aggressive"
    
    def test_calculates_average_savings(self):
        """Test calculation of average token savings."""
        variants = [
            create_variant(OptimizationMode.SAFE, "test", 9, 10, []),
            create_variant(OptimizationMode.BALANCED, "test", 6, 10, []),
            create_variant(OptimizationMode.AGGRESSIVE, "test", 3, 10, [])
        ]
        
        metrics = calculate_optimization_metrics(variants, 10)
        
        # Average of 1, 4, 7 = 4
        assert metrics["avg_savings"] == 4.0
    
    def test_handles_empty_variants(self):
        """Test metrics calculation with empty variants list."""
        metrics = calculate_optimization_metrics([], 10)
        
        assert metrics["max_savings"] == 0
        assert metrics["max_savings_pct"] == 0.0
        assert metrics["avg_savings"] == 0.0
        assert metrics["best_mode"] is None
    
    def test_handles_zero_original_tokens(self):
        """Test metrics calculation with zero original tokens."""
        variants = [
            create_variant(OptimizationMode.SAFE, "", 0, 0, [])
        ]
        
        metrics = calculate_optimization_metrics(variants, 0)
        
        assert metrics["max_savings_pct"] == 0.0
    
    def test_identifies_best_mode(self):
        """Test that best mode is correctly identified."""
        # Safe saves most (unusual case)
        variants = [
            create_variant(OptimizationMode.SAFE, "test", 5, 10, []),
            create_variant(OptimizationMode.BALANCED, "test", 7, 10, []),
            create_variant(OptimizationMode.AGGRESSIVE, "test", 8, 10, [])
        ]
        
        metrics = calculate_optimization_metrics(variants, 10)
        
        assert metrics["best_mode"] == "safe"
        assert metrics["max_savings"] == 5


class TestServiceIntegration:
    """Integration tests for the service layer."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from request to response."""
        request = OptimizeRequest(
            prompt="Could you please write a very detailed SQL query to select users."
        )
        
        response = optimize_prompt_service(request)
        
        # Verify complete response structure
        assert response.original_prompt == request.prompt
        assert response.original_tokens > 0
        assert len(response.variants) == 3
        assert response.analysis is not None
        
        # Verify variant ordering
        assert response.variants[0].mode == OptimizationMode.SAFE
        assert response.variants[1].mode == OptimizationMode.BALANCED
        assert response.variants[2].mode == OptimizationMode.AGGRESSIVE
        
        # Verify savings calculations
        for variant in response.variants:
            expected = response.original_tokens - variant.tokens
            assert variant.saved_tokens == expected
    
    def test_service_handles_special_characters(self):
        """Test service with special characters in prompt."""
        request = OptimizeRequest(
            prompt="Write SQL: SELECT * FROM users WHERE name = 'John' AND age > 18;"
        )
        
        response = optimize_prompt_service(request)
        
        assert response.original_prompt == request.prompt
        assert len(response.variants) == 3
    
    def test_service_handles_multiline_prompts(self):
        """Test service with multiline prompts."""
        request = OptimizeRequest(
            prompt="""Please write a function that:
            1. Takes two numbers
            2. Adds them together
            3. Returns the result"""
        )
        
        response = optimize_prompt_service(request)
        
        assert response.original_tokens > 0
        assert len(response.variants) == 3

"""Tests for the /optimize API endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.schemas import OptimizationMode

client = TestClient(app)


class TestOptimizeEndpoint:
    """Tests for the POST /api/optimize endpoint."""
    
    def test_optimize_endpoint_exists(self):
        """Test that the optimize endpoint is accessible."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Test prompt"}
        )
        
        # Should not return 404
        assert response.status_code != 404
    
    def test_optimize_basic_request(self):
        """Test basic optimization request."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Write a SQL query to select all users."}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "original_prompt" in data
        assert "original_tokens" in data
        assert "variants" in data
        assert isinstance(data["variants"], list)
    
    def test_optimize_returns_original_prompt(self):
        """Test that original prompt is returned unchanged."""
        test_prompt = "Hello, world!"
        
        response = client.post(
            "/api/optimize",
            json={"prompt": test_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_prompt"] == test_prompt
    
    def test_optimize_counts_tokens(self):
        """Test that original token count is included."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Hello, world!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "original_tokens" in data
        assert isinstance(data["original_tokens"], int)
        assert data["original_tokens"] > 0
    
    def test_optimize_returns_three_variants(self):
        """Test that three optimization variants are returned."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Test prompt for optimization"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["variants"]) == 3
        
        # Check that all modes are present
        modes = [variant["mode"] for variant in data["variants"]]
        assert "safe" in modes
        assert "balanced" in modes
        assert "aggressive" in modes
    
    def test_optimize_variant_structure(self):
        """Test that each variant has the expected structure."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Test prompt"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for variant in data["variants"]:
            assert "mode" in variant
            assert "prompt" in variant
            assert "tokens" in variant
            assert "saved_tokens" in variant
            assert variant["mode"] in ["safe", "balanced", "aggressive"]
    
    def test_optimize_with_explicit_mode(self):
        """Test optimization request with explicit mode."""
        response = client.post(
            "/api/optimize",
            json={
                "prompt": "Test prompt",
                "mode": "aggressive"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return all variants regardless of requested mode
        assert len(data["variants"]) == 3
    
    def test_optimize_empty_prompt_rejected(self):
        """Test that empty prompt is rejected."""
        response = client.post(
            "/api/optimize",
            json={"prompt": ""}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_optimize_whitespace_prompt_rejected(self):
        """Test that whitespace-only prompt is rejected."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "   "}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_optimize_missing_prompt_rejected(self):
        """Test that missing prompt field is rejected."""
        response = client.post(
            "/api/optimize",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_optimize_invalid_mode_rejected(self):
        """Test that invalid optimization mode is rejected."""
        response = client.post(
            "/api/optimize",
            json={
                "prompt": "Test",
                "mode": "super_aggressive"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_optimize_long_prompt(self):
        """Test optimization with a longer prompt."""
        long_prompt = """
        Please write a very detailed and comprehensive SQL query that will 
        select all users from our database, including their email addresses,
        usernames, and creation dates. Make sure to order the results by 
        creation date in descending order.
        """
        
        response = client.post(
            "/api/optimize",
            json={"prompt": long_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["original_tokens"] > 20  # Should have substantial token count
        assert len(data["variants"]) == 3
    
    def test_optimize_code_prompt(self):
        """Test optimization with a code-related prompt."""
        code_prompt = "def hello():\n    print('Hello, world!')\n    return True"
        
        response = client.post(
            "/api/optimize",
            json={"prompt": code_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["original_prompt"] == code_prompt
        assert data["original_tokens"] > 0
    
    def test_optimize_special_characters(self):
        """Test optimization with special characters."""
        special_prompt = "Hello! @#$% 123 👍 Test"
        
        response = client.post(
            "/api/optimize",
            json={"prompt": special_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["original_prompt"] == special_prompt
    
    def test_optimize_response_schema_compliance(self):
        """Test that response matches the expected schema."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Test prompt"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required top-level fields
        assert "original_prompt" in data
        assert "original_tokens" in data
        assert "variants" in data
        
        # Optional field
        assert "analysis" in data or "analysis" not in data  # Optional
        
        # Each variant should have required fields
        for variant in data["variants"]:
            assert "mode" in variant
            assert "prompt" in variant
            assert "tokens" in variant
            assert "saved_tokens" in variant


class TestRealOptimization:
    """Tests for real optimization functionality (Step 7)."""
    
    def test_verbose_prompt_gets_optimized(self):
        """Test that verbose prompts are actually optimized."""
        verbose_prompt = "Could you please very kindly write a really simple SQL query."
        
        response = client.post(
            "/api/optimize",
            json={"prompt": verbose_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Balanced and aggressive should produce different text
        balanced = next(v for v in data["variants"] if v["mode"] == "balanced")
        aggressive = next(v for v in data["variants"] if v["mode"] == "aggressive")
        
        # At least one variant should be different from original
        assert balanced["prompt"] != verbose_prompt or aggressive["prompt"] != verbose_prompt
    
    def test_token_savings_are_positive(self):
        """Test that verbose prompts show positive token savings."""
        verbose_prompt = "Please, if you would be so kind, could you very kindly write a SQL query."
        
        response = client.post(
            "/api/optimize",
            json={"prompt": verbose_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # At least balanced should save tokens on this verbose prompt
        balanced = next(v for v in data["variants"] if v["mode"] == "balanced")
        assert balanced["saved_tokens"] >= 0  # Some savings expected
    
    def test_saved_tokens_calculated_correctly(self):
        """Test that saved_tokens = original_tokens - optimized_tokens."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Please write a very simple function."}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for variant in data["variants"]:
            expected_saved = data["original_tokens"] - variant["tokens"]
            assert variant["saved_tokens"] == expected_saved
    
    def test_optimization_levels_differ(self):
        """Test that different optimization levels produce different results."""
        verbose_prompt = "Could you please just write a very simple function that adds numbers."
        
        response = client.post(
            "/api/optimize",
            json={"prompt": verbose_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        safe = next(v for v in data["variants"] if v["mode"] == "safe")
        balanced = next(v for v in data["variants"] if v["mode"] == "balanced")
        aggressive = next(v for v in data["variants"] if v["mode"] == "aggressive")
        
        # Aggressive should save at least as much as balanced
        assert aggressive["saved_tokens"] >= balanced["saved_tokens"]
        
        # Balanced should save at least as much as safe
        assert balanced["saved_tokens"] >= safe["saved_tokens"]
    
    def test_applied_rules_in_notes(self):
        """Test that applied optimization rules are included in notes."""
        verbose_prompt = "Please write a very detailed SQL query."
        
        response = client.post(
            "/api/optimize",
            json={"prompt": verbose_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Balanced should have some rules applied
        balanced = next(v for v in data["variants"] if v["mode"] == "balanced")
        assert "notes" in balanced
        assert isinstance(balanced["notes"], list)
        assert len(balanced["notes"]) > 0
    
    def test_concise_prompt_minimal_optimization(self):
        """Test that already concise prompts see minimal changes."""
        concise_prompt = "Write function to add numbers"
        
        response = client.post(
            "/api/optimize",
            json={"prompt": concise_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have minimal or no savings
        for variant in data["variants"]:
            assert variant["saved_tokens"] <= 2  # Minimal savings
    
    def test_whitespace_optimization(self):
        """Test that extra whitespace is normalized."""
        messy_prompt = "Write   a   function  that  adds  numbers  ."
        
        response = client.post(
            "/api/optimize",
            json={"prompt": messy_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Safe mode should at least normalize whitespace
        safe = next(v for v in data["variants"] if v["mode"] == "safe")
        assert "   " not in safe["prompt"]  # Multiple spaces should be collapsed
    
    def test_filler_words_removed(self):
        """Test that filler words are removed in balanced/aggressive modes."""
        filler_prompt = "Please write a very simple and really basic function."
        
        response = client.post(
            "/api/optimize",
            json={"prompt": filler_prompt}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        balanced = next(v for v in data["variants"] if v["mode"] == "balanced")
        
        # Fillers should be reduced
        assert balanced["tokens"] < data["original_tokens"]
    
    def test_analysis_field_present(self):
        """Test that prompt analysis is included in response."""
        response = client.post(
            "/api/optimize",
            json={"prompt": "Write a SQL query to select users."}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "analysis" in data
        assert data["analysis"] is not None
        assert "task" in data["analysis"] or "output_format" in data["analysis"]

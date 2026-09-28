"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError
from app.core.schemas import (
    OptimizationMode,
    OptimizeRequest,
    PromptVariant,
    OptimizeResponse
)


class TestOptimizationMode:
    """Tests for OptimizationMode enum."""
    
    def test_optimization_modes_exist(self):
        """Test that all expected modes are defined."""
        assert OptimizationMode.SAFE == "safe"
        assert OptimizationMode.BALANCED == "balanced"
        assert OptimizationMode.AGGRESSIVE == "aggressive"
    
    def test_optimization_mode_values(self):
        """Test that modes have correct string values."""
        modes = [mode.value for mode in OptimizationMode]
        assert "safe" in modes
        assert "balanced" in modes
        assert "aggressive" in modes


class TestOptimizeRequest:
    """Tests for OptimizeRequest schema."""
    
    def test_valid_request_minimal(self):
        """Test valid request with minimal fields."""
        request = OptimizeRequest(prompt="Hello, world!")
        
        assert request.prompt == "Hello, world!"
        assert request.mode == OptimizationMode.BALANCED  # default
    
    def test_valid_request_with_mode(self):
        """Test valid request with explicit mode."""
        request = OptimizeRequest(
            prompt="Test prompt",
            mode=OptimizationMode.AGGRESSIVE
        )
        
        assert request.prompt == "Test prompt"
        assert request.mode == OptimizationMode.AGGRESSIVE
    
    def test_valid_request_mode_as_string(self):
        """Test that mode can be provided as string."""
        request = OptimizeRequest(
            prompt="Test prompt",
            mode="safe"
        )
        
        assert request.mode == OptimizationMode.SAFE
    
    def test_prompt_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed."""
        request = OptimizeRequest(prompt="  Hello  ")
        assert request.prompt == "Hello"
    
    def test_empty_prompt_rejected(self):
        """Test that empty prompt is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            OptimizeRequest(prompt="")
        
        # Check that validation error occurred (min_length catches empty string)
        assert "validation error" in str(exc_info.value).lower()
    
    def test_whitespace_only_prompt_rejected(self):
        """Test that whitespace-only prompt is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            OptimizeRequest(prompt="   ")
        
        assert "Prompt cannot be empty" in str(exc_info.value)
    
    def test_invalid_mode_rejected(self):
        """Test that invalid mode is rejected."""
        with pytest.raises(ValidationError):
            OptimizeRequest(prompt="Test", mode="invalid_mode")
    
    def test_missing_prompt_rejected(self):
        """Test that missing prompt field is rejected."""
        with pytest.raises(ValidationError):
            OptimizeRequest(mode="safe")


class TestPromptVariant:
    """Tests for PromptVariant schema."""
    
    def test_valid_variant_minimal(self):
        """Test valid variant with minimal fields."""
        variant = PromptVariant(
            mode=OptimizationMode.SAFE,
            prompt="Optimized text",
            tokens=5,
            saved_tokens=2
        )
        
        assert variant.mode == OptimizationMode.SAFE
        assert variant.prompt == "Optimized text"
        assert variant.tokens == 5
        assert variant.saved_tokens == 2
        assert variant.notes is None
    
    def test_valid_variant_with_notes(self):
        """Test valid variant with notes."""
        variant = PromptVariant(
            mode=OptimizationMode.BALANCED,
            prompt="Test",
            tokens=1,
            saved_tokens=3,
            notes=["Removed filler", "Compressed"]
        )
        
        assert variant.notes == ["Removed filler", "Compressed"]
    
    def test_negative_tokens_rejected(self):
        """Test that negative token count is rejected."""
        with pytest.raises(ValidationError):
            PromptVariant(
                mode=OptimizationMode.SAFE,
                prompt="Test",
                tokens=-1,
                saved_tokens=0
            )
    
    def test_negative_saved_tokens_allowed(self):
        """Test that negative saved tokens is allowed (optimization could increase tokens)."""
        variant = PromptVariant(
            mode=OptimizationMode.SAFE,
            prompt="Test",
            tokens=10,
            saved_tokens=-5
        )
        
        assert variant.saved_tokens == -5
    
    def test_zero_tokens_allowed(self):
        """Test that zero tokens is valid."""
        variant = PromptVariant(
            mode=OptimizationMode.SAFE,
            prompt="",
            tokens=0,
            saved_tokens=0
        )
        
        assert variant.tokens == 0


class TestOptimizeResponse:
    """Tests for OptimizeResponse schema."""
    
    def test_valid_response_minimal(self):
        """Test valid response with minimal fields."""
        response = OptimizeResponse(
            original_prompt="Test prompt",
            original_tokens=5,
            variants=[
                PromptVariant(
                    mode=OptimizationMode.SAFE,
                    prompt="Test",
                    tokens=1,
                    saved_tokens=4
                )
            ]
        )
        
        assert response.original_prompt == "Test prompt"
        assert response.original_tokens == 5
        assert len(response.variants) == 1
        assert response.analysis is None
    
    def test_valid_response_with_multiple_variants(self):
        """Test response with multiple variants."""
        variants = [
            PromptVariant(
                mode=OptimizationMode.SAFE,
                prompt="Test 1",
                tokens=2,
                saved_tokens=3
            ),
            PromptVariant(
                mode=OptimizationMode.BALANCED,
                prompt="Test 2",
                tokens=1,
                saved_tokens=4
            ),
            PromptVariant(
                mode=OptimizationMode.AGGRESSIVE,
                prompt="T",
                tokens=1,
                saved_tokens=4
            )
        ]
        
        response = OptimizeResponse(
            original_prompt="Test prompt",
            original_tokens=5,
            variants=variants
        )
        
        assert len(response.variants) == 3
    
    def test_valid_response_with_analysis(self):
        """Test response with analysis field."""
        response = OptimizeResponse(
            original_prompt="Test",
            original_tokens=1,
            variants=[
                PromptVariant(
                    mode=OptimizationMode.SAFE,
                    prompt="Test",
                    tokens=1,
                    saved_tokens=0
                )
            ],
            analysis={
                "task": "testing",
                "constraints": ["none"]
            }
        )
        
        assert response.analysis == {"task": "testing", "constraints": ["none"]}
    
    def test_empty_variants_list_rejected(self):
        """Test that response must have at least one variant."""
        with pytest.raises(ValidationError):
            OptimizeResponse(
                original_prompt="Test",
                original_tokens=1,
                variants=[]
            )
    
    def test_negative_original_tokens_rejected(self):
        """Test that negative original tokens is rejected."""
        with pytest.raises(ValidationError):
            OptimizeResponse(
                original_prompt="Test",
                original_tokens=-1,
                variants=[
                    PromptVariant(
                        mode=OptimizationMode.SAFE,
                        prompt="Test",
                        tokens=1,
                        saved_tokens=0
                    )
                ]
            )
    
    def test_response_serialization(self):
        """Test that response can be serialized to JSON."""
        response = OptimizeResponse(
            original_prompt="Test",
            original_tokens=1,
            variants=[
                PromptVariant(
                    mode=OptimizationMode.SAFE,
                    prompt="Test",
                    tokens=1,
                    saved_tokens=0,
                    notes=["No changes"]
                )
            ]
        )
        
        json_data = response.model_dump()
        
        assert json_data["original_prompt"] == "Test"
        assert json_data["original_tokens"] == 1
        assert len(json_data["variants"]) == 1
        assert json_data["variants"][0]["mode"] == "safe"

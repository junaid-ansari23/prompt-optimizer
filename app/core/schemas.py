"""Pydantic schemas for request/response models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class OptimizationMode(str, Enum):
    """Optimization mode options."""
    SAFE = "safe"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class OptimizeRequest(BaseModel):
    """Request model for prompt optimization."""
    
    prompt: str = Field(
        ...,
        min_length=1,
        description="The prompt text to optimize",
        examples=["Write a SQL query to select all users from the database."]
    )
    
    mode: Optional[OptimizationMode] = Field(
        default=OptimizationMode.BALANCED,
        description="Optimization mode: safe (minimal), balanced (moderate), or aggressive (maximum)"
    )
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt_not_empty(cls, v: str) -> str:
        """Ensure prompt is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v.strip()


class PromptVariant(BaseModel):
    """A single optimized variant of the prompt."""
    
    mode: OptimizationMode = Field(
        ...,
        description="The optimization mode used for this variant"
    )
    
    prompt: str = Field(
        ...,
        description="The optimized prompt text"
    )
    
    tokens: int = Field(
        ...,
        ge=0,
        description="Token count for this optimized variant"
    )
    
    saved_tokens: int = Field(
        ...,
        description="Number of tokens saved compared to original (can be negative)"
    )
    
    notes: Optional[list[str]] = Field(
        default=None,
        description="Optional notes about transformations applied"
    )


class OptimizeResponse(BaseModel):
    """Response model for prompt optimization."""
    
    original_prompt: str = Field(
        ...,
        description="The original prompt text submitted"
    )
    
    original_tokens: int = Field(
        ...,
        ge=0,
        description="Token count for the original prompt"
    )
    
    variants: list[PromptVariant] = Field(
        ...,
        min_length=1,
        description="List of optimized variants"
    )
    
    analysis: Optional[dict] = Field(
        default=None,
        description="Optional analysis of the prompt structure"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "original_prompt": "Write a SQL query to select all users.",
                    "original_tokens": 10,
                    "variants": [
                        {
                            "mode": "safe",
                            "prompt": "Write SQL query to select all users.",
                            "tokens": 9,
                            "saved_tokens": 1,
                            "notes": ["Removed filler words"]
                        },
                        {
                            "mode": "balanced",
                            "prompt": "SQL: select all users",
                            "tokens": 6,
                            "saved_tokens": 4,
                            "notes": ["Removed filler words", "Compressed format"]
                        },
                        {
                            "mode": "aggressive",
                            "prompt": "SELECT * FROM users",
                            "tokens": 5,
                            "saved_tokens": 5,
                            "notes": ["Direct SQL output"]
                        }
                    ]
                }
            ]
        }
    }

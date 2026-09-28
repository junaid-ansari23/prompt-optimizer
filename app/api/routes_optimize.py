"""API routes for prompt optimization."""

from fastapi import APIRouter, HTTPException
from app.core.schemas import OptimizeRequest, OptimizeResponse
from app.service.optimize_service import optimize_prompt_service

router = APIRouter(prefix="/api", tags=["optimization"])


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(request: OptimizeRequest) -> OptimizeResponse:
    """
    Optimize a prompt to reduce token usage.
    
    This endpoint delegates to the service layer for business logic.
    Generates three optimization variants: safe, balanced, and aggressive.
    Each variant applies different levels of rule-based transformations.
    
    Args:
        request: OptimizeRequest containing the prompt and optional mode
    
    Returns:
        OptimizeResponse with original prompt and optimized variants
    
    Raises:
        HTTPException: If optimization fails
    """
    try:
        # Delegate to service layer for business logic
        response = optimize_prompt_service(request)
        return response
        
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing prompt: {str(e)}"
        )

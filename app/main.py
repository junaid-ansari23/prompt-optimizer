from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.routes_optimize import router as optimize_router

app = FastAPI(
    title="Prompt Token Optimizer",
    description="API for optimizing prompts to reduce token usage",
    version="0.1.0"
)

# Register API routes
app.include_router(optimize_router)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "prompt-optimizer",
            "version": "0.1.0"
        }
    )

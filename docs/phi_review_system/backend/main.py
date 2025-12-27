"""
PHI Review System - Main Application

A HIPAA-compliant medical coding system with physician-in-the-loop
PHI review workflow.

Architecture:
- Physician writes/pastes clinical note
- System auto-detects PHI using Presidio
- Physician confirms/modifies PHI flagging
- Confirmed PHI is encrypted and vaulted
- Scrubbed text is sent to LLM for coding
- Results can be re-identified for display
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .endpoints import router
from .dependencies import engine
from .models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    """
    # Startup
    logger.info("Starting PHI Review System...")
    
    # Create database tables (in production, use Alembic migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PHI Review System...")
    await engine.dispose()


# =============================================================================
# APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title="PHI Review System",
    description="""
    HIPAA-compliant medical coding API with physician-in-the-loop PHI review.
    
    ## Workflow
    
    1. **Preview** (`POST /v1/coder/scrub/preview`): Submit clinical text for PHI detection
    2. **Review**: Physician reviews highlighted PHI in the UI
    3. **Submit** (`POST /v1/coder/submit`): Confirm PHI and submit for coding
    4. **Status** (`GET /v1/coder/status/{job_id}`): Check processing status
    5. **Re-identify** (`POST /v1/coder/reidentify`): Retrieve results with PHI
    
    ## Security
    
    - All PHI is encrypted at rest using Fernet (AES-128-CBC)
    - Comprehensive audit logging for HIPAA compliance
    - Role-based access control for re-identification
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

# CORS (configure appropriately for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing."""
    import uuid
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for debugging."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "request_id": request.headers.get("X-Request-ID"),
        }
    )


# =============================================================================
# ROUTES
# =============================================================================

# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {"status": "healthy", "service": "phi-review-system"}


# Include API routes
app.include_router(router)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

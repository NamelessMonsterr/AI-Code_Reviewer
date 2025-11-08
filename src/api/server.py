from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest
from contextlib import asynccontextmanager
import logging
import time
from typing import Optional

from sqlalchemy import create_engine                 # <–– add SQLAlchemy import
from sqlalchemy.pool import QueuePool                # <–– for explicit poolclass
import redis                                         # <–– for Redis client

from src.config.settings import Settings
from src.config.validator import validate_configuration
from src.security.rate_limiter import RateLimiter
from src.security.input_validator import InputValidator
from src.auth.rbac import RBACManager, Permission
from src.autofix.code_fixer import CodeFixer
from src.analytics.metrics_tracker import MetricsTracker
from src.security.env_validator import validate_production_env

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load and validate configuration
settings = validate_configuration()

# === DATABASE CONNECTION POOL ===
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    # optionally: echo=settings.SQL_ECHO
)
logger.info("Database engine created with pool_size=20, max_overflow=40")

# === REDIS CONNECTION POOL ===
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,           # e.g., 'redis'
    port=settings.REDIS_PORT,           # e.g., 6379
    max_connections=50,
    decode_responses=True
)
redis_client = redis.Redis(connection_pool=redis_pool)
logger.info("Redis client created with connection pool of max_connections=50")

# Initialize components
rate_limiter = RateLimiter(settings.REDIS_URL)   # maybe reuse redis_client instead?
input_validator = InputValidator()
rbac_manager = RBACManager()
code_fixer = CodeFixer()
metrics_tracker = MetricsTracker()

# Prometheus metrics
review_counter = Counter('code_reviews_total', 'Total code reviews')
review_duration = Histogram('review_duration_seconds', 'Review duration')
error_counter = Counter('api_errors_total', 'Total API errors', ['endpoint', 'error_type'])

# Slowapi rate limiter for endpoints
limiter = Limiter(key_func=get_remote_address)

# HTTP Bearer token authentication
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    if settings.ENVIRONMENT.lower() == 'production':
        validate_production_env()
    logger.info("🚀 Starting AI Code Review Bot API Server")
    logger.info(f"Environment: {settings.ENVIRONMENT}, Debug: {settings.DEBUG}, Port: {settings.PORT}")
    yield
    logger.info("🛑 Shutting down AI Code Review Bot API Server")

app = FastAPI(
    title="AI Code Review Bot API",
    description="Enterprise-grade AI-powered code review system",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    return response

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        error_counter.labels(endpoint=request.url.path, error_type=type(e).__name__).inc()
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "message": str(e)}
        )

# … rest of your endpoints (unchanged) …

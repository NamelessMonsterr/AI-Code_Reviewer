import os
import sys


def validate_production_env():
    """Validate production environment variables"""
    errors = []

    # Check JWT_SECRET
    jwt_secret = os.getenv("JWT_SECRET", "")
    if jwt_secret == "your-jwt-secret-key-at-least-32-characters-long-please-change-this":
        errors.append("CRITICAL: JWT_SECRET is using default value!")

    if len(jwt_secret) < 32:
        errors.append("CRITICAL: JWT_SECRET must be at least 32 characters!")

    # Check API Keys
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("ERROR: OPENAI_API_KEY is required!")

    # Check Database
    db_url = os.getenv("DATABASE_URL", "")
    if "localhost" in db_url and os.getenv("ENVIRONMENT") == "production":
        errors.append("WARNING: Using localhost database in production!")

    if errors:
        print("❌ Environment Validation Failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("✅ Environment validation passed!")


if __name__ == "__main__":
    validate_production_env()

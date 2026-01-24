"""
Configuration management for Mployable

Supports environment-specific configs with validation and sensible defaults.
"""

import os
from pathlib import Path
from enum import Enum
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Environment(str, Enum):
    """Application environment"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Config:
    """Base configuration class"""

    # Application
    APP_NAME = "Mployable"
    VERSION = "1.0.0"

    # Environment
    ENVIRONMENT = Environment.DEVELOPMENT
    DEBUG = False

    # Server
    HOST = "0.0.0.0"
    PORT = 5000
    WORKERS = 1

    # Logging
    LOG_LEVEL = "INFO"
    LOG_DIR = "logs"

    # Security
    SECRET_KEY = "dev-secret-key-change-in-production"
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5000"]

    # API Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_PERIOD = 3600  # 1 hour in seconds

    # Caching
    CACHE_ENABLED = True
    CACHE_TTL_GITHUB = 3600  # 1 hour
    CACHE_TTL_ANALYSIS = 7200  # 2 hours
    CACHE_TTL_RESUME = 86400  # 24 hours
    REDIS_URL = "redis://localhost:6379/0"

    # External APIs
    GITHUB_API_TIMEOUT = 30
    GEMINI_API_TIMEOUT = 30
    LINKEDIN_API_TIMEOUT = 30

    # GitHub Scraper
    GITHUB_MAX_REPOS = 20
    GITHUB_MAX_TOP_PROJECTS = 5

    # Gemini
    GEMINI_MODEL = "gemini-2.0-flash-lite"
    GEMINI_MAX_TOKENS = 2000
    GEMINI_TEMPERATURE = 0.7

    # Resume Generation
    MAX_RESUME_SIZE_MB = 10
    RESUME_TIMEOUT = 300  # 5 minutes

    # Database (MongoDB)
    DATABASE_URL = "mongodb://localhost:27017/mployable"
    DATABASE_NAME = "mployable"
    DATABASE_HOST = "localhost"
    DATABASE_PORT = 27017
    DATABASE_USERNAME = None
    DATABASE_PASSWORD = None

    # File Upload
    MAX_UPLOAD_SIZE_MB = 50
    UPLOAD_DIR = "uploads"
    TEMP_DIR = "temp"

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        load_dotenv()

        # Load values from environment
        cls.ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", "development"))
        cls.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        cls.HOST = os.getenv("HOST", cls.HOST)
        cls.PORT = int(os.getenv("PORT", cls.PORT))
        cls.WORKERS = int(os.getenv("WORKERS", cls.WORKERS))

        # Security
        secret_key = os.getenv("SECRET_KEY")
        if secret_key:
            cls.SECRET_KEY = secret_key
        if (
            cls.ENVIRONMENT == Environment.PRODUCTION
            and cls.SECRET_KEY == "dev-secret-key-change-in-production"
        ):
            raise ValueError("SECRET_KEY must be set in production")

        cls.SESSION_COOKIE_SECURE = cls.ENVIRONMENT == Environment.PRODUCTION

        # CORS
        cors_origins = os.getenv("CORS_ORIGINS")
        if cors_origins:
            cls.CORS_ORIGINS = cors_origins.split(",")

        # APIs
        cls.GITHUB_API_TIMEOUT = int(
            os.getenv("GITHUB_API_TIMEOUT", cls.GITHUB_API_TIMEOUT)
        )
        cls.GEMINI_API_TIMEOUT = int(
            os.getenv("GEMINI_API_TIMEOUT", cls.GEMINI_API_TIMEOUT)
        )

        # Cache
        cls.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        cls.REDIS_URL = os.getenv("REDIS_URL", cls.REDIS_URL)

        # Database
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            cls.DATABASE_URL = db_url

        cls.DATABASE_NAME = os.getenv("DATABASE_NAME", cls.DATABASE_NAME)
        cls.DATABASE_HOST = os.getenv("DATABASE_HOST", cls.DATABASE_HOST)
        cls.DATABASE_PORT = int(os.getenv("DATABASE_PORT", cls.DATABASE_PORT))
        cls.DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
        cls.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

        return cls


# Environment-specific configuration classes
class DevelopmentConfig(Config):
    """Development environment configuration"""

    DEBUG = True
    LOG_LEVEL = "DEBUG"
    SESSION_COOKIE_SECURE = False
    CORS_ORIGINS = ["*"]  # Allow all origins in development
    RATE_LIMIT_ENABLED = False  # Disable rate limiting for easier testing
    CACHE_ENABLED = False  # Disable caching for fresh data during development


class StagingConfig(Config):
    """Staging environment configuration"""

    ENVIRONMENT = Environment.STAGING
    DEBUG = False
    LOG_LEVEL = "INFO"
    SESSION_COOKIE_SECURE = True
    RATE_LIMIT_ENABLED = True
    CACHE_ENABLED = True


class ProductionConfig(Config):
    """Production environment configuration"""

    ENVIRONMENT = Environment.PRODUCTION
    DEBUG = False
    LOG_LEVEL = "WARNING"
    SESSION_COOKIE_SECURE = True
    RATE_LIMIT_ENABLED = True
    CACHE_ENABLED = True
    RATE_LIMIT_REQUESTS = 1000
    WORKERS = 4


class TestingConfig(Config):
    """Testing environment configuration"""

    ENVIRONMENT = Environment.TESTING
    DEBUG = True
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    CACHE_ENABLED = False
    RATE_LIMIT_ENABLED = False


def get_config() -> Config:
    """Get configuration for current environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = config_map.get(env, DevelopmentConfig)
    return config_class.from_env()


# Validate required environment variables
def validate_config():
    """Validate that all required configuration is present"""
    required_vars = [
        "GEMINI_API_KEY",  # Gemini is required for resume generation
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    # Optional but recommended
    recommended = [
        "GITHUB_TOKEN",
        "SECRET_KEY",
    ]

    missing_recommended = [var for var in recommended if not os.getenv(var)]
    if missing_recommended:
        print(
            f"Warning: Missing recommended environment variables: {', '.join(missing_recommended)}"
        )


# Export current configuration
config = get_config()

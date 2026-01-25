"""
Custom exceptions for LLMployable application

Provides a hierarchy of application-specific exceptions for better
error handling and categorization.
"""


class LLMployableException(Exception):
    """Base exception for all LLMployable errors"""

    def __init__(
        self, message: str, error_code: str = "INTERNAL_ERROR", status_code: int = 500
    ):
        """
        Initialize exception with message and error code

        Args:
            message: Error description
            error_code: Machine-readable error code
            status_code: HTTP status code (for API responses)
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self):
        """Convert exception to dictionary for JSON response"""
        return {
            "error": self.error_code,
            "message": self.message,
            "status": self.status_code,
        }


# Input Validation Errors
class ValidationError(LLMployableException):
    """Raised when user input validation fails"""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR", 400)


class InvalidGitHubUsername(ValidationError):
    """Invalid GitHub username"""

    def __init__(self, username: str):
        super().__init__(
            f"Invalid GitHub username: '{username}'. Username must be alphanumeric and hyphens only.",
            "INVALID_GITHUB_USERNAME",
        )


class InvalidJobDescription(ValidationError):
    """Invalid job description"""

    def __init__(self, reason: str = "Job description is too short or invalid"):
        super().__init__(reason, "INVALID_JOB_DESCRIPTION")


# External Service Errors
class ExternalServiceError(LLMployableException):
    """Base exception for external service failures"""

    def __init__(self, service: str, message: str, status_code: int = 503):
        super().__init__(
            f"{service} service error: {message}",
            f"{service.upper()}_ERROR",
            status_code,
        )
        self.service = service


class GitHubAPIError(ExternalServiceError):
    """GitHub API request failed"""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__("GitHub", message, status_code)


class GitHubUserNotFound(GitHubAPIError):
    """GitHub user not found"""

    def __init__(self, username: str):
        super().__init__(f"User '{username}' not found on GitHub", 404)


class GitHubRateLimitExceeded(GitHubAPIError):
    """GitHub API rate limit exceeded"""

    def __init__(self, reset_time: int = None):
        msg = "GitHub API rate limit exceeded"
        if reset_time:
            msg += f". Rate limit resets at {reset_time}"
        super().__init__(msg, 429)


class GeminiAPIError(ExternalServiceError):
    """Google Gemini API request failed"""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__("Gemini", message, status_code)


class GeminiQuotaExceeded(GeminiAPIError):
    """Gemini API quota exceeded"""

    def __init__(self):
        super().__init__("API quota exceeded. Please try again later.", 429)


class LinkedInError(ExternalServiceError):
    """LinkedIn scraping failed"""

    def __init__(self, message: str):
        super().__init__("LinkedIn", message, 503)


# Processing Errors
class ProcessingError(LLMployableException):
    """Base exception for data processing errors"""

    def __init__(self, message: str, stage: str = None):
        self.stage = stage
        super().__init__(message, "PROCESSING_ERROR", 500)


class JobAnalysisError(ProcessingError):
    """Job description analysis failed"""

    def __init__(self, message: str = "Failed to analyze job description"):
        super().__init__(message, "JOB_ANALYSIS_ERROR")


class ResumeGenerationError(ProcessingError):
    """Resume generation failed"""

    def __init__(self, message: str = "Failed to generate resume"):
        super().__init__(message, "RESUME_GENERATION_ERROR")


class LaTeXCompilationError(ProcessingError):
    """LaTeX compilation failed"""

    def __init__(self, message: str, log_output: str = None):
        self.log_output = log_output
        super().__init__(message, "LATEX_COMPILATION_ERROR")


# Configuration Errors
class ConfigurationError(LLMployableException):
    """Configuration error"""

    def __init__(self, message: str, setting: str = None):
        self.setting = setting
        super().__init__(message, "CONFIGURATION_ERROR", 500)


class MissingAPIKey(ConfigurationError):
    """Required API key is missing"""

    def __init__(self, api_name: str):
        super().__init__(
            f"Required API key '{api_name}_API_KEY' not found in environment",
            f"MISSING_{api_name}_KEY",
        )


# Rate Limiting Errors
class RateLimitError(LLMployableException):
    """Rate limit exceeded"""

    def __init__(self, message: str = "Too many requests", retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)


# Cache Errors
class CacheError(LLMployableException):
    """Cache operation failed"""

    def __init__(self, message: str):
        super().__init__(message, "CACHE_ERROR", 500)


# Database Errors
class DatabaseError(LLMployableException):
    """Database operation failed"""

    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR", 500)


class DatabaseConnectionError(DatabaseError):
    """Failed to connect to database"""

    def __init__(self):
        super().__init__("Failed to connect to database")

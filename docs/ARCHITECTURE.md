# Architecture & Design Reference

This document provides technical reference for the production implementation of LLMployable.

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Client Browser                           │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP/HTTPS
                           ▼
┌──────────────────────────────────────────────────────────────┐
│         Nginx Reverse Proxy (nginx.conf)                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ - TLS/SSL Termination                                   │ │
│  │ - Rate Limiting (10 req/s)                              │ │
│  │ - Gzip Compression                                      │ │
│  │ - Security Headers                                      │ │
│  │ - Request Buffering                                     │ │
│  │ - Load Balancing (single upstream for now)              │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│      Flask Application (app_production.py)                   │
│  Gunicorn WSGI Server (4 workers, 2 threads each)            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Request Middleware                                      │ │
│  │  ├─ Request ID Generation                              │ │
│  │  ├─ Timing Tracking                                    │ │
│  │  └─ Logging                                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Route Handlers                                          │ │
│  │  ├─ GET /          (HTML interface)                     │ │
│  │  ├─ POST /api/v1/generate-resume                       │ │
│  │  ├─ GET /health    (basic check)                        │ │
│  │  └─ GET /api/v1/health (API check)                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Error Handlers                                          │ │
│  │  ├─ LLMployableException → JSON response                 │ │
│  │  ├─ 400 Bad Request                                    │ │
│  │  ├─ 404 Not Found                                      │ │
│  │  └─ 500 Internal Error                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
    Components       External APIs         Storage
┌───────────────┐ ┌───────────────────┐ ┌──────────────┐
│ GitHub Scraper│ │ GitHub API        │ │ Redis Cache  │
│ (with logging)│ │ (with timeouts)   │ │ (optional)   │
├───────────────┤ ├───────────────────┤ ├──────────────┤
│Job Analyzer   │ │ Gemini API        │ │PostgreSQL DB │
│(regex-based)  │ │ (with error hdlg) │ │ (future)     │
├───────────────┤ ├───────────────────┤ ├──────────────┤
│Resume Gen     │ │ LinkedIn API      │ │ Temp Files   │
│(with fallback)│ │ (placeholder)     │ │ (PDF, LaTeX) │
├───────────────┤ └───────────────────┘ └──────────────┘
│LaTeX Compiler │
│(with fallback)│
└───────────────┘
```

## Component Interaction Flow

### Resume Generation Request Flow

```
1. Client submits form with:
   - github_username (validated)
   - job_description (validated)
   - linkedin_data ZIP file (optional)
         ↓
2. Flask endpoint receives POST /api/v1/generate-resume
   - Generate request_id: "a1b2c3d4"
   - Log: "[a1b2c3d4] POST /api/v1/generate-resume"
         ↓
3. Input Validation (utils/validators.py)
   - ValidateGithubUsername: regex check
   - Validate JobDescription: length check
   - ValidateLinkedInUrl: URL pattern check
   - On error: raise ValidationError (400)
         ↓
4. Profile Scraping (scrapers/github_scraper.py)
   - GitHubScraper.scrape_profile(username)
   - Log: "[a1b2c3d4] Scraping GitHub profile: {username}"
   - On 404: raise GitHubUserNotFound
   - On rate limit: raise GitHubRateLimitExceeded
   - On error: raise GitHubAPIError
   - Result: profile_data dict
         ↓
5. Job Analysis (analyzer/job_analyzer.py)
   - JobAnalyzer.analyze(job_description)
   - Extract: skills, experience, education
   - Result: job_requirements dict
         ↓
6. Resume Content Generation (generator/resume_generator.py)
   - ResumeGenerator.generate(profile_data, job_requirements)
   - Use Gemini API (with fallback)
   - Result: resume_content dict
         ↓
7. LaTeX Compilation (generator/latex_compiler.py)
   - LaTeXCompiler.compile(resume_content)
   - Sanitize: all LaTeX special chars
   - Generate: .tex file
   - Compile: pdflatex → PDF
   - Result: pdf_path
         ↓
8. Security Check
   - Verify pdf_path is in temp directory
   - Prevent path traversal attacks
         ↓
9. Response
   - send_file(pdf_path, 'application/pdf')
   - Log: "[a1b2c3d4] Resume generated successfully"
         ↓
10. Client downloads PDF
```

## Configuration Hierarchy

```
┌─────────────────────────────────────────┐
│ Environment Variables                   │
│ (Loaded from .env or OS env)            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Config Module (config/config.py)        │
│ ┌─────────────────────────────────────┐ │
│ │ get_config()                        │ │
│ │  ├─ detect ENVIRONMENT              │ │
│ │  ├─ select config class             │ │
│ │  │  ├─ DevelopmentConfig            │ │
│ │  │  ├─ StagingConfig                │ │
│ │  │  ├─ ProductionConfig             │ │
│ │  │  └─ TestingConfig                │ │
│ │  └─ load & validate                 │ │
│ └─────────────────────────────────────┘ │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Application Code                        │
│ (Uses config.SETTING_NAME)              │
└─────────────────────────────────────────┘
```

## Exception Hierarchy

```
Exception
└── LLMployableException
    │   (base class with error_code, status_code)
    │
    ├── ValidationError (400)
    │   ├── InvalidGitHubUsername
    │   └── InvalidJobDescription
    │
    ├── ExternalServiceError (503)
    │   ├── GitHubAPIError
    │   │   ├── GitHubUserNotFound (404)
    │   │   └── GitHubRateLimitExceeded (429)
    │   ├── GeminiAPIError
    │   │   └── GeminiQuotaExceeded (429)
    │   └── LinkedInError
    │
    ├── ProcessingError (500)
    │   ├── JobAnalysisError
    │   ├── ResumeGenerationError
    │   └── LaTeXCompilationError
    │
    ├── ConfigurationError (500)
    │   └── MissingAPIKey
    │
    ├── RateLimitError (429)
    │
    ├── CacheError (500)
    │
    └── DatabaseError (500)
        └── DatabaseConnectionError
```

## Logging Architecture

```
┌─────────────────────────────────────────┐
│ Logging Configuration (config/logging_config.py)
│ ┌─────────────────────────────────────┐ │
│ │ setup_logging(name, log_level, ...) │ │
│ │  Creates logger with handlers       │ │
│ └─────────────────────────────────────┘ │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌──────────┐
│Console │  │File    │  │Rotating  │
│Handler │  │Handler │  │FileHndlr │
└────┬───┘  └───┬────┘  └────┬─────┘
     │          │            │
     │          │            │
  STDOUT    app.log      logs/
                         (10MB, 5 backups)
                         app.log
                         api.log
                         error.log
```

## Data Flow: Input Validation

```
User Input
    ↓
┌──────────────────────────────────┐
│ InputValidator.validate_request()│
├──────────────────────────────────┤
│ 1. validate_github_username()    │
│    - Check regex pattern         │
│    - Check length (1-39 chars)   │
│    - Raise InvalidGitHubUsername │
├──────────────────────────────────┤
│ 2. validate_job_description()    │
│    - Check length (50-50000)     │
│    - Raise InvalidJobDescription │
└──────────────────────────────────┘
    ↓
Cleaned Input (or Exception raised)
```

## Testing Strategy

### Unit Tests (test_comprehensive.py)
```
TestInputValidator
├── test_valid_github_username
├── test_invalid_github_username_format
├── test_valid_job_description
└── test_invalid_job_description_too_short

TestGitHubScraper
├── test_scrape_profile_success (mocked)
└── test_scrape_nonexistent_user (mocked)

TestJobAnalyzer
├── test_analyze_job_description
└── test_extract_experience_requirement

TestConfiguration
├── test_config_defaults
├── test_development_config
└── test_production_config

TestFlaskApp
├── test_health_endpoint
├── test_root_endpoint
├── test_generate_resume_endpoint (mocked)
└── test_error_cases

TestPerformance
├── test_validator_performance
└── test_config_loading_performance
```

## Deployment Architecture

### Docker Stack (docker-compose.yml)
```
┌──────────────┐
│ llmployable    │ (Flask + Gunicorn, 4 workers)
│ app:5000     │
└──────┬───────┘
       │ depends_on
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌─────────────┐   ┌──────────────┐  ┌────────────┐
│ redis       │   │ postgres     │  │ nginx      │
│ :6379       │   │ :5432        │  │ :80        │
│ (Cache)     │   │ (Database)   │  │ (Proxy)    │
└─────────────┘   └──────────────┘  └────────────┘

Docker Network: llmployable-network (bridge)
Volumes: redis-data, postgres-data
```

### Kubernetes Deployment
```
┌─────────────────────────────────────┐
│ Kubernetes Cluster                  │
├─────────────────────────────────────┤
│ Deployment: llmployable (3 replicas)  │
│ ├─ Pod 1: Flask app                 │
│ ├─ Pod 2: Flask app                 │
│ └─ Pod 3: Flask app                 │
│                                     │
│ Service: llmployable-service          │
│ ├─ Type: LoadBalancer               │
│ └─ Port: 80 → 5000                  │
│                                     │
│ External Resources:                 │
│ ├─ PostgreSQL (managed DB)          │
│ └─ Redis (managed cache)            │
└─────────────────────────────────────┘
```

## CI/CD Pipeline (.github/workflows/ci-cd.yml)

```
Push to main/develop
    ↓
┌─────────────────────────────────────┐
│ Test Job (Matrix: 3.9, 3.10, 3.11) │
├─────────────────────────────────────┤
│ 1. Lint with flake8                 │
│ 2. Format check with black          │
│ 3. Type check with mypy             │
│ 4. Run tests with pytest            │
│ 5. Upload coverage                  │
└─────┬───────────────────────────────┘
      │ on: success
      ▼
┌──────────────────────────────────────┐
│ Security Job                         │
├──────────────────────────────────────┤
│ 1. Bandit security scan              │
│ 2. Safety vulnerability check        │
└─────┬────────────────────────────────┘
      │ on: success
      ▼
┌──────────────────────────────────────┐
│ Build Job                            │
├──────────────────────────────────────┤
│ 1. Setup Docker Buildx               │
│ 2. Login to registry                 │
│ 3. Build & push Docker image         │
│ 4. Tag with branch/semver/sha        │
└─────┬────────────────────────────────┘
      │ on: develop branch
      ▼
┌──────────────────────────────────────┐
│ Deploy to Staging                    │
├──────────────────────────────────────┤
│ 1. Deploy to staging env             │
│ 2. Run smoke tests                   │
└──────────────────────────────────────┘

      On main branch (manual approval needed)
      ↓
┌──────────────────────────────────────┐
│ Deploy to Production                 │
├──────────────────────────────────────┤
│ 1. Deploy to prod env                │
│ 2. Run prod smoke tests              │
│ 3. Send notifications                │
└──────────────────────────────────────┘
```

## Error Response Format

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "status": 400
}

Examples:
{
  "error": "INVALID_GITHUB_USERNAME",
  "message": "Invalid GitHub username: 'invalid-user'. Username must be alphanumeric and hyphens only.",
  "status": 400
}

{
  "error": "GITHUB_USER_NOT_FOUND",
  "message": "User 'nonexistent' not found on GitHub",
  "status": 404
}

{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "GitHub API rate limit exceeded. Rate limit resets at ...",
  "status": 429
}
```

## Performance Considerations

### Response Times (Target)
- Health check: <100ms
- GitHub scrape: 1-3s
- Job analysis: 100-500ms
- Resume generation (Gemini): 2-5s
- LaTeX compilation: 1-2s
- **Total: 4-12 seconds** (target)

### Optimization Strategies
1. **Caching**: Redis for GitHub profiles, job analyses
2. **Async**: Background jobs for long operations
3. **Compression**: Gzip responses
4. **Rate Limiting**: Prevent abuse
5. **Database Indexing**: Fast lookups
6. **Connection Pooling**: Efficient database access

### Resource Limits
- Flask memory: 256-512 MB per worker
- Docker: 512 MB limit
- Timeout: 300 seconds for resume generation
- Upload size: 50 MB max
- Job description: 50-50000 characters

## Security Model

```
Input Security:
  - Regex validation (GitHub username)
  - Length validation (job description)
  - URL pattern validation (LinkedIn)
  - LaTeX sanitization (prevent injection)

Network Security:
  - CORS configuration (allowed origins)
  - Rate limiting (10 req/s)
  - HTTPS support (Session cookie secure)
  - Security headers (Nginx)

API Security:
  - Request validation
  - Error message sanitization
  - File path validation
  - API key secrets (environment)

Data Security:
  - No sensitive data in logs
  - Temporary file cleanup
  - Database encryption (future)
  - API key rotation support
```

---

This architecture provides a solid foundation for scaling and evolving LLMployable as requirements grow.

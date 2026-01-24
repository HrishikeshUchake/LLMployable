# Quick Start - Production Setup

This guide will get you up and running with the production-ready Mployable application in 5-10 minutes.

## Option 1: Local Development (Fastest)

### Setup (2 minutes)

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env and add:
# - GEMINI_API_KEY=your-key-here
# - GITHUB_TOKEN=your-token-here (optional)
```

### Run (1 minute)

```bash
# Development mode (with auto-reload)
ENVIRONMENT=development python app_production.py

# Open browser
open http://localhost:5000
```

## Option 2: Docker (Recommended for production)

### Setup (3 minutes)

```bash
# Copy environment
cp .env.example .env

# Edit .env with production values:
nano .env
```

### Run (2 minutes)

```bash
# Start all services (App + Redis + PostgreSQL + Nginx)
docker-compose up -d

# Check health
curl http://localhost/health

# View logs
docker-compose logs -f mployable

# Open browser
open http://localhost
```

## Option 3: Gunicorn Server

### Setup (2 minutes)

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env
```

### Run (1 minute)

```bash
gunicorn -w 4 \
         --worker-class gthread \
         --threads 2 \
         --timeout 120 \
         --bind 0.0.0.0:5000 \
         app_production:create_app()

# Open browser
open http://localhost:5000
```

## Testing the Application

### Quick Health Check

```bash
# Basic health
curl http://localhost:5000/health

# Detailed health  
curl http://localhost:5000/health/detailed

# API health
curl http://localhost:5000/api/v1/health
```

### Generate a Resume (Example)

```bash
# Using curl
curl -X POST http://localhost:5000/api/v1/generate-resume \
  -H "Content-Type: application/json" \
  -d '{
    "github_username": "torvalds",
    "linkedin_url": "",
    "job_description": "We are looking for a C programmer with 10+ years of experience working on operating systems and kernel development. Required skills: C, Assembly, Linux, Git. Nice to have: Rust, Python."
  }' \
  -o resume.pdf
```

## Running Tests

### Quick Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov

# Run specific test
pytest tests/test_comprehensive.py::TestInputValidator -v
```

## Common Operations

### View Logs

```bash
# Application logs
tail -f logs/app.log

# API logs
tail -f logs/api.log

# Error logs
tail -f logs/error.log

# Docker logs
docker-compose logs -f mployable
```

### Stop Services

```bash
# Docker Compose
docker-compose down

# Keep volumes (database data, Redis)
docker-compose down --volumes

# Kill gunicorn
pkill gunicorn
```

### Check Status

```bash
# Docker containers
docker-compose ps

# Application health
curl http://localhost:5000/health

# Check port usage
lsof -i :5000
```

## Configuration Quick Reference

| Setting | Development | Production |
|---------|-------------|-----------|
| DEBUG | true | false |
| LOG_LEVEL | DEBUG | WARNING |
| CACHE_ENABLED | false | true |
| RATE_LIMIT_ENABLED | false | true |
| HOST | 127.0.0.1 | 0.0.0.0 |
| SESSION_COOKIE_SECURE | false | true |
| WORKERS | 1 | 4 |

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use different port
PORT=8000 python app_production.py
```

### Missing API Key

```bash
# Error: Missing GEMINI_API_KEY

# Solution: Add to .env
echo "GEMINI_API_KEY=your-key-here" >> .env

# Verify
grep GEMINI_API_KEY .env
```

### LaTeX Not Found

```bash
# Error: pdflatex not found

# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra

# macOS
brew install basictex
```

### Database Connection Error

```bash
# Error: Failed to connect to database

# With Docker Compose: Wait for PostgreSQL to start
docker-compose logs postgres

# With manual PostgreSQL: Verify connection
psql $DATABASE_URL -c "SELECT 1"
```

## Next Steps

1. **Review Documentation**
   - [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) - Full implementation plan
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
   - [PRODUCTION_IMPLEMENTATION.md](PRODUCTION_IMPLEMENTATION.md) - What's been done

2. **Customize Configuration**
   - Review all options in [.env.example](../.env.example)
   - Set environment-specific values
   - Configure database and Redis (if using)

3. **Run Tests**
   - `pytest tests/ -v --cov` to verify everything works
   - Review test output for any failures

4. **Deploy**
   - For production: Follow cloud platform guide in [DEPLOYMENT.md](DEPLOYMENT.md)
   - For staging: Use Docker Compose with staging configuration
   - For development: Use local Python environment

5. **Monitor**
   - Setup health checks: `curl http://localhost:5000/health`
   - Review logs regularly: `tail -f logs/app.log`
   - Configure error tracking (Sentry) in production

## Architecture

```
User Browser
    ↓
Nginx (Rate Limiting, SSL, Compression)
    ↓
Flask App (Gunicorn, 4 workers)
    ↓
┌───────────────────────────────────┐
│ GitHub API  │  Gemini API  │ etc. │
└───────────────────────────────────┘
    ↓
Redis Cache (optional)
PostgreSQL Database (optional)
```

## Performance Tips

1. **Enable Caching**: Set `CACHE_ENABLED=true` and configure Redis
2. **Use Gunicorn**: Don't use Flask dev server in production
3. **Configure Workers**: Set `WORKERS=4` for quad-core systems
4. **Use Reverse Proxy**: Nginx for rate limiting and SSL
5. **Monitor Logs**: Watch `logs/error.log` for issues

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `SESSION_COOKIE_SECURE=true` (requires HTTPS)
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Use HTTPS with valid SSL certificate
- [ ] Store API keys in secrets manager
- [ ] Enable rate limiting: `RATE_LIMIT_ENABLED=true`
- [ ] Review and enable monitoring/logging

## Support

For detailed information:
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- See [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) for future improvements
- See [README.md](README.md) for feature overview

Happy deploying! 🚀

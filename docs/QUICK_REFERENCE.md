# Quick Reference Guide

## Essential Commands

### Setup & Installation

```bash
# Clone repository
git clone <repo-url>
cd LLMployable

# Copy environment template
cp .env.example .env

# Install Python dependencies
pip install -r requirements.txt

# Start Docker services
docker-compose up -d

# Initialize database
python -c "from database import init_db; init_db()"
```

### Running the Application

```bash
# Production mode (with Docker)
docker-compose up -d

# Development mode (Flask dev server)
ENVIRONMENT=development python app_production.py

# Access web interface
open http://localhost:5000

# API health check
curl http://localhost:5000/api/v1/health
```

### Database Operations

```bash
# MongoDB shell
docker-compose exec mongodb mongosh
use llmployable
show collections

# View user data
db.users.find()

# View resumes
db.resumes.find()

# Count documents
db.resumes.countDocuments()

# Create backup
docker exec llmployable-mongodb mongodump --out /backup
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=./ --cov-report=html

# Run specific test file
pytest tests/test_comprehensive.py::TestInputValidator -v

# Run tests matching pattern
pytest tests/ -k "validate" -v

# Run tests with detailed output
pytest tests/ -vv --tb=long
```

### Code Quality

```bash
# Format code with Black
black .

# Check code style
flake8 .

# Type checking
mypy . --ignore-missing-imports

# Security scanning
bandit -r . -f json

# All quality checks
black . && flake8 . && mypy . --ignore-missing-imports
```

### Logging & Monitoring

```bash
# View application logs
docker-compose logs -f llmployable

# View MongoDB logs
docker-compose logs -f mongodb

# View specific log file
tail -f logs/app.log
tail -f logs/error.log
tail -f logs/api.log

# Search logs
grep "ERROR" logs/error.log
grep "generate_resume" logs/api.log
```

### Debugging

```bash
# Enable debug mode
ENVIRONMENT=development DEBUG=true python app_production.py

# Connect to MongoDB directly
docker-compose exec mongodb mongosh
> use llmployable
> db.resumes.find({_id: ObjectId("...")})

# Check container status
docker-compose ps

# View container logs with timestamps
docker-compose logs --timestamps --tail=100 llmployable

# SSH into container
docker-compose exec llmployable /bin/bash
```

### Docker Management

```bash
# Build image
docker build -t llmployable:latest .

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild services
docker-compose up -d --build

# View service status
docker-compose ps

# Restart specific service
docker-compose restart mongodb

# View resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Stage changes
git add .

# Commit with message
git commit -m "Add MongoDB integration"

# Push to remote
git push origin feature/my-feature

# View changes
git diff

# View log
git log --oneline

# Stash changes
git stash

# Create pull request (on GitHub)
# Then merge after approval
```

### Deployment

```bash
# Build and tag image
docker build -t registry.example.com/llmployable:latest .

# Push to registry
docker push registry.example.com/llmployable:latest

# Deploy with docker-compose (staging)
docker-compose -f docker-compose.staging.yml up -d

# Deploy with docker-compose (production)
docker-compose -f docker-compose.prod.yml up -d

# Check deployment status
docker-compose ps
curl http://localhost:5000/health
```

## Common Workflows

### Starting Development Session

```bash
# 1. Start services
docker-compose up -d

# 2. Check services are running
docker-compose ps

# 3. Run tests to ensure everything works
pytest tests/

# 4. Start coding
# Edit files in your editor
```

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Implement feature
# Edit files, create tests

# 3. Run tests
pytest tests/

# 4. Format and lint
black . && flake8 .

# 5. Commit changes
git add .
git commit -m "Add new feature"

# 6. Push and create PR
git push origin feature/new-feature
# Create PR on GitHub
```

### Debugging an Issue

```bash
# 1. Check logs
docker-compose logs -f llmployable | grep ERROR

# 2. Check database
docker-compose exec mongodb mongosh
use llmployable
db.audit_logs.find({status: "failure"}).limit(5)

# 3. Enable debug mode and test
ENVIRONMENT=development DEBUG=true python app_production.py

# 4. Add logging to pinpoint issue
# Edit code, run tests

# 5. Commit fix
git add .
git commit -m "Fix: Resolved issue with..."
```

### Database Migration

```bash
# 1. Connect to MongoDB
docker-compose exec mongodb mongosh
use llmployable

# 2. Check data
db.resumes.find().limit(1)

# 3. Run migration script
# Create migration.py script

# 4. Test migration
pytest tests/test_migration.py

# 5. Verify data integrity
db.resumes.countDocuments()
```

## File Locations

| What | Where |
|------|-------|
| Application code | `app_production.py` |
| Models | `database/mongodb.py` |
| Tests | `tests/test_comprehensive.py` |
| Configuration | `config/config.py` |
| Environment | `.env` |
| Logs | `logs/` directory |
| Temporary files | `temp/` directory |
| Uploads | `uploads/` directory |
| Documentation | `*.md` files |

## Environment Variables

```bash
# Required
GEMINI_API_KEY=your-key

# Optional but recommended
GITHUB_TOKEN=your-token

# Application
ENVIRONMENT=production  # or development, staging
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=mongodb://localhost:27017/llmployable
DATABASE_NAME=llmployable

# Server
HOST=0.0.0.0
PORT=5000

# See .env.example for all options
```

## Useful URLs

| Purpose | URL |
|---------|-----|
| Web UI | http://localhost:5000 |
| API Health | http://localhost:5000/health |
| API Detailed Health | http://localhost:5000/api/v1/health/detailed |
| Nginx | http://localhost:80 |
| Redis | localhost:6379 |
| MongoDB | localhost:27017 |

## Troubleshooting Quick Fixes

### Services won't start
```bash
# Check Docker daemon
docker ps

# Rebuild images
docker-compose build --no-cache

# Check port conflicts
lsof -i :5000
lsof -i :27017
```

### Database connection error
```bash
# Check MongoDB is running
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb

# Check connection string in .env
cat .env | grep DATABASE
```

### Tests failing
```bash
# Run with verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Run specific test
pytest tests/test_comprehensive.py::TestInputValidator::test_valid_github_username -vv
```

### Permission errors
```bash
# Fix file permissions
chmod -R 755 logs/ temp/ uploads/

# Fix Docker socket (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

## Performance Optimization

```bash
# Monitor database queries
docker-compose exec mongodb mongosh
> db.setProfilingLevel(1)
> db.system.profile.find().pretty()

# Check indexes
> db.resumes.getIndexes()

# Create missing index
> db.resumes.createIndex({user_id: 1, created_at: -1})

# Check connection pool
# In logs, look for "MongoDB connection pool"
```

## Security Quick Checks

```bash
# Verify no hardcoded secrets
grep -r "GEMINI_API_KEY=" .
grep -r "password=" .

# Check environment file
cat .env  # Should not contain real secrets

# Scan for security issues
bandit -r . -f json | grep "HIGH\|CRITICAL"

# Review Docker image
docker inspect llmployable:latest
```

## Learning Resources

- **MongoDB:** See `MONGODB_GUIDE.md`
- **Production Setup:** See `PRODUCTION_ROADMAP.md`
- **Database Models:** See `database/mongodb.py`
- **Examples:** See `tests/test_comprehensive.py`
- **API:** See `app_production.py`

## Emergency Procedures

### Database Recovery
```bash
# Backup current data
docker exec llmployable-mongodb mongodump --out /backup-$(date +%Y%m%d)

# Restore from backup
docker exec llmployable-mongodb mongorestore /backup-20240124
```

### Service Restart
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart llmployable

# Hard restart (stop and start)
docker-compose down
docker-compose up -d
```

### Rollback Deployment
```bash
# Use previous image tag
docker tag llmployable:previous llmployable:latest

# Restart with previous version
docker-compose down
docker-compose up -d
```

## Contact & Support

- **Documentation:** See `.md` files in root
- **Issues:** Create GitHub issue
- **Questions:** Check FAQ in documentation
- **Bug Reports:** See bug-report template

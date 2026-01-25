# Deployment Guide - LLMployable

This guide covers deploying LLMployable to production environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Troubleshooting](#troubleshooting)

## Local Development

### Prerequisites

- Python 3.9+
- PostgreSQL or SQLite
- Redis (optional, for caching)
- LaTeX (for PDF generation)

### Setup

```bash
# Clone repository
git clone <repository-url>
cd LLMployable

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
# - Add GEMINI_API_KEY
# - Add GITHUB_TOKEN (optional)
# - Set ENVIRONMENT=development

# Run application
python app_production.py
```

The application will be available at `http://localhost:5000`

### Development Server

For development with auto-reload:

```bash
export FLASK_APP=app_production.py
export FLASK_ENV=development
flask run
```

## Docker Deployment

### Build Docker Image

```bash
# Build image
docker build -t llmployable:latest .

# Tag for registry
docker tag llmployable:latest myregistry/llmployable:latest
```

### Run with Docker Compose

```bash
# Start all services (app, Redis, PostgreSQL, Nginx)
docker-compose up -d

# View logs
docker-compose logs -f llmployable

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Environment Variables

Create `.env` file for docker-compose:

```bash
ENVIRONMENT=production
GEMINI_API_KEY=your-key-here
GITHUB_TOKEN=your-token-here
DATABASE_URL=postgresql://llmployable:llmployable@postgres:5432/llmployable
REDIS_URL=redis://redis:6379/0
```

### Health Checks

```bash
# Check container health
docker-compose ps

# Test application health
curl http://localhost:5000/health
curl http://localhost/api/v1/health  # Through Nginx
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Docker image pushed to registry
- PostgreSQL database (separate from cluster)
- Redis (separate from cluster)

### Create Kubernetes Manifests

Create `k8s/llmployable-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llmployable
  labels:
    app: llmployable
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llmployable
  template:
    metadata:
      labels:
        app: llmployable
    spec:
      containers:
      - name: llmployable
        image: myregistry/llmployable:latest
        ports:
        - containerPort: 5000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: gemini-api-key
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: github-token
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
```

Create `k8s/llmployable-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: llmployable-service
spec:
  selector:
    app: llmployable
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic api-secrets \
  --from-literal=gemini-api-key=<YOUR_KEY> \
  --from-literal=github-token=<YOUR_TOKEN>

kubectl create secret generic db-secrets \
  --from-literal=database-url=postgresql://...

# Deploy application
kubectl apply -f k8s/llmployable-deployment.yaml
kubectl apply -f k8s/llmployable-service.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/llmployable

# Scale deployment
kubectl scale deployment llmployable --replicas=5
```

## Cloud Platform Deployment

### AWS Deployment

#### Option 1: EC2

```bash
# Launch EC2 instance (Ubuntu 22.04)
# SSH into instance

# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip texlive-latex-base texlive-latex-extra

# Clone and setup
git clone <repo>
cd LLMployable
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment
cp .env.example .env
# Edit .env with production values

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app_production:create_app()
```

#### Option 2: ECS (Elastic Container Service)

```bash
# Push Docker image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
docker tag llmployable:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/llmployable:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/llmployable:latest

# Create ECS task definition and service through AWS Console or AWS CLI
```

#### Option 3: App Service (Managed PaaS)

Similar to Azure App Service deployment below.

### Azure Deployment

#### Using Azure App Service

```bash
# Create resource group
az group create --name llmployable-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name llmployable-plan \
  --resource-group llmployable-rg \
  --sku B2 --is-linux

# Create web app
az webapp create \
  --resource-group llmployable-rg \
  --plan llmployable-plan \
  --name llmployable-app \
  --runtime "PYTHON|3.11"

# Configure deployment from Git
az webapp deployment source config-zip \
  --resource-group llmployable-rg \
  --name llmployable-app \
  --src app.zip

# Set application settings
az webapp config appsettings set \
  --resource-group llmployable-rg \
  --name llmployable-app \
  --settings ENVIRONMENT=production \
              GEMINI_API_KEY=<KEY> \
              GITHUB_TOKEN=<TOKEN>
```

### GCP Deployment

#### Using Cloud Run

```bash
# Authenticate
gcloud auth login
gcloud config set project <PROJECT_ID>

# Build and push image
gcloud builds submit --tag gcr.io/<PROJECT_ID>/llmployable:latest

# Deploy to Cloud Run
gcloud run deploy llmployable \
  --image gcr.io/<PROJECT_ID>/llmployable:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars ENVIRONMENT=production,GEMINI_API_KEY=<KEY>,GITHUB_TOKEN=<TOKEN> \
  --memory 512Mi \
  --timeout 300
```

## Environment Configuration

### Production Environment Variables

Create production `.env` file:

```bash
ENVIRONMENT=production
SECRET_KEY=<STRONG_RANDOM_KEY>
HOST=0.0.0.0
PORT=5000
WORKERS=4

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# APIs
GEMINI_API_KEY=<YOUR_KEY>
GITHUB_TOKEN=<YOUR_TOKEN>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/llmployable

# Cache
CACHE_ENABLED=true
REDIS_URL=redis://redis-host:6379/0

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=https://yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
```

### Using Secrets Manager

AWS Secrets Manager:
```bash
aws secretsmanager create-secret \
  --name llmployable/production \
  --secret-string file://secrets.json
```

## Monitoring & Logging

### Application Logging

Logs are written to `logs/` directory with rotation:

- `app.log` - Application logs
- `api.log` - API request/response logs  
- `error.log` - Error logs

View logs:
```bash
tail -f logs/app.log
tail -f logs/error.log
```

### Application Monitoring

#### Health Checks

```bash
# Basic health
curl http://localhost:5000/health

# Detailed health
curl http://localhost:5000/health/detailed

# API health
curl http://localhost:5000/api/v1/health
```

#### Metrics Collection

Setup Prometheus scraping (if using metrics):

```bash
# Prometheus configuration
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'llmployable'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

### Error Tracking

Setup Sentry for error tracking:

```python
# In app_production.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

if config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1
    )
```

## Troubleshooting

### Application Won't Start

```bash
# Check for port conflicts
lsof -i :5000

# Verify environment variables
env | grep -E 'GEMINI|GITHUB|DATABASE'

# Check logs
tail -f logs/error.log

# Test imports
python -c "from app_production import create_app; print('OK')"
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"

# Check connection string format
# postgresql://username:password@host:port/database
```

### LaTeX Compilation Failures

```bash
# Verify LaTeX installation
which pdflatex
pdflatex --version

# Install missing packages
sudo apt-get install texlive-latex-extra
```

### High Memory Usage

```bash
# Check process memory
ps aux | grep app_production

# Reduce worker count
WORKERS=2 python app_production.py

# Enable caching to reduce API calls
CACHE_ENABLED=true
```

### Rate Limiting Issues

```bash
# Disable rate limiting for debugging
RATE_LIMIT_ENABLED=false

# Check Redis connection
redis-cli ping

# Monitor rate limit status
RATE_LIMIT_REQUESTS=10  # Lower limit for testing
```

## Performance Tuning

### Web Server

Use Gunicorn for production:

```bash
gunicorn -w 4 \
         --worker-class gthread \
         --threads 2 \
         --timeout 120 \
         --bind 0.0.0.0:5000 \
         --access-logfile - \
         --error-logfile - \
         app_production:create_app()
```

### Database Connection Pooling

```python
# Configured in config/config.py
DATABASE_POOL_SIZE = 10
DATABASE_MAX_OVERFLOW = 20
```

### Caching Strategy

Enable Redis caching for better performance:

```bash
CACHE_ENABLED=true
REDIS_URL=redis://redis-host:6379/0
CACHE_TTL_GITHUB=3600        # 1 hour
CACHE_TTL_ANALYSIS=7200      # 2 hours
```

## Backup & Recovery

### Database Backups

```bash
# PostgreSQL daily backup
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Restore from backup
gunzip < /backups/db_20240101.sql.gz | psql $DATABASE_URL
```

### Application State Backup

```bash
# Backup logs and generated resumes
tar -czf backups/app_state_$(date +%Y%m%d).tar.gz logs/ uploads/ temp/
```

## Security Hardening

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS with valid SSL certificate
- [ ] Enable CORS only for trusted origins
- [ ] Set SESSION_COOKIE_SECURE=true
- [ ] Enable rate limiting
- [ ] Regular security updates: `pip install --upgrade -r requirements.txt`
- [ ] Use secrets manager for API keys
- [ ] Enable audit logging
- [ ] Regular security audits

## Support & Documentation

For issues and questions:
- GitHub Issues: [Repository Issues]
- Documentation: See [README.md](../README.md)
- Production Roadmap: See [PRODUCTION_ROADMAP.md](../PRODUCTION_ROADMAP.md)

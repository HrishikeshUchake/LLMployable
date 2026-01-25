# Multi-stage Dockerfile for Mployable

# Stage 1: Frontend Builder
FROM node:20-slim as frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# Set API URL to empty string so it uses relative paths in production
ENV VITE_API_URL=""
RUN npm run build

# Stage 2: Python Builder
FROM python:3.11-slim as python-builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 3: Runtime
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies (LaTeX, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=python-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy frontend build to a directory Flask can serve
RUN mkdir -p static
COPY --from=frontend-builder /frontend/dist ./static

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p logs uploads temp && \
    chmod -R 755 logs uploads temp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Default environment
ENV ENVIRONMENT=production \
    HOST=0.0.0.0 \
    PORT=5000 \
    STATIC_FOLDER=static

# Run with gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app_production:create_app()"]

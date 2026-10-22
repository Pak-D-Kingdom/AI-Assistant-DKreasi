# Base Image Python 3.12 Slim
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY app/ app/
COPY knowledge_base/ knowledge_base/
COPY tenant_templates/ tenant_templates/
COPY widget/ widget/
COPY main.py .

# Create directory for persistent runtime data (SQLite DB & FAISS indices)
RUN mkdir -p /app/data

# Expose AI Engine Port
EXPOSE 8001

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

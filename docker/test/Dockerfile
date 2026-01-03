FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for better Docker caching
COPY pyproject.toml ./

# Install Python dependencies from pyproject.toml (base + dev extras for testing)
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

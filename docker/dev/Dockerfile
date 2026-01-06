FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# hadolint ignore=DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /app

# Install system dependencies and uv
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (installed to ~/.local/bin by the install script)
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files first for better Docker caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv (base + dev extras)
# --system flag installs packages system-wide in the container
RUN uv pip install --system -e ".[dev]"

COPY . .

EXPOSE 8000

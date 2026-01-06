FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (installed to ~/.local/bin by the install script)
ENV PATH="/root/.local/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy dependency files first for better Docker caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv (base + production extras)
# --system flag installs packages system-wide in the container
RUN uv pip install --system -e ".[production]"

COPY . .

# Copy and setup entrypoint script
COPY docker/production/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Change ownership
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

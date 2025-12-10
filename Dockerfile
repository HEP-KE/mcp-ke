# Single-stage build for MCP-KE server with CLASS support
FROM python:3.11-slim

# Install build dependencies for CLASS (includes runtime libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libgsl-dev \
    libfftw3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy all application code (needed for editable install)
COPY pyproject.toml ./
COPY mcp_server.py ./
COPY hybrid_server.py ./
COPY mcp_utils/ ./mcp_utils/
COPY codes/ ./codes/
COPY tools/ ./tools/
COPY agent_tools/ ./agent_tools/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Create directories for data
RUN mkdir -p /app/input /app/out

# Copy input data if it exists (optional - can be volume-mounted)
COPY input/ /app/input/

# Set environment variables
ENV MCP_TRANSPORT=sse \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    PYTHONUNBUFFERED=1

# Expose the SSE server port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/tools').read()" || exit 1

# Run the hybrid server (supports both MCP and REST)
CMD ["python", "hybrid_server.py"]

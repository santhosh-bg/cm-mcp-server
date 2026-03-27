# Stage 1: Build and Install
FROM python:3.12-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy only the files needed for installation first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies without the project itself 
# This layer stays cached unless your dependencies change
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the source code
COPY . .

# Install the project (this creates the entry point/executable)
RUN uv sync --frozen --no-dev --no-editable

# Stage 2: Runtime
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Ensure the venv's bin directory is in the PATH
# This makes your [project.scripts] executable globally
ENV PATH="/app/.venv/bin:$PATH"

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1

# Use the entry point name you defined in pyproject.toml
ENTRYPOINT ["cm-mcp-server"]

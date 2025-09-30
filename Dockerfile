FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy the application code
COPY analytics_mcp/ ./analytics_mcp/

# Create directory for credentials
RUN mkdir -p /secrets/adc

# Expose port for Cloud Run
EXPOSE 8080

# Set environment variables
ENV PORT=8080

# Run the server with HTTP transport
CMD ["python", "-m", "analytics_mcp.server", "--transport", "http", "--port", "8080"]

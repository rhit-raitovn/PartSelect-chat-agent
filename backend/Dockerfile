FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for vector database
RUN mkdir -p /app/chroma_db

# Expose port
EXPOSE 8000

# Run initialization script and then start server
CMD python scripts/setup_vector_db.py && python main.py
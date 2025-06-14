# Base image with Python 3.11
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy local files to the container
COPY . /app

# Set open ai arg
ARG OPENAI_API_KEY

# Set environment variables
ENV OPENAI_API_KEY=$OPENAI_API_KEY

# Install system dependencies for DuckDB and other tools
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the data directory exists
RUN mkdir -p /app/data/csv

# Expose ports (optional, if you're running a web app or API)
EXPOSE 8501

# Default command to run your Python script
CMD ["python", "main.py"]
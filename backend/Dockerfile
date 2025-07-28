# backend/Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (including your 'app' folder and 'run.py')
COPY . .

# Expose port (default Flask port, as defined in run.py)
EXPOSE 5000

# Start Flask app using run.py
CMD ["python", "run.py"]
# Base Image
FROM python:3.11-slim

# Maintainer / Metadata
LABEL maintainer="CAMPS-ML Engineering Team"
LABEL description="Centralized Academic Monitoring and Prediction System Using Machine Learning"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application source code
COPY . .

# Run database seeder if not populated, then expose port
EXPOSE 5000

# Start production server with Gunicorn (4 workers, 120s timeout for ML inference)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "wsgi:app"]

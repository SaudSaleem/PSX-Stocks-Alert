# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Chrome/Chromium and Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p /app/app/data

# Expose port
EXPOSE 8000

# Run database migrations and start the application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]


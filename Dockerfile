# Dockerfile for deploying the LINE Bot to Hugging Face Spaces
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (for sqlite etc., usually fine)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app (including university_bot.db)
COPY . .

# Hugging Face Spaces typically exposes on port 7860
# We set PORT env in Space settings or here
ENV PORT=7860

# Expose the port
EXPOSE 7860

# Run with gunicorn (recommended for HF Spaces and production)
# Workers=1 or 2 is fine for LINE bot
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 app:app
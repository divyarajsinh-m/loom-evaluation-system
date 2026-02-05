FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for yt-dlp
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY app.py .
COPY plivo_logo.png .

# Create directories
RUN mkdir -p .streamlit knowledge_base batch_videos

# Streamlit config
COPY .streamlit/config.toml .streamlit/config.toml

# Secrets are injected at runtime, not baked into image
# Use: docker run -v /path/to/secrets.toml:/app/.streamlit/secrets.toml

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]

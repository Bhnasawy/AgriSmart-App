# =====================================================
# AgriSmart - Hugging Face Spaces Dockerfile
# =====================================================
FROM python:3.11-slim

# Hugging Face Spaces runs as user 1000
RUN useradd -m -u 1000 user
USER user

# Set environment paths
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Copy requirements first (for Docker layer caching)
COPY --chown=user requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY --chown=user . .

# Create necessary folders
RUN mkdir -p uploads ml_models instance

# Expose port 7860 (required by Hugging Face Spaces)
EXPOSE 7860

# Start the app with gunicorn on port 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "app:app"]

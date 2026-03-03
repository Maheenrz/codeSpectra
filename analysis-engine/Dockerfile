FROM python:3.9-slim-bullseye

# Install System Dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py /app/main.py
COPY api /app/api
COPY config /app/config
COPY core /app/core
COPY data /app/data
COPY detectors /app/detectors
COPY engine /app/engine
COPY models /app/models
COPY schemas /app/schemas
COPY services /app/services
COPY utils /app/utils

RUN mkdir -p /workspace

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

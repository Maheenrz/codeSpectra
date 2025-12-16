# Use a Python base image that supports the required system dependencies (Bullseye is stable)
FROM python:3.9-slim-bullseye

# 1. Install System Dependencies 
# We keep these tools installed as they contain shared libraries (like libicu-dev, etc.) 
# that might be useful for future Type 4 analysis, but the compilation steps are gone.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    git \
    libtool \
    autoconf \
    automake \
    make \
    build-essential \
    autoconf-archive \
    libboost-all-dev \
    libicu-dev \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# --- Python Setup (Ready for Native Detection) ---

# Set the working directory to /app
WORKDIR /app

# 2. Install Python Dependencies
# NOTE: Ensure 'pygments' is in your requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy Code Structure (MAPPING YOUR EXACT STRUCTURE)
COPY main.py /app/main.py
COPY app /app/app 

# 4. Set the command to run your FastAPI service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
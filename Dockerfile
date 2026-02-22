FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install minimal dependencies for Python packages (OpenCV, matplotlib, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose ports for both Streamlit (8501) and FastAPI (8000)
EXPOSE 8000 8501

# Default to FastAPI backend
# Use environment variable APP_TYPE to switch between 'api' and 'web'
ENV APP_TYPE=api

CMD if [ "$APP_TYPE" = "web" ]; then \
        streamlit run web/app.py --server.port=8501 --server.address=0.0.0.0; \
    else \
        uvicorn src.main:app --host 0.0.0.0 --port 8000; \
    fi
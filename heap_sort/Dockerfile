# Python 3.11 lightweight image for Cloud Run
FROM python:3.11-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application source files (algorithms.py, main.py, etc.)
COPY . .

# Cloud Run port
EXPOSE 8080

# Start FastAPI application (Google Cloud Run official CMD format)
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}

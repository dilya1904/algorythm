FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

WORKDIR /app

# Upgrade pip and install dependencies (wheel-only, no gcc needed)
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all server files (including main.py and algorithms.py)
COPY . .

# Expose default Cloud Run port
EXPOSE 8080

# Run uvicorn using exec form so SIGTERM is handled properly
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}


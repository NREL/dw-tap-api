# Use the official Python image with Debian trixie
FROM python:3.13-slim-trixie

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
ENV PYTHONPATH=/app

# Set the working directory
WORKDIR $APP_HOME

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application
COPY . .

# Generate OpenAPI spec at build-time
RUN python scripts/generate_openapi.py || true

# Expose the port
EXPOSE 8000

# Run the app with Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]

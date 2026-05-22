# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY app.py .

# Expose port for FastAPI service
EXPOSE 8000

# Run uvicorn server
CMD ["python", "app.py"]

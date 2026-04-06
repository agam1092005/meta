FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y bash git docker-compose && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY server/templates/hard/requirements.txt /tmp/req-hard.txt

# Install dependencies normally (no || true hack!)
RUN pip install -r requirements.txt
RUN pip install -r /tmp/req-hard.txt

# Copy the entire project into the container
COPY . /app/

# Set up the workspace directory AND grant full permissions
RUN mkdir -p /app/server/workspace && chmod -R 777 /app

# Set environment variables
ENV PYTHONPATH=/app

# Start the FastAPI server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
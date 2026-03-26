FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y bash git docker-compose && rm -rf /var/lib/apt/lists/*

# Install dependencies from the hard task template (most comprehensive)
COPY server/templates/hard/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn pydantic openenv openai requests

# Copy the entire project into the container
COPY . /app/

# Set up the workspace directory
RUN mkdir -p /app/server/workspace

# Set environment variables
ENV PYTHONPATH=/app
ENV OPENAI_API_KEY=your_key_here

# Start the FastAPI server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]

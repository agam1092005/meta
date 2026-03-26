FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
# Added docker-compose for the Medium Task
RUN apt-get update && apt-get install -y bash git docker-compose && rm -rf /var/lib/apt/lists/*

# Install OpenEnv and dependencies
COPY cicd_pipeline_fixer/server/templates/hard/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn pydantic openenv openai

# Copy the environment code
COPY cicd_pipeline_fixer/ /app/cicd_pipeline_fixer/

# Set up the workspace
RUN mkdir -p /app/cicd_pipeline_fixer/server/workspace

ENV PYTHONPATH=/app
# Default OpenAI key placeholder for baseline agent
ENV OPENAI_API_KEY=your_key_here

CMD ["uvicorn", "cicd_pipeline_fixer.server.app:app", "--host", "0.0.0.0", "--port", "7860"]

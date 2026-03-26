# CI/CD Pipeline Fixer - OpenEnv RL Environment

## Running Locally & Testing

1. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Start the server:
   ```bash
   uvicorn cicd_pipeline_fixer.server.app:app --host 0.0.0.0 --port 7860
   ```

3. Run tests:
   ```bash
   pytest
   ```

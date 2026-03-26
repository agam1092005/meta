import os
import json
from openai import OpenAI
from cicd_pipeline_fixer.models import Action

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            _client = OpenAI(api_key=api_key)
        else:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
    return _client

def get_action(observation: str) -> Action:
    client = _get_client()
    prompt = f"""
    You are an expert DevOps engineer. Your goal is to fix a broken CI/CD pipeline.
    Current Observation:
    {observation}

    Respond ONLY with a JSON object matching the Action schema:
    {{
        "tool": "read_file" | "write_file" | "run_pipeline",
        "file_path": "path/to/file",
        "content": "new content for write_file"
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    return Action(**data)

if __name__ == "__main__":
    # Example usage for testing
    print("Baseline script loaded.")

import os
import json
import requests
from openai import OpenAI
from models import Action

# 1. Grab the strict hackathon variables
api_base = os.getenv("API_BASE_URL", "https://api.openai.com/v1") 
model_name = os.getenv("MODEL_NAME", "gpt-4-turbo")
hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    print("WARNING: HF_TOKEN environment variable is not set.")

# 2. Initialize the OpenAI client using THEIR variables
client = OpenAI(
    base_url=api_base,
    api_key=hf_token
)

def get_action(observation_text: str) -> Action:
    """
    Calls the LLM using the provided configuration to determine the next action.
    """
    # System prompt to guide the agent
    system_prompt = """
    You are an expert DevOps AI agent fixing a broken CI/CD pipeline.
    You will be provided with terminal outputs and file listings.
    You must output ONLY a valid JSON object matching this schema:
    {
      "tool": "read_file" | "write_file" | "run_pipeline",
      "file_path": "string (optional)",
      "content": "string (optional)"
    }
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": observation_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        # Parse the JSON string returned by the LLM into our Pydantic model
        result_json = response.choices[0].message.content
        return Action.model_validate_json(result_json)
        
    except Exception as e:
        print(f"Error calling LLM: {e}")
        # Fallback action to prevent complete crash
        return Action(tool="run_pipeline")

if __name__ == "__main__":
    import requests
    import time
    
    print("Testing Baseline Inference Script...")
    print("Connecting to local environment on port 7860...")
    
    try:
        # Trigger the baseline endpoint you built
        response = requests.post("http://localhost:7860/baseline", timeout=60)
        response.raise_for_status()
        
        data = response.json()
        print("\n--- Baseline Scores ---")
        for task, score in data.get("scores", {}).items():
            print(f"Task '{task.upper()}': {score}/1.0")
            
        print("\nBaseline script executed successfully.")
    except Exception as e:
        print(f"Failed to run baseline: {e}")
        print("Ensure the server is running (uvicorn server.app:app --port 7860)")

import os
import json
from typing import List, Optional
from openai import OpenAI

from models import Action
from server.environment import PipelineEnvironment

# --- Mandatory Hackathon Variables ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")

BENCHMARK = "cicd-pipeline-fixer"

# --- Strict Stdout Logging Functions (DO NOT MODIFY) ---
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# --- Agent Logic ---
def get_action(client: OpenAI, observation_text: str) -> Action:
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
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": observation_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        result_json = response.choices[0].message.content
        return Action.model_validate_json(result_json)
    except Exception as e:
        # Fallback action to prevent a total crash
        return Action(tool="run_pipeline")

def main():
    # Initialize the required OpenAI Client
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    # Initialize environment directly for maximum stability
    base_dir = os.path.dirname(os.path.abspath(__file__))
    workspace = os.path.join(base_dir, "server", "workspace")
    templates = os.path.join(base_dir, "server", "templates")

    env = PipelineEnvironment(workspace_root=workspace, templates_root=templates)

    # Run all 3 required tasks
    tasks = ["easy", "medium", "hard"]
    max_steps = 10

    for task_id in tasks:
        log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

        obs = env.reset(task_level=task_id)

        rewards_list = []
        steps_taken = 0

        for step in range(1, max_steps + 1):
            if obs.done:
                break

            obs_text = f"Terminal: {obs.terminal_output}\nFiles: {obs.files_in_directory}"
            action = get_action(client, obs_text)

            # Compress action into a single line string to avoid breaking the stdout parser
            action_str = json.dumps(action.model_dump(exclude_none=True), separators=(',', ':'))

            try:
                obs = env.step(action)
                reward = obs.reward
                done = obs.done
                error = None
            except Exception as e:
                reward = 0.0
                done = True
                error = str(e).replace('\n', ' ')

            rewards_list.append(reward)
            steps_taken = step

            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

        score = env.get_grader_score()
        success = score > 0.0

        log_end(success=success, steps=steps_taken, score=score, rewards=rewards_list)

if __name__ == "__main__":
    main()

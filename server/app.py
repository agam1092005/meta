from fastapi import FastAPI, Request
from openenv import create_fastapi_app
from .environment import PipelineEnvironment
from .models import Action, Observation
# Fixed: Absolute import for Docker compatibility
from baseline import get_action
import os
import asyncio

# Initialize environment
workspace = os.path.join(os.path.dirname(__file__), "workspace")
templates = os.path.join(os.path.dirname(__file__), "templates")
env = PipelineEnvironment(workspace, templates)

# Standard OpenEnv FastAPI wrapper
app = create_fastapi_app(env)

@app.get("/tasks")
async def get_tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "Fix a syntax error in build.sh or requirements.txt"},
            {"id": "medium", "description": "Fix a logic bug in app.py that causes test failures"},
            {"id": "hard", "description": "Fix a subtle configuration/linting error in the pipeline"}
        ],
        "action_schema": Action.schema()
    }

@app.get("/grader")
async def get_grader():
    return {"score": env.get_grader_score()}

@app.post("/baseline")
async def run_baseline_endpoint():
    """
    Triggers the OpenAI baseline agent for all 3 tasks (Easy, Medium, Hard).
    Returns the scores as required by the hackathon.
    """
    scores = {}
    for task_id in ["easy", "medium", "hard"]:
        # Reset to specific level
        obs = env.reset(task_level=task_id)
        
        # Simple loop for baseline agent to attempt the task
        max_steps = 5
        for _ in range(max_steps):
            try:
                # Get action from GPT-4o
                obs_text = f"Terminal: {obs.terminal_output}\nFiles: {obs.files_in_directory}"
                action = get_action(obs_text)
                
                # Execute action
                obs = env.step(action)
                
                if obs.done:
                    break
            except Exception:
                break 
        
        scores[task_id] = env.get_grader_score()
        
    return {
        "status": "baseline_completed",
        "scores": scores
    }

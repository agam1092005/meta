from fastapi import FastAPI, Request
from openenv.core.env_server import create_fastapi_app
from .environment import PipelineEnvironment
from models import Action, Observation
from inference import get_action
import os

# Initialize environment paths
workspace = os.path.join(os.path.dirname(__file__), "workspace")
templates = os.path.join(os.path.dirname(__file__), "templates")

# NOTE: OpenEnv expects the Environment CLASS, not the instance, 
# along with the Action and Observation models to build the spec automatically.
class BoundPipelineEnvironment(PipelineEnvironment):
    def __init__(self):
        super().__init__(workspace, templates)

# Standard OpenEnv FastAPI wrapper (Builds /ws, /step, /reset, /state natively)
app = create_fastapi_app(BoundPipelineEnvironment, Action, Observation)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the CI/CD Pipeline Fixer Environment",
        "status": "online",
        "endpoints": {
            "tasks": "/tasks",
            "grader": "/grader",
            "baseline": "/baseline (POST)"
        }
    }

@app.get("/tasks")
async def get_tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "Fix a syntax error in build.sh or requirements.txt"},
            {"id": "medium", "description": "Fix a logic bug in app.py that causes test failures"},
            {"id": "hard", "description": "Fix a subtle configuration/linting error in the pipeline"}
        ],
        "action_schema": Action.model_json_schema()
    }

@app.get("/grader")
async def get_grader():
    # We must instantiate the env locally just for the grader/baseline endpoints
    env = BoundPipelineEnvironment()
    return {"score": env.get_grader_score()}

@app.post("/baseline")
async def run_baseline_endpoint():
    """
    Triggers the inference.py baseline agent for all 3 tasks (Easy, Medium, Hard).
    Returns the scores as required by the hackathon.
    """
    env = BoundPipelineEnvironment()
    scores = {}
    for task_id in ["easy", "medium", "hard"]:
        obs = env.reset(task_level=task_id)
        max_steps = 5
        
        for _ in range(max_steps):
            try:
                obs_text = f"Terminal: {obs.terminal_output}\nFiles: {obs.files_in_directory}"
                action = get_action(obs_text)
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
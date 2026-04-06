from fastapi import FastAPI, Request
from openenv.core.env_server import create_fastapi_app
from .environment import PipelineEnvironment
from models import Action, Observation
from baseline import get_action
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

@app.get("/tasks")
async def get_tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "Fix a synta            {"id": "easy", "description": "Fix a synta            {"id": "easy", "descripix a logic bug in app.py that causes test failures"},
            {"id": "hard", "description"            {"id": "hard", "description"    i            {"id": "hard", "descriptiac            {"id": "hard", "den_     a()
                               c                                c                               t                                c                               nme                               c                                as                               c                                c            seline agent for all 3 tasks (Easy, Medium, Hard).
    Returns the scores as req    Returns the scores as req    Returns thoundPipelineEnvironment()
    scores = {}
    for task_id in ["easy", "medium", "hard"]:
        obs = env.reset(task_level=task_id)
        max_steps = 5
        
        for _ in range(max_steps):
            try:
                                                                                                                                                                                                                                     break
            except Exception:
                break 
        
        scores[task_id] = env.get_grader_score()
        
    return {
        "status": "baseline_completed",
        "scores": scores
    }

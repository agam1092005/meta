import requests
from .models import Action, Observation

class PipelineClient:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url

    def reset(self, task_level: str = "easy") -> Observation:
        response = requests.post(f"{self.base_url}/reset", json={"task_level": task_level})
        response.raise_for_status()
        return Observation(**response.json())

    def step(self, action: Action) -> Observation:
        response = requests.post(f"{self.base_url}/step", json=action.dict())
        response.raise_for_status()
        return Observation(**response.json())

    def get_state(self):
        response = requests.get(f"{self.base_url}/state")
        response.raise_for_status()
        return response.json()

    def get_grader(self):
        response = requests.get(f"{self.base_url}/grader")
        response.raise_for_status()
        return response.json()

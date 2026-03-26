import os
import shutil
import subprocess
import difflib
from typing import Tuple, Dict
from cicd_pipeline_fixer.models import Action, Observation, State

class PipelineEnvironment:
    def __init__(self, workspace_root: str, templates_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        self.templates_root = os.path.abspath(templates_root)
        self.state = State(
            current_task_level="easy", 
            pipeline_runs=0, 
            step_count=0,
            last_exit_code=1, 
            stage_reached=0,
            original_files={}
        )
        self.max_steps = 15

    def reset(self, task_level: str = "easy") -> Observation:
        self.state = State(
            current_task_level=task_level, 
            pipeline_runs=0, 
            step_count=0,
            last_exit_code=1, 
            stage_reached=0,
            original_files={}
        )
        
        if os.path.exists(self.workspace_root):
            shutil.rmtree(self.workspace_root)
        os.makedirs(self.workspace_root)
        
        template_path = os.path.join(self.templates_root, task_level)
        for item in os.listdir(template_path):
            s = os.path.join(template_path, item)
            d = os.path.join(self.workspace_root, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
                with open(s, 'r') as f:
                    self.state.original_files[item] = f.read()
                
        return self._get_observation("Environment reset.", 0, 0.0, False)

    def step(self, action: Action) -> Observation:
        self.state.step_count += 1
        reward = 0.0
        done = False
        output = ""
        exit_code = 0

        if action.tool == "read_file":
            reward = 0.01 
            if not action.file_path:
                output = "Error: file_path is required for read_file"
                exit_code = 1
                reward = -0.1
            else:
                try:
                    path = os.path.abspath(os.path.join(self.workspace_root, action.file_path))
                    if not path.startswith(self.workspace_root):
                        output = "Error: Permission denied. Path traversal detected."
                        exit_code = 1
                        reward = -0.5
                    elif os.path.exists(path):
                        with open(path, 'r') as f:
                            output = f.read()
                    else:
                        output = f"Error: File {action.file_path} not found"
                        exit_code = 1
                        reward = -0.1
                except Exception as e:
                    output = str(e)
                    exit_code = 1

        elif action.tool == "write_file":
            # Anti-Cheat: Protect critical files from modification
            protected_files = ["build.sh", "test_app.py", "deploy.sh"]
            if action.file_path in protected_files:
                output = f"Error: Permission denied. You cannot modify {action.file_path}."
                exit_code = 1
                reward = -0.1
            elif not action.file_path or action.content is None:
                output = "Error: file_path and content are required for write_file"
                exit_code = 1
                reward = -0.1
            else:
                try:
                    path = os.path.abspath(os.path.join(self.workspace_root, action.file_path))
                    if not path.startswith(self.workspace_root):
                        output = "Error: Permission denied. Path traversal detected."
                        exit_code = 1
                        reward = -0.5
                    else:
                        with open(path, 'w') as f:
                            f.write(action.content)
                        output = f"Successfully wrote to {action.file_path}"
                        reward = 0.05
                except Exception as e:
                    output = str(e)
                    exit_code = 1

        elif action.tool == "run_pipeline":
            self.state.pipeline_runs += 1
            try:
                env_vars = {**os.environ, "GITHUB_ACTIONS": "true", "CI": "true"}
                
                # GHA Runner Simulation for Hard Task
                workflow_path = os.path.join(self.workspace_root, "workflow.yml")
                if self.state.current_task_level == "hard" and os.path.exists(workflow_path):
                    with open(workflow_path, 'r') as f:
                        workflow_content = f.read()
                    # Check if agent fixed the YAML to correctly map the secret
                    if "API_KEY: ${{ secrets.PROD_API_KEY }}" in workflow_content:
                        env_vars["API_KEY"] = "supersecret"

                cmd = ["bash", "build.sh"]
                if os.path.exists(os.path.join(self.workspace_root, "docker-compose.yml")):
                    output += "[System] Detected docker-compose.yml. Running in containerized mode...\n"
                
                result = subprocess.run(
                    cmd,
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env=env_vars
                )
                output += result.stdout + result.stderr
                exit_code = result.returncode
                self.state.last_exit_code = exit_code
                
                new_stage = self._determine_stage(output, exit_code)
                if exit_code == 0:
                    reward = 1.0
                    done = True
                elif new_stage > self.state.stage_reached:
                    reward = (new_stage - self.state.stage_reached) * 0.3
                    self.state.stage_reached = new_stage
                else:
                    reward = -0.05
                
            except subprocess.TimeoutExpired:
                output = "Error: Pipeline timed out"
                exit_code = 124
                reward = -0.2
            except Exception as e:
                output = str(e)
                exit_code = 1

        if self.state.step_count >= self.max_steps:
            done = True

        return self._get_observation(output, exit_code, reward, done)

    def _determine_stage(self, output: str, exit_code: int) -> int:
        score = 0
        if "Dependencies installed" in output or "pip install" in output:
            score = 1
        if "Tests passed" in output or "pytest" in output:
            score = 2
        if "Linting passed" in output or "flake8" in output or "Services healthy" in output:
            score = 3
        return score

    def _get_diff_summary(self) -> str:
        diffs = []
        for filename, original_content in self.state.original_files.items():
            path = os.path.join(self.workspace_root, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    current_content = f.read()
                if current_content != original_content:
                    diff = difflib.unified_diff(
                        original_content.splitlines(),
                        current_content.splitlines(),
                        fromfile=f"a/{filename}",
                        tofile=f"b/{filename}"
                    )
                    diffs.append("\n".join(diff))
        return "\n\n".join(diffs)

    def _get_observation(self, output: str, exit_code: int, reward: float, done: bool) -> Observation:
        files = []
        for root, dirs, filenames in os.walk(self.workspace_root):
            for f in filenames:
                rel_path = os.path.relpath(os.path.join(root, f), self.workspace_root)
                files.append(rel_path)
        
        metadata = {
            "GITHUB_RUN_ID": "12345",
            "GITHUB_REPOSITORY": "org/cicd-fixer",
            "NODE_ENV": "test",
            "RUNNER_OS": "Linux"
        }
        
        return Observation(
            terminal_output=output,
            exit_code=exit_code,
            files_in_directory=files,
            diff_summary=self._get_diff_summary(),
            reward=reward,
            done=done,
            metadata=metadata
        )

    def get_grader_score(self) -> float:
        progress = self.state.stage_reached / 3.0
        if self.state.last_exit_code == 0:
            progress = 1.0
            
        efficiency = 1.0
        if self.state.step_count > 5:
            efficiency = max(0.5, 1.0 - (self.state.step_count - 5) * 0.05)
            
        return round(progress * efficiency, 2)
    
    def get_state(self):
        return self.state

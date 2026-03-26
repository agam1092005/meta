from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class Action(BaseModel):
    tool: Literal["read_file", "write_file", "run_pipeline"] = Field(..., description="The tool to use")
    file_path: Optional[str] = Field(None, description="Path to the file for read/write")
    content: Optional[str] = Field(None, description="Content to write to the file")

class Observation(BaseModel):
    terminal_output: str = Field(..., description="The standard out/error from the tool")
    exit_code: int = Field(..., description="Exit code of the command (0 for success)")
    files_in_directory: List[str] = Field(..., description="List of files currently in the workspace")
    diff_summary: str = Field("", description="A unified diff of the changes made so far")
    reward: float = Field(..., description="The reward received for the last action")
    done: bool = Field(..., description="Whether the episode is finished")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Simulated GHA runner metadata")

class State(BaseModel):
    current_task_level: Literal["easy", "medium", "hard"]
    pipeline_runs: int
    step_count: int
    last_exit_code: int
    stage_reached: int  # 0: None, 1: Deps, 2: Tests, 3: Build/Deploy
    original_files: Dict[str, str] = Field(default_factory=dict)

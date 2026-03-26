import pytest
from models import Action

def test_anti_cheat(test_env):
    test_env.reset(task_level="easy")
    
    # Try to overwrite build.sh
    action = Action(tool="write_file", file_path="build.sh", content="echo 'cheating'")
    obs = test_env.step(action)
    
    assert "Permission denied" in obs.terminal_output
    assert obs.reward == -0.1
    assert obs.exit_code == 1

def test_directory_traversal(test_env):
    test_env.reset(task_level="easy")
    
    # Try to read environment.py
    action = Action(tool="read_file", file_path="../environment.py")
    obs = test_env.step(action)
    
    assert "Path traversal detected" in obs.terminal_output
    assert obs.reward == -0.5
    assert obs.exit_code == 1

def test_determine_stage(test_env):
    # Stage 1: Dependencies
    assert test_env._determine_stage("pip install flask", 0) == 1
    # Stage 2: Tests
    assert test_env._determine_stage("pytest test_app.py\nTests passed", 0) == 2
    # Stage 3: Linting
    assert test_env._determine_stage("flake8 app.py\nLinting passed", 0) == 3

def test_grader_efficiency(test_env):
    test_env.reset(task_level="easy")
    test_env.state.stage_reached = 3
    test_env.state.last_exit_code = 0
    
    # High efficiency (5 steps)
    test_env.state.step_count = 5
    assert test_env.get_grader_score() == 1.0
    
    # Lower efficiency (10 steps)
    test_env.state.step_count = 10
    # 1.0 - (10 - 5) * 0.05 = 0.75
    assert test_env.get_grader_score() == 0.75

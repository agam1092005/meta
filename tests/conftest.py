import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure the parent directory is in the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@pytest.fixture
def test_env():
    from cicd_pipeline_fixer.server.environment import PipelineEnvironment
    workspace = os.path.join(os.path.dirname(__file__), "test_workspace")
    templates = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server/templates")
    return PipelineEnvironment(workspace, templates)

@pytest.fixture
def api_client():
    from cicd_pipeline_fixer.server.app import app
    return TestClient(app)

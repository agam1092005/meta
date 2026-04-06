import pytest
import os
from unittest.mock import patch, MagicMock

# Skip if no API key is provided, or mock it for CI
@pytest.mark.skipif(not os.getenv("HF_TOKEN"), reason="Requires HF API Key")
def test_baseline_e2e(api_client):
    """
    Test the baseline endpoint which runs the OpenAI agent across tasks.
    """
    response = api_client.post("/baseline")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "baseline_completed"
    assert "scores" in data
    assert all(level in data["scores"] for level in ["easy", "medium", "hard"])

def test_mock_baseline_logic(monkeypatch):
    """
    Unit test for the baseline logic itself using a mock LLM.
    """
    # Set dummy API config for testing
    monkeypatch.setenv("HF_TOKEN", "hf-test-token")
    monkeypatch.setenv("API_BASE_URL", "http://test-url.com")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    
    from inference import get_action
    from models import Action
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"tool": "run_pipeline"}'
    
    with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
        action = get_action("Sample observation")
        assert action.tool == "run_pipeline"

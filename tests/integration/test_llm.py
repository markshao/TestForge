import pytest
import os
from forge.llm import create_llm, get_settings
from langchain_core.messages import HumanMessage

def test_llm_settings_load_env():
    """
    Test that settings are correctly loaded from .env file
    """
    settings = get_settings()
    
    # Check if key settings are loaded (values might come from .env)
    assert settings.openai_api_key is not None
    assert settings.openai_base_url is not None
    assert settings.openai_model_name is not None
    
    # Verify specific values if known from your .env content
    # Based on the user input, temperature is set to 0.5
    assert settings.openai_temperature == 0.5

@pytest.mark.asyncio
async def test_llm_api_call():
    """
    Test that the LLM can actually make a call to the API.
    This test requires a valid API key and connectivity.
    """
    llm = create_llm()
    
    # Simple test message
    message = HumanMessage(content="Hello, reply with 'pong'")
    
    try:
        response = await llm.ainvoke([message])
        assert response.content is not None
        print(f"LLM Response: {response.content}")
    except Exception as e:
        pytest.fail(f"LLM API call failed: {str(e)}")

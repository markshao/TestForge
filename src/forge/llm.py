from functools import lru_cache
from typing import Optional

from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """
    LLM Configuration settings.
    Reads from environment variables or .env file.
    Prefix: OPENAI_
    """
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model_name: str = "gpt-4-turbo"
    openai_temperature: float = 0.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> LLMSettings:
    """
    Get the cached LLM settings.
    """
    return LLMSettings()


def create_llm(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> ChatOpenAI:
    """
    Create a LangChain ChatOpenAI instance with the specified configuration.
    Falls back to environment variables/settings if parameters are not provided.

    Args:
        api_key: OpenAI API Key
        base_url: OpenAI Base URL
        model: Model name (e.g., gpt-4-turbo)
        temperature: Sampling temperature
        
    Returns:
        ChatOpenAI: Configured ChatOpenAI instance
    """
    settings = get_settings()
    
    # Use provided values or fall back to settings
    final_api_key = api_key or settings.openai_api_key
    final_base_url = base_url or settings.openai_base_url
    final_model = model or settings.openai_model_name
    final_temp = temperature if temperature is not None else settings.openai_temperature
    
    return ChatOpenAI(
        api_key=final_api_key,
        base_url=final_base_url,
        model=final_model,
        temperature=final_temp,
    )

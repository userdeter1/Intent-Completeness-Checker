from functools import lru_cache

from agno.models.base import Model
from agno.models.utils import get_model
from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables into os.environ so that SDKs can find API keys
load_dotenv()


class Settings(BaseSettings):
    llm_provider: str = "groq"
    llm_model_id: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        raise ValueError(
            "Configuration error. Please check your .env file or environment variables."
        ) from e


def resolve_model(provider: str | None = None, model_id: str | None = None) -> Model:
    """Returns an Agno Model instance matching the requested provider and model_id.

    If provider or model_id are not provided, falls back to values defined in Settings.
    Raises ValueError if the provider is unsupported by Agno.
    """
    settings = get_settings()
    chosen_provider = provider or settings.llm_provider
    actual_model_id = model_id or settings.llm_model_id

    model_string = f"{chosen_provider}:{actual_model_id}"
    try:
        return get_model(model_string)
    except Exception as e:
        error_msg = str(e)
        if "not installed" in error_msg.lower():
            raise ValueError(
                f"Failed to resolve model '{model_string}'. "
                f"The required SDK is not installed. "
                f"Original error: {error_msg}"
            ) from e
        raise ValueError(
            f"Failed to resolve model '{model_string}'. "
            "Make sure the provider exists in Agno "
            "(e.g., openai, anthropic, groq, mistral). "
            f"Original error: {error_msg}"
        ) from e

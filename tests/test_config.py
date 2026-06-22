import pytest

from intentcheck.config import resolve_model


def test_resolve_model_default(monkeypatch):
    # Ensure no environment variables interfere
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)

    # "groq" is the default provider and "llama-3.3-70b-versatile" is the default model
    model = resolve_model()
    assert model.id == "llama-3.3-70b-versatile"
    # Agno's internal get_model returns the specific Groq model class
    assert model.__class__.__name__ == "Groq"


def test_resolve_model_explicit_valid():
    # Should resolve groq successfully with a different model
    model = resolve_model(provider="groq", model_id="llama3-8b-8192")
    assert model.id == "llama3-8b-8192"
    assert model.__class__.__name__ == "Groq"


def test_resolve_model_invalid_provider():
    with pytest.raises(ValueError) as excinfo:
        resolve_model(provider="not-a-real-provider", model_id="gpt-4o")

    error_msg = str(excinfo.value)
    assert "Failed to resolve model 'not-a-real-provider:gpt-4o'" in error_msg
    assert "Make sure the provider exists in Agno" in error_msg

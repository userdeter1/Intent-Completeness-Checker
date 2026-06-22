from unittest.mock import MagicMock, patch

from intentcheck.agents.investigator import (
    _ensure_unique_assertion_ids,
    investigate_intent,
)
from intentcheck.core.models import Assertion, Intent, InvestigatorOutput


@patch("intentcheck.agents.investigator.Agent")
@patch("intentcheck.agents.investigator.resolve_model")
def test_investigate_intent(mock_resolve_model, mock_agent_class):
    mock_model = MagicMock()
    mock_resolve_model.return_value = mock_model

    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_response = MagicMock()
    mock_content = InvestigatorOutput(
        intent=Intent(
            text="renomme GROQ_API_KEY en GROQ_KEY partout", source="user_provided"
        ),
        assertions=[
            Assertion(
                id="A1",
                description="GROQ_API_KEY doit être absent du code",
                assertion_type="textual_absence",
            ),
            Assertion(
                id="A2",
                description="GROQ_KEY doit être présent dans le code",
                assertion_type="textual_presence",
            ),
        ],
    )
    mock_response.content = mock_content
    mock_agent_instance.run.return_value = mock_response

    intent = Intent(
        text="renomme GROQ_API_KEY en GROQ_KEY partout", source="user_provided"
    )
    output = investigate_intent(intent)

    mock_agent_instance.run.assert_called_once()
    assert len(output.assertions) == 2
    assert output.assertions[0].id == "A1"
    assert output.assertions[1].id == "A2"
    assert output.intent.text == "renomme GROQ_API_KEY en GROQ_KEY partout"


def test_ensure_unique_ids_fixes_duplicate_ids():
    """When the LLM produces two assertions with the same ID, all IDs should be
    reassigned to a deterministic sequential scheme (A1, A2, ...)."""
    output = InvestigatorOutput(
        intent=Intent(text="test", source="user_provided"),
        assertions=[
            Assertion(
                id="same-id",
                description="First assertion",
                assertion_type="textual_absence",
            ),
            Assertion(
                id="same-id",
                description="Second assertion",
                assertion_type="textual_presence",
            ),
            Assertion(
                id="unique-id",
                description="Third assertion",
                assertion_type="logical_consistency",
            ),
        ],
    )

    fixed = _ensure_unique_assertion_ids(output)

    ids = [a.id for a in fixed.assertions]
    assert ids == ["A1", "A2", "A3"]
    # Verify all IDs are now unique
    assert len(set(ids)) == len(ids)


def test_ensure_unique_ids_fixes_empty_ids():
    """When the LLM produces an assertion with an empty or whitespace-only ID,
    all IDs should be reassigned to a deterministic sequential scheme."""
    output = InvestigatorOutput(
        intent=Intent(text="test", source="user_provided"),
        assertions=[
            Assertion(
                id="",
                description="Empty ID assertion",
                assertion_type="textual_absence",
            ),
            Assertion(
                id="A1",
                description="Normal assertion",
                assertion_type="textual_presence",
            ),
        ],
    )

    fixed = _ensure_unique_assertion_ids(output)

    ids = [a.id for a in fixed.assertions]
    assert ids == ["A1", "A2"]
    assert len(set(ids)) == len(ids)


def test_ensure_unique_ids_preserves_already_unique_ids():
    """When all IDs are already unique and non-empty, no changes should be made."""
    output = InvestigatorOutput(
        intent=Intent(text="test", source="user_provided"),
        assertions=[
            Assertion(
                id="check-api-key",
                description="Check API key",
                assertion_type="textual_absence",
            ),
            Assertion(
                id="verify-config",
                description="Verify config",
                assertion_type="textual_presence",
            ),
        ],
    )

    fixed = _ensure_unique_assertion_ids(output)

    # Original IDs should be preserved untouched
    assert fixed.assertions[0].id == "check-api-key"
    assert fixed.assertions[1].id == "verify-config"

@patch('intentcheck.agents.investigator.Agent')
@patch('intentcheck.agents.investigator.resolve_model')
def test_investigate_intent_retry_success(mock_resolve_model, mock_agent_class):
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_response = MagicMock()
    mock_content = InvestigatorOutput(
        intent=Intent(text='test', source='user_provided'),
        assertions=[],
    )
    mock_response.content = mock_content

    # Simulate a failure on the first call, success on the second
    mock_agent_instance.run = MagicMock(
        side_effect=[Exception('tool_use_failed'), mock_response]
    )

    intent = Intent(text='test', source='user_provided')
    output = investigate_intent(intent)

    assert mock_agent_instance.run.call_count == 2
    assert output.intent.text == 'test'

@patch('intentcheck.agents.investigator.Agent')
@patch('intentcheck.agents.investigator.resolve_model')
def test_investigate_intent_retry_failure(mock_resolve_model, mock_agent_class):
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    # Simulate persistent failure
    mock_agent_instance.run = MagicMock(side_effect=Exception('persistent failure'))

    intent = Intent(text='test', source='user_provided')

    import pytest
    with pytest.raises(ValueError, match='Investigator failed after 3 attempts'):
        investigate_intent(intent)

    assert mock_agent_instance.run.call_count == 3

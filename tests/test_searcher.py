from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from intentcheck.agents.searcher import run_searcher
from intentcheck.core.models import Assertion, Evidence, SearcherOutput


@pytest.mark.asyncio
@patch("intentcheck.agents.searcher.Agent")
@patch("intentcheck.agents.searcher.resolve_model")
async def test_run_searcher(mock_resolve_model, mock_agent_class):
    mock_model = MagicMock()
    mock_resolve_model.return_value = mock_model

    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_response = MagicMock()
    mock_content = SearcherOutput(
        assertion_id="A1",
        evidence=[
            Evidence(
                file_path="config.py",
                line_number=1,
                snippet="API_KEY='secret'",
                relevance_note="Found API_KEY",
            )
        ],
        confidence="high",
    )
    mock_response.content = mock_content
    # Since agent.arun is an async function, we need to mock it as an
    # AsyncMock or set the return value to a coroutine
    mock_agent_instance.arun = AsyncMock(return_value=mock_response)

    assertion = Assertion(
        id="A1",
        description="GROQ_API_KEY doit être absent",
        assertion_type="textual_absence",
    )

    output = await run_searcher(assertion, "/fake/repo")

    mock_agent_instance.arun.assert_called_once()
    assert len(output.evidence) == 1
    assert output.evidence[0].file_path == "config.py"
    assert output.assertion_id == "A1"
    assert output.confidence == "high"


@pytest.mark.asyncio
@patch("intentcheck.agents.searcher.Agent")
@patch("intentcheck.agents.searcher.resolve_model")
async def test_run_searcher_retry_success(mock_resolve_model, mock_agent_class):
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_response = MagicMock()
    mock_content = SearcherOutput(
        assertion_id="A1",
        evidence=[],
        confidence="low",
    )
    mock_response.content = mock_content

    mock_agent_instance.arun = AsyncMock(
        side_effect=[Exception("tool_use_failed"), mock_response]
    )

    assertion = Assertion(
        id="A1",
        description="test",
        assertion_type="textual_absence",
    )

    output = await run_searcher(assertion, "/fake/repo")

    assert mock_agent_instance.arun.call_count == 2
    assert output.assertion_id == "A1"


@pytest.mark.asyncio
@patch("intentcheck.agents.searcher.Agent")
@patch("intentcheck.agents.searcher.resolve_model")
async def test_run_searcher_retry_failure(mock_resolve_model, mock_agent_class):
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_agent_instance.arun = AsyncMock(side_effect=Exception("persistent failure"))

    assertion = Assertion(
        id="A1",
        description="test",
        assertion_type="textual_absence",
    )

    with pytest.raises(ValueError, match="Searcher failed after 3 attempts"):
        await run_searcher(assertion, "/fake/repo")

    assert mock_agent_instance.arun.call_count == 3

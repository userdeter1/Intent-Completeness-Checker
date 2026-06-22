from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from intentcheck.agents.judge import run_judge
from intentcheck.core.models import (
    Assertion,
    Evidence,
    JudgeVerdict,
    SearcherOutput,
)


@pytest.mark.asyncio
@patch("intentcheck.agents.judge.Agent")
@patch("intentcheck.agents.judge.resolve_model")
async def test_run_judge(mock_resolve_model, mock_agent_class):
    mock_model = MagicMock()
    mock_resolve_model.return_value = mock_model

    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_response = MagicMock()
    mock_content = JudgeVerdict(
        assertion_id="A1",
        verdict="satisfied",
        reasoning="Because of evidence",
        confirmed_evidence=[
            Evidence(
                file_path="config.py",
                line_number=1,
                snippet="API_KEY='secret'",
                relevance_note="Found API_KEY",
            )
        ],
        dismissed_evidence=[],
    )
    mock_response.content = mock_content
    mock_agent_instance.arun = AsyncMock(return_value=mock_response)

    assertion = Assertion(
        id="A1",
        description="GROQ_API_KEY doit être absent",
        assertion_type="textual_absence",
    )

    searcher_output = SearcherOutput(
        assertion_id="A1",
        evidence=[],
        confidence="low",
    )

    output = await run_judge(assertion, searcher_output, "/fake/repo")

    mock_agent_instance.arun.assert_called_once()
    assert output.verdict == "satisfied"
    assert output.assertion_id == "A1"
    assert len(output.confirmed_evidence) == 1
    assert len(output.dismissed_evidence) == 0


@pytest.mark.asyncio
@patch("intentcheck.agents.judge.Agent")
@patch("intentcheck.agents.judge.resolve_model")
async def test_run_judge_retry_success(mock_resolve_model, mock_agent_class):
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_response = MagicMock()
    mock_content = JudgeVerdict(
        assertion_id="A1",
        verdict="uncertain",
        reasoning="test",
        confirmed_evidence=[],
        dismissed_evidence=[],
    )
    mock_response.content = mock_content

    mock_agent_instance.arun = AsyncMock(
        side_effect=[Exception("tool_use_failed"), mock_response]
    )

    assertion = Assertion(id="A1", description="test", assertion_type="textual_absence")
    searcher_output = SearcherOutput(assertion_id="A1", evidence=[], confidence="low")

    output = await run_judge(assertion, searcher_output, "/fake/repo")

    assert mock_agent_instance.arun.call_count == 2
    assert output.verdict == "uncertain"


@pytest.mark.asyncio
@patch("intentcheck.agents.judge.Agent")
@patch("intentcheck.agents.judge.resolve_model")
async def test_run_judge_retry_failure(mock_resolve_model, mock_agent_class):
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    mock_agent_instance.arun = AsyncMock(side_effect=Exception("persistent failure"))

    assertion = Assertion(id="A1", description="test", assertion_type="textual_absence")
    searcher_output = SearcherOutput(assertion_id="A1", evidence=[], confidence="low")

    with pytest.raises(ValueError, match="Judge failed after 3 attempts"):
        await run_judge(assertion, searcher_output, "/fake/repo")

    assert mock_agent_instance.arun.call_count == 3

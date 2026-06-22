from pathlib import Path
from unittest.mock import patch

import pytest

from intentcheck.core.models import (
    Assertion,
    Intent,
    IntentCheckResult,
    InvestigatorOutput,
    JudgeVerdict,
    SearcherOutput,
)
from intentcheck.core.orchestrator import run_pipeline


@pytest.fixture
def mock_investigator_output():
    return InvestigatorOutput(
        intent=Intent(text="Fix typo", source="user_provided"),
        assertions=[
            Assertion(
                id="A1",
                description="Assertion 1",
                assertion_type="textual_absence",
            ),
            Assertion(
                id="A2",
                description="Assertion 2",
                assertion_type="textual_presence",
            ),
            Assertion(
                id="A3",
                description="Assertion 3",
                assertion_type="logical_consistency",
            ),
        ],
    )


@pytest.fixture
def mock_searcher_output():
    return SearcherOutput(
        assertion_id="A1",
        evidence=[],
        confidence="high",
    )


@pytest.fixture
def mock_judge_verdict():
    return JudgeVerdict(
        assertion_id="A1",
        verdict="satisfied",
        reasoning="Good enough",
        confirmed_evidence=[],
        dismissed_evidence=[],
    )


@pytest.mark.asyncio
@patch("intentcheck.core.orchestrator.investigate_intent")
@patch("intentcheck.core.orchestrator.run_searcher")
@patch("intentcheck.core.orchestrator.run_judge")
async def test_run_pipeline_success(
    mock_run_judge,
    mock_run_searcher,
    mock_investigate_intent,
    mock_investigator_output,
    mock_searcher_output,
    mock_judge_verdict,
):
    # Setup mocks
    mock_investigate_intent.return_value = mock_investigator_output
    mock_run_searcher.return_value = mock_searcher_output

    # We need to return different judge verdicts with correct IDs
    def mock_judge_side_effect(assertion, *args, **kwargs):
        return JudgeVerdict(
            assertion_id=assertion.id,
            verdict="satisfied",
            reasoning="Test",
            confirmed_evidence=[],
            dismissed_evidence=[],
        )

    mock_run_judge.side_effect = mock_judge_side_effect

    result = await run_pipeline("Fix typo", Path("."))

    assert isinstance(result, IntentCheckResult)
    assert len(result.verdicts) == 3
    assert len(result.errors) == 0
    assert result.intent.text == "Fix typo"
    assert result.intent.source == "user_provided"

    # Verify calls
    mock_investigate_intent.assert_called_once()
    assert mock_run_searcher.call_count == 3
    assert mock_run_judge.call_count == 3


@pytest.mark.asyncio
@patch("intentcheck.core.orchestrator.investigate_intent")
@patch("intentcheck.core.orchestrator.run_searcher")
@patch("intentcheck.core.orchestrator.run_judge")
async def test_run_pipeline_with_errors(
    mock_run_judge,
    mock_run_searcher,
    mock_investigate_intent,
    mock_investigator_output,
    mock_searcher_output,
):
    mock_investigate_intent.return_value = mock_investigator_output
    mock_run_searcher.return_value = mock_searcher_output

    # Simulate an error on the second assertion
    def mock_judge_side_effect(assertion, *args, **kwargs):
        if assertion.id == "A2":
            raise ValueError("Something went wrong with A2")
        return JudgeVerdict(
            assertion_id=assertion.id,
            verdict="satisfied",
            reasoning="Test",
            confirmed_evidence=[],
            dismissed_evidence=[],
        )

    mock_run_judge.side_effect = mock_judge_side_effect

    result = await run_pipeline("Fix typo", Path("."))

    assert isinstance(result, IntentCheckResult)
    assert len(result.verdicts) == 2
    assert len(result.errors) == 1

    error = result.errors[0]
    assert error.assertion_id == "A2"
    assert "ValueError: Something went wrong with A2" in error.error_message


@pytest.mark.asyncio
@patch("intentcheck.core.orchestrator.get_current_diff")
@patch("intentcheck.core.orchestrator.investigate_intent")
@patch("intentcheck.core.orchestrator.run_searcher")
@patch("intentcheck.core.orchestrator.run_judge")
async def test_run_pipeline_no_intent_text(
    mock_run_judge,
    mock_run_searcher,
    mock_investigate_intent,
    mock_get_current_diff,
    mock_investigator_output,
    mock_searcher_output,
):
    mock_get_current_diff.return_value = "diff --git a/file b/file"
    mock_investigate_intent.return_value = mock_investigator_output
    mock_run_searcher.return_value = mock_searcher_output

    def mock_judge_side_effect(assertion, *args, **kwargs):
        return JudgeVerdict(
            assertion_id=assertion.id,
            verdict="satisfied",
            reasoning="Test",
            confirmed_evidence=[],
            dismissed_evidence=[],
        )

    mock_run_judge.side_effect = mock_judge_side_effect

    result = await run_pipeline(None, Path("."))

    assert isinstance(result, IntentCheckResult)
    assert result.intent.source == "inferred_from_diff"
    assert result.intent.text == "diff --git a/file b/file"

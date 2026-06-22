"""Tests for the CLI."""

import json
from unittest.mock import patch

from typer.testing import CliRunner

from intentcheck.cli import app
from intentcheck.core.models import (
    Assertion,
    Evidence,
    Intent,
    IntentCheckResult,
    JudgeVerdict,
)

runner = CliRunner()


@patch("intentcheck.cli.run_pipeline")
def test_investigate_json_output_does_not_corrupt_brackets(mock_run_pipeline) -> None:
    """Ensure that the --json flag does not pass output through Rich markup,
    which corrupts square brackets like list[str].
    """
    intent = Intent(text="Test intent", source="user_provided")
    assertion = Assertion(
        id="A1", description="desc", assertion_type="textual_presence"
    )
    evidence = Evidence(
        file_path="foo.py",
        line_number=10,
        snippet="def foo(items: list[str]) -> list[int]:",
        relevance_note="It uses list[str]",
    )
    verdict = JudgeVerdict(
        assertion_id="A1",
        verdict="satisfied",
        reasoning="Because of list[str] and dict[str, Any]",
        confirmed_evidence=[evidence],
        dismissed_evidence=[],
    )
    fake_result = IntentCheckResult(
        intent=intent,
        assertions=[assertion],
        verdicts=[verdict],
        errors=[],
    )

    async def fake_run_pipeline(*args, **kwargs):
        return fake_result

    mock_run_pipeline.side_effect = fake_run_pipeline

    result = runner.invoke(app, ["--intent", "test", "--full-pipeline", "--json"])
    assert result.exit_code == 0

    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        assert False, f"Failed to parse JSON output: {result.stdout}"

    entry = parsed["results"][0]
    assert entry["reasoning"] == "Because of list[str] and dict[str, Any]"
    assert entry["confirmed_evidence"][0]["snippet"] == (
        "def foo(items: list[str]) -> list[int]:"
    )
    assert entry["confirmed_evidence"][0]["relevance_note"] == "It uses list[str]"

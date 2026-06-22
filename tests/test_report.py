"""Tests for intentcheck.core.report."""

from rich.console import Console

from intentcheck.core.models import (
    Assertion,
    AssertionErrorModel,
    DismissedEvidence,
    Evidence,
    Intent,
    IntentCheckResult,
    JudgeVerdict,
)
from intentcheck.core.report import (
    build_json_report,
    compute_overall_verdict,
    render_terminal_report,
)

# ── Fixtures / helpers ─────────────────────────────────────────────────


def _make_result(
    verdict_values: list[str],
    *,
    errors: list[AssertionErrorModel] | None = None,
    dismissed: bool = False,
) -> IntentCheckResult:
    """Build a minimal IntentCheckResult with the given verdict strings.

    If *dismissed* is True, the first verdict will carry dismissed
    evidence so we can exercise that rendering path.
    """
    intent = Intent(text="Ensure no secret is leaked", source="user_provided")
    assertions = [
        Assertion(
            id=f"A{i + 1}",
            description=f"Assertion {i + 1}",
            assertion_type="textual_absence",
        )
        for i in range(len(verdict_values))
    ]
    verdicts: list[JudgeVerdict] = []
    for i, v in enumerate(verdict_values):
        dismissed_evidence: list[DismissedEvidence] = []
        confirmed: list[Evidence] = []

        if i == 0 and dismissed:
            dismissed_evidence = [
                DismissedEvidence(
                    file_path="old_config.py",
                    line_number=102,
                    snippet="API_KEY = 'old_value'",
                    relevance_note="Looks like an API key",
                    dismissal_reason="File is no longer imported; dead code.",
                )
            ]

        if v == "violated":
            confirmed = [
                Evidence(
                    file_path="config.py",
                    line_number=8,
                    snippet="GROQ_API_KEY = 'sk-xxx'",
                    relevance_note="Hard-coded secret found.",
                )
            ]

        verdicts.append(
            JudgeVerdict(
                assertion_id=f"A{i + 1}",
                verdict=v,
                reasoning=f"Reasoning for A{i + 1}",
                confirmed_evidence=confirmed,
                dismissed_evidence=dismissed_evidence,
            )
        )

    return IntentCheckResult(
        intent=intent,
        assertions=assertions,
        verdicts=verdicts,
        errors=errors or [],
    )


# ── compute_overall_verdict ────────────────────────────────────────────


class TestComputeOverallVerdict:
    def test_all_satisfied(self) -> None:
        result = _make_result(["satisfied", "satisfied", "satisfied"])
        assert compute_overall_verdict(result) == "complete"

    def test_one_violated(self) -> None:
        result = _make_result(["satisfied", "violated", "satisfied"])
        assert compute_overall_verdict(result) == "incomplete"

    def test_multiple_violated(self) -> None:
        result = _make_result(["violated", "violated"])
        assert compute_overall_verdict(result) == "incomplete"

    def test_uncertain_no_violated(self) -> None:
        result = _make_result(["satisfied", "uncertain"])
        assert compute_overall_verdict(result) == "uncertain"

    def test_uncertain_and_violated(self) -> None:
        """violated takes precedence over uncertain."""
        result = _make_result(["violated", "uncertain", "satisfied"])
        assert compute_overall_verdict(result) == "incomplete"

    def test_empty_verdicts(self) -> None:
        """No verdicts at all → nothing violated → complete."""
        result = _make_result([])
        assert compute_overall_verdict(result) == "complete"

    def test_only_uncertain(self) -> None:
        result = _make_result(["uncertain", "uncertain"])
        assert compute_overall_verdict(result) == "uncertain"


# ── build_json_report ──────────────────────────────────────────────────


class TestBuildJsonReport:
    def test_structure_keys(self) -> None:
        result = _make_result(["satisfied", "violated"])
        report = build_json_report(result)

        assert "intent" in report
        assert "summary" in report
        assert "verdict" in report
        assert "results" in report
        assert "errors" in report

    def test_summary_counts(self) -> None:
        result = _make_result(
            ["satisfied", "violated", "uncertain"],
            errors=[AssertionErrorModel(assertion_id="A4", error_message="Timeout")],
        )
        # Add the assertion corresponding to the error so total_assertions
        # is consistent.
        result.assertions.append(
            Assertion(
                id="A4",
                description="Assertion 4",
                assertion_type="textual_presence",
            )
        )

        report = build_json_report(result)
        summary = report["summary"]

        assert summary["total_assertions"] == 4
        assert summary["satisfied"] == 1
        assert summary["violated"] == 1
        assert summary["uncertain"] == 1
        assert summary["errors"] == 1

    def test_verdict_incomplete(self) -> None:
        result = _make_result(["satisfied", "violated"])
        report = build_json_report(result)
        assert report["verdict"] == "incomplete"

    def test_verdict_complete(self) -> None:
        result = _make_result(["satisfied", "satisfied"])
        report = build_json_report(result)
        assert report["verdict"] == "complete"

    def test_verdict_uncertain(self) -> None:
        result = _make_result(["satisfied", "uncertain"])
        report = build_json_report(result)
        assert report["verdict"] == "uncertain"

    def test_per_assertion_detail(self) -> None:
        result = _make_result(["violated"], dismissed=True)
        report = build_json_report(result)

        assert len(report["results"]) == 1
        entry = report["results"][0]
        assert entry["assertion_id"] == "A1"
        assert entry["verdict"] == "violated"
        assert entry["reasoning"] == "Reasoning for A1"
        assert len(entry["confirmed_evidence"]) == 1
        assert entry["confirmed_evidence"][0]["file_path"] == "config.py"

    def test_dismissed_evidence_in_json(self) -> None:
        result = _make_result(["satisfied"], dismissed=True)
        report = build_json_report(result)

        dismissed = report["results"][0]["dismissed_evidence"]
        assert len(dismissed) == 1
        assert "dismissal_reason" in dismissed[0]
        assert dismissed[0]["file_path"] == "old_config.py"

    def test_errors_section(self) -> None:
        result = _make_result(
            ["satisfied"],
            errors=[
                AssertionErrorModel(assertion_id="A2", error_message="LLM timeout")
            ],
        )
        report = build_json_report(result)
        assert len(report["errors"]) == 1
        assert report["errors"][0]["assertion_id"] == "A2"
        assert report["errors"][0]["error_message"] == "LLM timeout"


# ── render_terminal_report ─────────────────────────────────────────────


class TestRenderTerminalReport:
    """We don't assert on visual output, but we ensure no exceptions are
    raised for every combination of verdict categories."""

    def test_all_satisfied(self) -> None:
        result = _make_result(["satisfied", "satisfied"])
        console = Console(file=None, force_terminal=True, width=120)
        render_terminal_report(result, console)  # should not raise

    def test_all_violated(self) -> None:
        result = _make_result(["violated", "violated"])
        console = Console(file=None, force_terminal=True, width=120)
        render_terminal_report(result, console)

    def test_mixed_verdicts(self) -> None:
        result = _make_result(["satisfied", "violated", "uncertain"])
        console = Console(file=None, force_terminal=True, width=120)
        render_terminal_report(result, console)

    def test_with_dismissed_evidence(self) -> None:
        result = _make_result(["satisfied", "violated"], dismissed=True)
        console = Console(file=None, force_terminal=True, width=120)
        render_terminal_report(result, console)

    def test_with_errors(self) -> None:
        result = _make_result(
            ["satisfied"],
            errors=[
                AssertionErrorModel(
                    assertion_id="A2", error_message="Connection refused"
                )
            ],
        )
        console = Console(file=None, force_terminal=True, width=120)
        render_terminal_report(result, console)

    def test_empty_result(self) -> None:
        """Edge case: no assertions at all."""
        result = _make_result([])
        console = Console(file=None, force_terminal=True, width=120)
        render_terminal_report(result, console)

    def test_long_intent_truncated(self) -> None:
        """Intents longer than 200 chars should not break rendering."""
        result = _make_result(["satisfied"])
        result.intent = Intent(text="x" * 500, source="inferred_from_diff")
        console = Console(file=None, force_terminal=True, width=120)
        render_terminal_report(result, console)

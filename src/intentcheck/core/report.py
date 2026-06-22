"""Final report rendering for the intent completeness pipeline.

Provides three public functions:
- compute_overall_verdict: derives a single global verdict from all assertion
  verdicts and errors.
- build_json_report: serialises an IntentCheckResult into a dict ready for
  json.dumps().
- render_terminal_report: pretty-prints a full human report using Rich panels,
  tables, and colour-coded sections.
"""

from typing import Any, Literal

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from intentcheck.core.models import Assertion, IntentCheckResult

# ── verdict logic ──────────────────────────────────────────────────────


def compute_overall_verdict(
    result: IntentCheckResult,
) -> Literal["complete", "incomplete", "uncertain"]:
    """Determine the global verdict from all per-assertion verdicts.

    Rules (applied in order):
    1. Any ``"violated"`` verdict → ``"incomplete"``.
    2. No violations but at least one ``"uncertain"`` → ``"uncertain"``.
    3. All assertions satisfied (and no errors that would reduce verdict
       count) → ``"complete"``.
    """
    verdicts = [v.verdict for v in result.verdicts]

    if "violated" in verdicts:
        return "incomplete"
    if "uncertain" in verdicts:
        return "uncertain"
    return "complete"


# ── JSON report ────────────────────────────────────────────────────────


def build_json_report(result: IntentCheckResult) -> dict[str, Any]:
    """Build a JSON-serialisable dict from an *IntentCheckResult*.

    The structure is designed for direct consumption by CI tools:
    a top-level ``summary`` gives counts at a glance, ``verdict`` is a
    single string, and ``results`` holds per-assertion detail including
    confirmed and dismissed evidence.
    """
    verdicts_list = [v.verdict for v in result.verdicts]
    overall = compute_overall_verdict(result)

    summary = {
        "total_assertions": len(result.assertions),
        "satisfied": verdicts_list.count("satisfied"),
        "violated": verdicts_list.count("violated"),
        "uncertain": verdicts_list.count("uncertain"),
        "errors": len(result.errors),
    }

    # Build a lookup from assertion id → assertion for descriptions.
    assertion_map = {a.id: a for a in result.assertions}

    per_assertion: list[dict[str, Any]] = []
    for v in result.verdicts:
        assertion = assertion_map.get(v.assertion_id)
        per_assertion.append(
            {
                "assertion_id": v.assertion_id,
                "assertion_description": assertion.description if assertion else "",
                "verdict": v.verdict,
                "reasoning": v.reasoning,
                "confirmed_evidence": [
                    {
                        "file_path": e.file_path,
                        "line_number": e.line_number,
                        "snippet": e.snippet,
                        "relevance_note": e.relevance_note,
                    }
                    for e in v.confirmed_evidence
                ],
                "dismissed_evidence": [
                    {
                        "file_path": e.file_path,
                        "line_number": e.line_number,
                        "snippet": e.snippet,
                        "dismissal_reason": e.dismissal_reason,
                    }
                    for e in v.dismissed_evidence
                ],
            }
        )

    errors_section: list[dict[str, str]] = [
        {"assertion_id": e.assertion_id, "error_message": e.error_message}
        for e in result.errors
    ]

    return {
        "intent": result.intent.text,
        "summary": summary,
        "verdict": overall,
        "results": per_assertion,
        "errors": errors_section,
    }


# ── Rich terminal report ──────────────────────────────────────────────
#
# Design choices:
# • Rich *Panel* for the header and the final verdict — these are the
#   first and last things the user sees; a bordered panel gives them
#   visual weight.
# • Rich *Table* for per-assertion detail — tabular data is the most
#   scannable format when there are several assertions.
# • Separate sections (panels or tables) for satisfied / violated /
#   uncertain / dismissed / errors so that the user can jump to the
#   category they care about.
# • Colour palette: green (#00d787) for satisfied, red (#ff5555) for
#   violated, yellow (#ffaf00) for uncertain, dim grey for dismissed
#   evidence.

_STYLE_SATISFIED = "bold green"
_STYLE_VIOLATED = "bold red"
_STYLE_UNCERTAIN = "bold yellow"
_STYLE_DISMISSED = "dim"
_STYLE_ERROR = "bold red"


def render_terminal_report(result: IntentCheckResult, console: Console) -> None:
    """Render a full human-readable report to *console*."""

    assertion_map = {a.id: a for a in result.assertions}

    # ── 1. Header ──────────────────────────────────────────────────────
    intent_text = result.intent.text
    # Truncate very long diffs for the header display (show first 200
    # chars with an ellipsis).
    if len(intent_text) > 200:
        intent_text = intent_text[:200] + "…"

    console.print()
    console.print(
        Panel(
            f"[bold]Intent:[/] {intent_text}",
            title="🔍 Intent Completeness Report",
            border_style="bright_blue",
            expand=True,
        )
    )

    # Partition verdicts by category.
    satisfied = [v for v in result.verdicts if v.verdict == "satisfied"]
    violated = [v for v in result.verdicts if v.verdict == "violated"]
    uncertain = [v for v in result.verdicts if v.verdict == "uncertain"]

    # ── 2. Satisfied assertions ────────────────────────────────────────
    if satisfied:
        table = Table(
            title="✅ Assertions satisfied",
            show_lines=True,
            title_style=_STYLE_SATISFIED,
            border_style="green",
        )
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Reasoning")

        for v in satisfied:
            desc = _get_desc(assertion_map, v.assertion_id)
            table.add_row(v.assertion_id, desc, v.reasoning)

        console.print()
        console.print(table)

    # ── 3. Violated assertions ─────────────────────────────────────────
    if violated:
        table = Table(
            title="❌ Assertions violated",
            show_lines=True,
            title_style=_STYLE_VIOLATED,
            border_style="red",
        )
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Description", style="red")
        table.add_column("Verdict", style=_STYLE_VIOLATED)
        table.add_column("Reasoning")
        table.add_column("Evidence", min_width=30)

        for v in violated:
            desc = _get_desc(assertion_map, v.assertion_id)
            evidence_lines: list[str] = []
            for e in v.confirmed_evidence:
                evidence_lines.append(
                    f"[bold]{e.file_path}[/]"
                    f"{':' + str(e.line_number) if e.line_number is not None else ''}  "
                    f"[dim]{_truncate(e.snippet, 80)}[/]\n"
                    f"  ↳ {e.relevance_note}"
                )
            evidence_text = (
                "\n\n".join(evidence_lines) if evidence_lines else "[dim]No evidence[/]"
            )
            table.add_row(
                v.assertion_id,
                desc,
                "VIOLATED",
                v.reasoning,
                evidence_text,
            )

        console.print()
        console.print(table)

    # ── 4. Uncertain assertions ────────────────────────────────────────
    if uncertain:
        table = Table(
            title="⚠️  Assertions uncertain",
            show_lines=True,
            title_style=_STYLE_UNCERTAIN,
            border_style="yellow",
        )
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Description", style="yellow")
        table.add_column("Reasoning")
        table.add_column("Evidence", min_width=30)

        for v in uncertain:
            desc = _get_desc(assertion_map, v.assertion_id)
            evidence_lines: list[str] = []
            for e in v.confirmed_evidence:
                evidence_lines.append(
                    f"[bold]{e.file_path}[/]"
                    f"{':' + str(e.line_number) if e.line_number is not None else ''}  "
                    f"[dim]{_truncate(e.snippet, 80)}[/]\n"
                    f"  ↳ {e.relevance_note}"
                )
            evidence_text = (
                "\n\n".join(evidence_lines) if evidence_lines else "[dim]No evidence[/]"
            )
            table.add_row(
                v.assertion_id,
                desc,
                v.reasoning,
                evidence_text,
            )

        console.print()
        console.print(table)

    # ── 5. Dismissed evidence (false positives) ────────────────────────
    all_dismissed = [(v, d) for v in result.verdicts for d in v.dismissed_evidence]

    console.print()
    if all_dismissed:
        table = Table(
            title="🔇 Dismissed evidence (false positives)",
            show_lines=True,
            title_style=_STYLE_DISMISSED,
            border_style="dim",
        )
        table.add_column("Assertion", justify="center", style="cyan", no_wrap=True)
        table.add_column("File", style="dim")
        table.add_column("Line", justify="right", style="dim")
        table.add_column("Snippet", style="dim")
        table.add_column("Reason for dismissal", style="dim italic")

        for v, d in all_dismissed:
            table.add_row(
                v.assertion_id,
                d.file_path,
                str(d.line_number) if d.line_number is not None else "N/A",
                _truncate(d.snippet, 60),
                d.dismissal_reason,
            )

        console.print(table)
    else:
        console.print("[dim]No dismissed evidence (false positives).[/]")

    # ── 6. Technical errors ────────────────────────────────────────────
    if result.errors:
        console.print()
        table = Table(
            title="🛑 Technical errors",
            show_lines=True,
            title_style=_STYLE_ERROR,
            border_style="red",
        )
        table.add_column("Assertion ID", style="cyan")
        table.add_column("Error", style="red")

        for err in result.errors:
            table.add_row(err.assertion_id, err.error_message)

        console.print(table)

    # ── 7. Global verdict banner ───────────────────────────────────────
    overall = compute_overall_verdict(result)
    n_satisfied = len(satisfied)
    n_violated = len(violated)
    n_uncertain = len(uncertain)
    n_errors = len(result.errors)

    counts = (
        f"[green]{n_satisfied} satisfied[/]  •  "
        f"[red]{n_violated} violated[/]  •  "
        f"[yellow]{n_uncertain} uncertain[/]  •  "
        f"[red]{n_errors} error(s)[/]"
    )

    if overall == "complete":
        banner_text = Text("✅ Intention complètement appliquée", style="bold green")
        border = "green"
    elif overall == "incomplete":
        banner_text = Text(
            f"❌ {n_violated} problème(s) bloquant(s) détecté(s)",
            style="bold red",
        )
        border = "red"
    else:  # uncertain
        banner_text = Text(
            "⚠️  Aucune violation, mais des incertitudes subsistent",
            style="bold yellow",
        )
        border = "yellow"

    console.print()
    console.print(
        Panel(
            Text.assemble(counts, "\n", banner_text),
            title="Verdict global",
            border_style=border,
            expand=True,
        )
    )
    console.print()


# ── helpers ────────────────────────────────────────────────────────────


def _get_desc(
    assertion_map: dict[str, Assertion],
    assertion_id: str,
) -> str:
    """Return the description for *assertion_id*, or empty string."""
    a = assertion_map.get(assertion_id)
    return a.description if a else ""


def _truncate(text: str, max_len: int) -> str:
    """Return *text* truncated to *max_len* chars with an ellipsis."""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"

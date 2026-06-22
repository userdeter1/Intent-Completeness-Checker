import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from intentcheck.core.git_utils import NotAGitRepoError
from intentcheck.core.orchestrator import resolve_intent, run_pipeline
from intentcheck.core.report import (
    build_json_report,
    compute_overall_verdict,
    render_terminal_report,
)

app = typer.Typer(help="Intent Completeness Checker")
console = Console()


@app.command()
def investigate(
    intent: Optional[str] = typer.Option(
        None, "--intent", "-i", help="The textual intent to verify."
    ),
    repo_path: Path = typer.Option(
        Path("."), "--repo-path", "-r", help="Path to the git repository."
    ),
    full_pipeline: bool = typer.Option(
        False,
        "--full-pipeline",
        help="Run the Searcher and Judge on all assertions concurrently.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output the report as JSON instead of the Rich terminal format.",
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        help="Override the default LLM provider (e.g., openai, anthropic, groq).",
    ),
    model_id: Optional[str] = typer.Option(
        None,
        "--model",
        help="Override the default model ID (e.g., gpt-4o, claude-3-5-sonnet-latest).",
    ),
) -> None:
    """
    Investigates an intent and breaks it down into precise assertions.
    """
    if not full_pipeline:
        from intentcheck.agents.investigator import investigate_intent

        try:
            raw_intent = resolve_intent(intent, repo_path)
        except NotAGitRepoError as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise typer.Exit(code=1)
        except ValueError as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise typer.Exit(code=1)

        with console.status("[bold green]Investigating intent..."):
            try:
                output = investigate_intent(raw_intent, provider, model_id)
            except Exception as e:
                console.print(f"[bold red]Error during investigation:[/] {e}")
                raise typer.Exit(code=1)

        table = Table(title="Generated Assertions", show_lines=True)
        table.add_column("ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="green")

        for assertion in output.assertions:
            table.add_row(assertion.id, assertion.assertion_type, assertion.description)

        console.print(table)
        return

    # Running the full pipeline
    with console.status("[bold green]Running intent completeness pipeline..."):
        try:
            # use asyncio.run to execute the async orchestrator
            result = asyncio.run(
                run_pipeline(
                    intent_text=intent,
                    repo_path=repo_path,
                    provider=provider,
                    model_id=model_id,
                )
            )
        except Exception as e:
            console.print(f"[bold red]Pipeline Error:[/] {e}")
            raise typer.Exit(code=1)

    # Render the report (JSON or Rich terminal).
    if json_output:
        report = build_json_report(result)
        # We use standard print() because console.print() interprets square brackets
        # as markup, which corrupts JSON containing type hints like list[str].
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        render_terminal_report(result, console)

    # Exit code: 1 when at least one assertion is violated.
    if compute_overall_verdict(result) == "incomplete":
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

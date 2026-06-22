import asyncio
from pathlib import Path

from intentcheck.agents.investigator import investigate_intent
from intentcheck.agents.judge import run_judge
from intentcheck.agents.searcher import run_searcher
from intentcheck.core.git_utils import get_current_diff
from intentcheck.core.models import (
    Assertion,
    AssertionErrorModel,
    Intent,
    IntentCheckResult,
    JudgeVerdict,
)


def resolve_intent(intent_text: str | None, repo_path: Path) -> Intent:
    """Builds an Intent from explicit text or from the git diff of a repo.

    This is the single source of truth for constructing an Intent object.
    Both the CLI commands (simple investigate and full pipeline) delegate here
    so that the logic for falling back to a git diff is never duplicated.

    Args:
        intent_text: Explicit intent text provided by the user, or None to
            auto-detect from the git diff.
        repo_path: Path to the git repository (used when intent_text is None).

    Returns:
        A fully constructed Intent object.

    Raises:
        NotAGitRepoError: If no intent_text is given and repo_path is not a
            valid git repository.
        ValueError: If no intent_text is given and the git diff is empty.
    """
    if intent_text is not None:
        return Intent(text=intent_text, source="user_provided")

    # No explicit intent — fall back to the git diff.
    diff = get_current_diff(repo_path)
    if not diff.strip():
        raise ValueError("No intent provided and no git diff found.")
    return Intent(text=diff, source="inferred_from_diff")


async def _process_assertion(
    assertion: Assertion,
    repo_path: Path,
    semaphore: asyncio.Semaphore,
    provider: str | None = None,
    model_id: str | None = None,
) -> JudgeVerdict | AssertionErrorModel:
    """Processes a single assertion through Searcher and Judge.
    Wrapped with a semaphore."""
    async with semaphore:
        try:
            # We use run_searcher and run_judge which use the async agent.arun()
            searcher_output = await run_searcher(
                assertion, repo_path, provider, model_id
            )
            judge_verdict = await run_judge(
                assertion, searcher_output, repo_path, provider, model_id
            )
            return judge_verdict
        except Exception as e:
            return AssertionErrorModel(
                assertion_id=assertion.id,
                error_message=f"{type(e).__name__}: {str(e)}",
            )


async def run_pipeline(
    intent_text: str | None,
    repo_path: Path,
    max_concurrency: int = 3,
    provider: str | None = None,
    model_id: str | None = None,
) -> IntentCheckResult:
    """
    Runs the full intent completeness pipeline.

    1. Determines intent.
    2. Investigates intent to extract assertions.
    3. Runs Searcher and Judge for each assertion concurrently.
    """
    raw_intent = resolve_intent(intent_text, repo_path)

    investigator_output = investigate_intent(raw_intent, provider, model_id)

    semaphore = asyncio.Semaphore(max_concurrency)

    tasks = [
        _process_assertion(assertion, repo_path, semaphore, provider, model_id)
        for assertion in investigator_output.assertions
    ]

    results = await asyncio.gather(*tasks)

    verdicts = []
    errors = []

    for result in results:
        if isinstance(result, JudgeVerdict):
            verdicts.append(result)
        elif isinstance(result, AssertionErrorModel):
            errors.append(result)

    return IntentCheckResult(
        intent=raw_intent,
        assertions=investigator_output.assertions,
        verdicts=verdicts,
        errors=errors,
    )

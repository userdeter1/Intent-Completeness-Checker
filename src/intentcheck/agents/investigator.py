import logging

from agno.agent import Agent

from intentcheck.config import resolve_model
from intentcheck.core.models import Intent, InvestigatorOutput

logger = logging.getLogger(__name__)


def _ensure_unique_assertion_ids(output: InvestigatorOutput) -> InvestigatorOutput:
    """Validates and fixes assertion IDs to guarantee uniqueness.

    We cannot trust the LLM to always produce unique, non-empty assertion IDs.
    If the LLM generates duplicates or blank IDs, the downstream matching logic
    (Searcher -> Judge -> final report) would silently corrupt results because
    it joins on assertion_id. This function detects collisions and empty IDs,
    replacing them with deterministic sequential identifiers (A1, A2, ...).
    """
    seen: set[str] = set()
    needs_fix = False

    for assertion in output.assertions:
        if not assertion.id or not assertion.id.strip() or assertion.id in seen:
            needs_fix = True
            break
        seen.add(assertion.id)

    if not needs_fix:
        return output

    # At least one ID is empty or duplicated — reassign all IDs sequentially
    # to maintain a consistent, predictable scheme.
    for idx, assertion in enumerate(output.assertions, start=1):
        assertion.id = f"A{idx}"

    return output


def investigate_intent(
    intent: Intent, provider: str | None = None, model_id: str | None = None
) -> InvestigatorOutput:
    """Uses the LLM to break down the intent into an InvestigatorOutput."""

    agent = Agent(
        model=resolve_model(provider, model_id),
        description=(
            "You are an expert Investigator AI, specialized in verifying code "
            "modification intents."
        ),
        instructions=[
            "Your ONLY role is to receive a raw intent (text or diff) and "
            "decompose it into a list of verifiable Assertions.",
            "Assertions MUST be atomic (one specific thing per assertion).",
            "Assertions MUST be precise and unambiguous.",
            "Cover both textual aspects (variable names, strings) AND logical "
            "aspects (business rules) if suggested.",
            "If the intent is vague or too broad, produce reasonable assertions "
            "instead of failing.",
            "Ensure output strictly matches the InvestigatorOutput schema.",
        ],
        output_schema=InvestigatorOutput,
    )

    prompt = f"""
Analyze the following intent and decompose it into verifiable assertions.

Intent Source: {intent.source}
Intent Content:
{intent.text}
"""

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = agent.run(prompt)
            if isinstance(response.content, InvestigatorOutput):
                # Post-process to guarantee ID uniqueness before returning.
                return _ensure_unique_assertion_ids(response.content)

            content_str = str(response.content)
            if "api key" in content_str.lower() or "apikey" in content_str.lower():
                raise ValueError(
                    "Missing/invalid API key. "
                    "Set the correct API key for your provider.\n"
                    f"Original error: {content_str}"
                )

            raise ValueError(
                "Agent did not return a valid InvestigatorOutput. "
                f"Got: {type(response.content)}\nContent snippet: {content_str[:200]}"
            )
        except Exception as e:
            if attempt < max_retries:
                logger.warning(
                    f"Investigator attempt {attempt + 1} failed: {e}. Retrying..."
                )
                prompt = (
                    f"The previous attempt failed with error: {e}\n"
                    "Please correct your formatting and try again."
                )
            else:
                raise ValueError(
                    "Investigator failed after "
                    f"{max_retries + 1} attempts. Last error: {e}"
                ) from e

import logging
from pathlib import Path

from agno.agent import Agent

from intentcheck.config import resolve_model
from intentcheck.core.models import Assertion, SearcherOutput
from intentcheck.tools.agent_wrappers import (
    get_agent_grep_tool,
    get_agent_read_file_tool,
)

logger = logging.getLogger(__name__)


async def run_searcher(
    assertion: Assertion,
    repo_path: Path | str,
    provider: str | None = None,
    model_id: str | None = None,
) -> SearcherOutput:
    """
    Uses the LLM asynchronously to search the repository for evidence of an assertion.
    """

    agent_grep_tool = get_agent_grep_tool(repo_path)
    agent_read_file_tool = get_agent_read_file_tool(repo_path)

    agent = Agent(
        model=resolve_model(provider, model_id),
        description=(
            "You are an expert Searcher AI, specialized in finding evidence "
            "for or against code modification assertions."
        ),
        instructions=[
            "Your goal is to find concrete evidence in the repository regarding "
            "the provided assertion.",
            "Use agent_grep_tool to search for terms. If the first search yields no "
            "results, TRY DIFFERENT FORMULATIONS (e.g., snake_case, camelCase, "
            "synonyms) before concluding absence.",
            "Use agent_read_file_tool to examine the context around matched lines "
            "if necessary to understand the relevance.",
            "An absence of evidence is only valid if you have searched thoroughly "
            "under multiple angles.",
            "IMPORTANT: Use ONLY the native tool-calling mechanism for tools. "
            "NEVER generate free text imitating a function call (like <function=...>).",
            "Provide your final output as a SearcherOutput object, including the "
            "assertion ID, the list of evidence, and your confidence level.",
        ],
        tools=[agent_grep_tool, agent_read_file_tool],
        output_schema=SearcherOutput,
        # We use a parser_model to separate tool usage from structured output parsing.
        # This is a workaround for Groq API which does not support combining
        # JSON mode and tool/function calling in a single request.
        parser_model=resolve_model(provider, model_id),
    )

    prompt = f"""
Search the repository for evidence regarding the following assertion:

Assertion ID: {assertion.id}
Assertion Description: {assertion.description}
Assertion Type: {assertion.assertion_type}

Ensure you use your tools to search thoroughly.
"""

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = await agent.arun(prompt)
            if isinstance(response.content, SearcherOutput):
                return response.content
            raise ValueError(
                "Agent did not return a valid SearcherOutput. "
                f"Got: {type(response.content)}"
            )
        except Exception as e:
            if attempt < max_retries:
                logger.warning(
                    f"Searcher attempt {attempt + 1} failed: {e}. Retrying..."
                )
                prompt = (
                    f"The previous attempt failed with error: {e}\n"
                    "Please correct your formatting or tool usage and try again."
                )
            else:
                raise ValueError(
                    f"Searcher failed after {max_retries + 1} attempts. Last error: {e}"
                ) from e

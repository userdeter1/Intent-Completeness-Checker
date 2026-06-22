import logging
from pathlib import Path

from agno.agent import Agent

from intentcheck.config import resolve_model
from intentcheck.core.models import Assertion, JudgeVerdict, SearcherOutput
from intentcheck.tools.agent_wrappers import (
    get_agent_grep_tool,
    get_agent_read_file_tool,
)

logger = logging.getLogger(__name__)


async def run_judge(
    assertion: Assertion,
    searcher_output: SearcherOutput,
    repo_path: Path | str,
    provider: str | None = None,
    model_id: str | None = None,
) -> JudgeVerdict:
    """
    Uses the LLM asynchronously to judge an assertion based on Searcher
    output and tools.
    """

    agent_grep_tool = get_agent_grep_tool(repo_path)
    agent_read_file_tool = get_agent_read_file_tool(repo_path)

    agent = Agent(
        model=resolve_model(provider, model_id),
        description=(
            "You are an expert Judge AI, specialized in rendering verdicts on "
            "code modification assertions based on evidence."
        ),
        instructions=[
            "Examine the evidence provided by the Searcher critically. Do not accept "
            "it by default.",
            "If the Searcher's confidence is 'low', or if the evidence seems "
            "insufficient to cover the assertion, USE YOUR TOOLS to re-verify "
            "yourself before concluding.",
            "Justify explicitly each retained or dismissed evidence in your output.",
            "Never render a verdict of 'satisfied' without at least one concrete piece "
            "of evidence supporting it, EXCEPT for 'textual_absence' assertions where "
            "an exhaustive search yielding no evidence can constitute validation.",
            "If you cannot confidently render a 'satisfied' or 'violated' verdict, "
            "choose 'uncertain'.",
            "IMPORTANT: Use ONLY the native tool-calling mechanism for tools. "
            "NEVER generate free text imitating a function call (like <function=...>).",
            "Provide your final output as a JudgeVerdict object.",
        ],
        tools=[agent_grep_tool, agent_read_file_tool],
        output_schema=JudgeVerdict,
        # We use a parser_model to separate tool usage from structured output parsing.
        # This is a workaround for Groq API which does not support combining
        # JSON mode and tool/function calling in a single request.
        parser_model=resolve_model(provider, model_id),
    )

    prompt = f"""
Please judge the following assertion:

Assertion ID: {assertion.id}
Assertion Description: {assertion.description}
Assertion Type: {assertion.assertion_type}

Searcher Output:
{searcher_output.model_dump_json(indent=2)}

Remember to critically evaluate the evidence and use your tools if needed.
"""

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = await agent.arun(prompt)
            if isinstance(response.content, JudgeVerdict):
                return response.content
            raise ValueError(
                "Agent did not return a valid JudgeVerdict. "
                f"Got: {type(response.content)}"
            )
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Judge attempt {attempt + 1} failed: {e}. Retrying...")
                prompt = (
                    f"The previous attempt failed with error: {e}\n"
                    "Please correct your formatting or tool usage and try again."
                )
            else:
                raise ValueError(
                    f"Judge failed after {max_retries + 1} attempts. Last error: {e}"
                ) from e

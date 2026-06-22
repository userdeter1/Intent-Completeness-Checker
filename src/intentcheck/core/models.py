from typing import Literal

from pydantic import BaseModel, Field


class Intent(BaseModel):
    """Represents the raw intent to be verified."""

    text: str = Field(
        description="The textual description of the intent or the git diff."
    )
    source: Literal["user_provided", "inferred_from_diff"] = Field(
        description=(
            "The source of this intent (provided by user or inferred from diff)."
        )
    )


class Assertion(BaseModel):
    """A verifiable assertion extracted from an intent."""

    id: str = Field(
        description=(
            "A stable, unique identifier for this assertion (e.g., 'A1', "
            "'no-groq-key')."
        )
    )
    description: str = Field(
        description=(
            "A clear, precise, and atomic verifiable statement. (e.g., "
            "'GROQ_API_KEY should not appear in active code')."
        )
    )
    assertion_type: Literal[
        "textual_absence", "textual_presence", "logical_consistency"
    ] = Field(description="The type of assertion being made.")


class InvestigatorOutput(BaseModel):
    """The output of the Investigator agent."""

    intent: Intent = Field(description="The original intent that was investigated.")
    assertions: list[Assertion] = Field(
        description="A list of atomic assertions derived from the intent."
    )


class Evidence(BaseModel):
    """Concrete evidence found in the repository relating to an assertion."""

    file_path: str = Field(description="The path to the file containing the evidence.")
    line_number: int | None = Field(
        default=None,
        description="The line number where the evidence is found (if applicable).",
    )
    snippet: str = Field(description="The relevant code snippet or text from the file.")
    relevance_note: str = Field(
        description="Explanation of why this evidence is relevant to the assertion."
    )


class SearcherOutput(BaseModel):
    """The output of the Searcher agent."""

    assertion_id: str = Field(
        description="The ID of the assertion this search relates to."
    )
    evidence: list[Evidence] = Field(
        description="A list of evidence found in the repository."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="How confident the searcher is that it found all relevant evidence."
    )


class DismissedEvidence(Evidence):
    """Evidence that was reviewed but dismissed by the Judge."""

    dismissal_reason: str = Field(
        description="Explanation of why this evidence was dismissed."
    )


class JudgeVerdict(BaseModel):
    """The final verdict rendered by the Judge agent for an assertion."""

    assertion_id: str = Field(description="The ID of the assertion being judged.")
    verdict: Literal["satisfied", "violated", "uncertain"] = Field(
        description="The final verdict on the assertion."
    )
    reasoning: str = Field(
        description="Explanation of the verdict, citing the evidence used."
    )
    confirmed_evidence: list[Evidence] = Field(
        description="The evidence confirmed as relevant to the verdict."
    )
    dismissed_evidence: list[DismissedEvidence] = Field(
        description="Evidence that was reviewed but deemed irrelevant or insufficient."
    )


class AssertionErrorModel(BaseModel):
    """Represents an error that occurred while processing an assertion."""

    assertion_id: str = Field(description="The ID of the assertion that failed.")
    error_message: str = Field(description="The error message or traceback.")


class IntentCheckResult(BaseModel):
    """The final result of the intent check pipeline."""

    intent: Intent = Field(description="The original intent that was investigated.")
    assertions: list[Assertion] = Field(
        description="The assertions extracted from the intent."
    )
    verdicts: list[JudgeVerdict] = Field(
        description="The verdicts for the successfully processed assertions."
    )
    errors: list[AssertionErrorModel] = Field(
        description="Errors encountered while processing specific assertions."
    )

from collections.abc import Callable
from pathlib import Path

from intentcheck.tools.grep_tool import grep_tool
from intentcheck.tools.read_file_tool import read_file_tool


def get_agent_grep_tool(repo_path: Path | str) -> Callable[[str], str]:
    def agent_grep_tool(term: str) -> str:
        """
        Search the repository for a given term.

        Args:
            term: The base term to search for (e.g. 'api key' or 'apiKey').
        """
        return grep_tool(term=term, repo_path=str(repo_path))

    return agent_grep_tool


def get_agent_read_file_tool(
    repo_path: Path | str,
) -> Callable[[str, int, int | None], str]:
    def agent_read_file_tool(
        file_path: str, start_line: int = 1, end_line: int | None = None
    ) -> str:
        """
        Reads the content of a file, optionally within a specific line range.

        Args:
            file_path: The relative path to the file from the repository root.
            start_line: The starting line number (1-indexed). Defaults to 1.
            end_line: The ending line number (inclusive). Defaults to None.
        """
        return read_file_tool(
            file_path=file_path,
            repo_path=str(repo_path),
            start_line=start_line,
            end_line=end_line,
        )

    return agent_read_file_tool

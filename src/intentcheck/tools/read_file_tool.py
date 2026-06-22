from pathlib import Path


def read_file_tool(
    file_path: str, repo_path: str, start_line: int = 1, end_line: int | None = None
) -> str:
    """
    Reads the content of a file, optionally within a specific line range.

    Args:
        file_path: The relative path to the file from the repository root.
        repo_path: The absolute path to the repository.
        start_line: The starting line number (1-indexed). Defaults to 1.
        end_line: The ending line number (inclusive). Defaults to None (end of file).

    Returns:
        The content of the file or line range as a string.
    """
    repo = Path(repo_path).resolve()
    target_file = (repo / file_path).resolve()

    try:
        if not target_file.is_relative_to(repo):
            return f"Error: Cannot read files outside the repository ({file_path})."
    except ValueError:
        return f"Error: Path {file_path} is invalid."

    if not target_file.exists() or not target_file.is_file():
        return f"Error: File '{file_path}' does not exist or is not a file."

    try:
        content = target_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: File '{file_path}' is not a readable text file."

    lines = content.splitlines()
    total_lines = len(lines)

    start = max(1, start_line)
    end = min(total_lines, end_line) if end_line is not None else total_lines

    if start > end or start > total_lines:
        return (
            f"Error: Invalid line range {start_line}-{end_line} "
            f"for file with {total_lines} lines."
        )

    selected_lines = lines[start - 1 : end]
    formatted_lines = [f"{i}: {line}" for i, line in enumerate(selected_lines, start)]

    output = "\n".join(formatted_lines)
    if len(output) > 10000:
        return output[:10000] + "\n... (content truncated due to length)"
    return output

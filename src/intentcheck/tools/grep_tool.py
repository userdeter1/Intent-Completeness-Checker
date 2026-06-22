import re
import subprocess
from pathlib import Path


def generate_case_variants(term: str) -> list[str]:
    """Generates different casing variants for a given term."""
    # Split by non-alphanumeric or camelCase boundary
    words_split = re.sub(r"([a-z])([A-Z])", r"\1 \2", term)
    words = re.split(r"[^a-zA-Z0-9]+", words_split)
    words = [w.lower() for w in words if w]

    if not words:
        return [term]

    snake_case = "_".join(words)
    screaming_case = snake_case.upper()
    camel_case = words[0] + "".join(w.capitalize() for w in words[1:])
    pascal_case = "".join(w.capitalize() for w in words)
    kebab_case = "-".join(words)
    spaced = " ".join(words)

    variants = {
        snake_case,
        screaming_case,
        camel_case,
        pascal_case,
        kebab_case,
        spaced,
        term,
    }
    return list(variants)


def get_searchable_files(repo_path: Path) -> list[Path]:
    """Returns a list of files to search, respecting gitignore if possible."""
    try:
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(repo_path),
            check=True,
            capture_output=True,
            text=True,
        )

        all_files = set(tracked.stdout.splitlines() + untracked.stdout.splitlines())
        return [repo_path / f for f in all_files if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = []
        ignored_dirs = {
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            "venv",
            "env",
            ".ruff_cache",
            ".pytest_cache",
        }
        for path in repo_path.rglob("*"):
            if path.is_file() and not any(part in ignored_dirs for part in path.parts):
                files.append(path)
        return files


def grep_tool(term: str, repo_path: str) -> str:
    """
    Searches the repository for a given term and its case variants
    (snake_case, camelCase, SCREAMING_CASE, etc.).

    Args:
        term: The base term to search for (e.g. 'api key' or 'apiKey').
        repo_path: The absolute path to the repository.

    Returns:
        A string containing the matched files and line numbers, or a message
        if no matches were found.
    """
    repo = Path(repo_path).resolve()
    if not repo.exists() or not repo.is_dir():
        return (
            f"Error: Repository path '{repo_path}' does not exist "
            "or is not a directory."
        )

    variants = generate_case_variants(term)
    # Use case-insensitive search for the generated variants just to be broader
    pattern = "|".join(re.escape(v) for v in variants)
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        # Fallback if somehow pattern is invalid
        regex = re.compile(re.escape(term), re.IGNORECASE)

    files = get_searchable_files(repo)
    results = []

    for path in files:
        if not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                try:
                    rel_path = path.relative_to(repo)
                except ValueError:
                    rel_path = path
                results.append(f"{rel_path}:{i}: {line.strip()}")

    if not results:
        return f"No matches found for term '{term}' (variants: {', '.join(variants)})"

    # Limit output length to avoid context overflow
    output = "\n".join(results)
    if len(output) > 8000:
        return output[:8000] + "\n... (results truncated due to length)"
    return output

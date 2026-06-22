import subprocess
from pathlib import Path


class NotAGitRepoError(Exception):
    """Raised when the specified directory is not a git repository."""

    pass


def get_current_diff(repo_path: Path) -> str:
    """
    Returns the uncommitted git diff (staged + unstaged) of the repository.

    Args:
        repo_path: The path to the git repository.

    Returns:
        The git diff as a string. Empty string if no diff.

    Raises:
        NotAGitRepoError: If the repo_path is not a valid git repository.
    """
    repo_path_str = str(repo_path.resolve())

    try:
        # Check if it's a git repository
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_path_str,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise NotAGitRepoError(f"'{repo_path}' is not a valid git repository.") from e
    except FileNotFoundError as e:
        raise NotAGitRepoError("Git executable not found.") from e

    try:
        # Get unstaged changes
        unstaged = subprocess.run(
            ["git", "diff"],
            cwd=repo_path_str,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        # Get staged changes
        staged = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=repo_path_str,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        return staged + unstaged
    except subprocess.CalledProcessError:
        return ""

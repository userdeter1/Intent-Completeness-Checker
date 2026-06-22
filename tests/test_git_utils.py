import os
import subprocess
from pathlib import Path

import pytest

from intentcheck.core.git_utils import NotAGitRepoError, get_current_diff


def _run_git(cmd: list[str], cwd: Path) -> None:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(cmd, cwd=str(cwd), check=True, env=env, capture_output=True)


def test_get_current_diff_not_a_repo(tmp_path: Path):
    with pytest.raises(NotAGitRepoError):
        get_current_diff(tmp_path)


def test_get_current_diff_no_changes(tmp_path: Path):
    _run_git(["git", "init"], cwd=tmp_path)

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")
    _run_git(["git", "add", "test.txt"], cwd=tmp_path)
    _run_git(["git", "commit", "-m", "init"], cwd=tmp_path)

    diff = get_current_diff(tmp_path)
    assert diff == ""


def test_get_current_diff_with_unstaged_changes(tmp_path: Path):
    _run_git(["git", "init"], cwd=tmp_path)

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")
    _run_git(["git", "add", "test.txt"], cwd=tmp_path)
    _run_git(["git", "commit", "-m", "init"], cwd=tmp_path)

    test_file.write_text("hello world")

    diff = get_current_diff(tmp_path)
    assert "hello world" in diff
    assert "+hello world" in diff


def test_get_current_diff_with_staged_changes(tmp_path: Path):
    _run_git(["git", "init"], cwd=tmp_path)

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")
    _run_git(["git", "add", "test.txt"], cwd=tmp_path)
    _run_git(["git", "commit", "-m", "init"], cwd=tmp_path)

    test_file.write_text("hello world")
    _run_git(["git", "add", "test.txt"], cwd=tmp_path)

    diff = get_current_diff(tmp_path)
    assert "hello world" in diff
    assert "+hello world" in diff

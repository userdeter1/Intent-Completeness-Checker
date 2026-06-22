from pathlib import Path

from intentcheck.tools.grep_tool import generate_case_variants, grep_tool
from intentcheck.tools.read_file_tool import read_file_tool


def test_generate_case_variants():
    variants = generate_case_variants("API Key")
    assert "api_key" in variants
    assert "apiKey" in variants
    assert "API_KEY" in variants
    assert "api-key" in variants
    assert "API Key" in variants


def test_grep_tool(tmp_path: Path):
    import subprocess

    repo = tmp_path

    # Initialize a git repository to test the primary logic
    subprocess.run(["git", "init"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=str(repo), check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=str(repo), check=True
    )

    file1 = repo / "config.py"
    file1.write_text("API_KEY = 'secret'\nother_var = 1")

    # Track config.py
    subprocess.run(["git", "add", "config.py"], cwd=str(repo), check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=str(repo), check=True, capture_output=True
    )

    file2 = repo / "utils.js"
    file2.write_text("function getApiKey() { return 'secret'; }\n")

    # Ignoring logic test
    ignore_file = repo / ".gitignore"
    ignore_file.write_text(".venv/\n")

    ignore_dir = repo / ".venv"
    ignore_dir.mkdir()
    lib_file = ignore_dir / "lib.py"
    lib_file.write_text("api_key = 'ignored'")

    result = grep_tool("API Key", str(repo))

    assert "config.py" in result
    assert "utils.js" in result
    assert "API_KEY" in result
    assert "getApiKey" in result
    assert "lib.py" not in result


def test_read_file_tool(tmp_path: Path):
    repo = tmp_path
    file1 = repo / "test.txt"
    file1.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

    res1 = read_file_tool("test.txt", str(repo))
    assert "1: Line 1" in res1
    assert "5: Line 5" in res1

    res2 = read_file_tool("test.txt", str(repo), start_line=2, end_line=3)
    assert "2: Line 2" in res2
    assert "3: Line 3" in res2
    assert "1: Line 1" not in res2
    assert "4: Line 4" not in res2

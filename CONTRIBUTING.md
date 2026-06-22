# Contributing to Intent Completeness Checker

First off, thank you for considering contributing to the **Intent Completeness Checker**! It's people like you that make the open-source community such a fantastic place to learn, inspire, and create.

This document provides guidelines and instructions for contributing to this project.

## 🛠️ Development Setup

To set up the project locally for development:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/userdeter1/Intent-Completeness-Checker.git
   cd Intent-Completeness-Checker
   ```

2. **Set up your environment:**
   We recommend using a virtual environment (e.g., `venv`, `conda`, or `uv`).
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the project in editable mode with development dependencies:**
   *(Note: ensure you have `pre-commit` installed as well)*
   ```bash
   pip install -e .
   pip install pre-commit pytest ruff
   ```

4. **Install the Pre-commit hook:**
   This project uses `pre-commit` to ensure code quality before every commit.
   ```bash
   pre-commit install
   ```

5. **Configure API Keys:**
   Copy the `.env.example` file to `.env` and add your Groq API key (required to run the AI agents).
   ```bash
   cp .env.example .env
   ```

## 🧪 Running Tests

We use `pytest` for unit testing. Before submitting a Pull Request, please ensure all tests pass:

```bash
pytest
```

## 🧹 Code Quality and Linting

We strictly use `ruff` for fast linting and formatting.

- To check for lint errors:
  ```bash
  ruff check .
  ```
- To auto-format the code:
  ```bash
  ruff format .
  ```

*Note: If you installed `pre-commit`, Ruff will run automatically when you try to commit.*

## 🚀 Submitting a Pull Request (PR)

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes** (ensure they are atomic and well-documented).
3. **Run tests and linting** to verify your changes don't break existing functionality.
4. **Commit your changes**. Our AI pre-commit hook will also verify if your intent is fully covered!
5. **Push to your fork** and submit a PR to the `main` branch of this repository.

## 🐛 Reporting Bugs

If you find a bug, please create an issue providing as much detail as possible, including:
- Steps to reproduce the issue.
- The expected behavior vs. the actual behavior.
- Your OS, Python version, and terminal setup.

Thank you for your contributions!

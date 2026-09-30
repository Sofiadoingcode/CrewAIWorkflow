import subprocess
from pathlib import Path


def git(
    repo_path: str,
    *args: str,
) -> dict:

    process = subprocess.run(
        ["git", *args],
        cwd=Path(repo_path),
        capture_output=True,
        text=True,
    )

    return {
        "command": ["git", *args],
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
        "success": process.returncode == 0,
    }


def create_branch(
    repo_path: str,
    branch: str,
) -> dict:

    return git(
        repo_path,
        "switch",
        "-c",
        branch,
    )


def commit(
    repo_path: str,
    message: str,
) -> dict:

    git(repo_path, "add", ".")

    return git(
        repo_path,
        "commit",
        "-m",
        message,
    )
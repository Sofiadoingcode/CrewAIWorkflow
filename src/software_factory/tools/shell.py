import subprocess
from pathlib import Path


def run_command(
    command: str,
    cwd: str,
    timeout: int = 300,
) -> dict:

    process = subprocess.run(
        command,
        cwd=Path(cwd),
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    return {
        "command": command,
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
        "success": process.returncode == 0,
    }
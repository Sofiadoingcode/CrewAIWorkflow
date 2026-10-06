import sys
import traceback
from pathlib import Path

from software_factory.flow import SoftwareFactoryFlow
from software_factory.llm import coder_llm, reasoning_llm
from software_factory.tools.filesystem import write_file
from software_factory.tools.git import git
from software_factory.tools.shell import run_command

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_REPO = PROJECT_ROOT.parent / "crewai-demo"

FEATURE_REQUEST = (
    'Add a function farewell(name) in greeting.py that returns "Goodbye {name}", '
    "and a pytest test for it in test_greeting.py."
)

SEED_FILES = {
    "greeting.py": 'def greet(name):\n    return f"Hello {name}"\n',
    "test_greeting.py": (
        "from greeting import greet\n\n\n"
        "def test_greet():\n"
        '    assert greet("Bob") == "Hello Bob"\n'
    ),
    ".gitignore": "__pycache__/\n.DS_Store\n",
}

ARTIFACTS = [
    ("Architecture", "architecture.md"),
    ("Tech lead", "tickets.md"),
    ("Implementation", "implementation.md"),
    ("Testing & quality", "quality_report.md"),
    ("Documentation", "documentation.md"),
    ("Deployment validation", "deployment_checklist.md"),
]


def banner(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def check(label: str, ok: bool, detail: str = ""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}" + (f": {detail}" if detail else ""))


def prepare_repo(repo: Path) -> bool:

    if not repo.exists():

        print(f"Creating demo repository {repo}")

        for name, content in SEED_FILES.items():
            write_file(str(repo), name, content)

        git(str(repo), "init", "-b", "main")
        git(str(repo), "add", "-A")
        result = git(str(repo), "commit", "-m", "Initial")

        if not result["success"]:
            print(result["stderr"])
            return False

        return True

    if not git(str(repo), "rev-parse", "--git-dir")["success"]:
        print(f"{repo} exists but is not a git repository.")
        return False

    if git(str(repo), "status", "--porcelain")["stdout"].strip():
        print(
            f"{repo} has uncommitted changes. Clean it, or delete the folder\n"
            "to let the demo create a fresh one."
        )
        return False

    switched = git(str(repo), "checkout", "main")

    if not switched["success"]:
        print(switched["stderr"])
        return False

    print(f"Using demo repository {repo} (branch main)")

    return True


def changed_code_files(repo: Path) -> list[str]:

    tracked = git(str(repo), "diff", "--name-only", "main")["stdout"].split()
    untracked = git(
        str(repo), "ls-files", "--others", "--exclude-standard"
    )["stdout"].split()

    return sorted(
        name
        for name in set(tracked) | set(untracked)
        if not name.startswith("docs/factory/")
    )


def main():

    repo = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else DEFAULT_REPO

    banner("SOFTWARE FACTORY DEMO")

    print(
        f"""
Target repository: {repo}
Feature request:   {FEATURE_REQUEST}

Endpoint 1: {reasoning_llm.model} at {reasoning_llm.base_url}
            Architect, Tech Lead, QA, Documentation, Deployment
Endpoint 2: {coder_llm.model} at {coder_llm.base_url}
            the two coding workers

Six phases run in order, then the diff is shown and you are asked
whether to commit. A run takes about 8 minutes.
"""
    )

    if not prepare_repo(repo):
        return

    flow = SoftwareFactoryFlow()

    try:
        flow.kickoff(
            inputs={
                "repo_path": str(repo),
                "feature_request": FEATURE_REQUEST,
            }
        )
    except Exception:
        traceback.print_exc()
        print("\nThe flow failed. Results below show what was produced before it.")

    banner("ARTIFACTS")

    for responsibility, name in ARTIFACTS:
        path = repo / "docs" / "factory" / name
        print(f"  {responsibility:<24} {path if path.exists() else 'missing'}")

    banner("REALITY CHECK")

    print(
        "Checked by git and pytest, not by the agents. The agents' reports can\n"
        "claim changes that never happened; these checks cannot.\n"
    )

    missing = [name for _, name in ARTIFACTS if not (repo / "docs" / "factory" / name).exists()]
    check("All six artifacts written", not missing, ", ".join(missing))

    code_files = changed_code_files(repo)
    check("Code changed in the repository", bool(code_files), ", ".join(code_files))

    test_run = run_command(
        f"PYTHONDONTWRITEBYTECODE=1 {sys.executable} -m pytest -q -p no:cacheprovider",
        cwd=str(repo),
    )
    summary = (test_run["stdout"].strip().splitlines() or ["no output"])[-1]
    check("Tests pass", test_run["success"], summary)

    test_file = repo / "test_greeting.py"
    farewell_test = test_file.exists() and "def test_farewell" in test_file.read_text(
        encoding="utf-8"
    )
    check("A test for farewell() exists", farewell_test)

    print(
        f"""
Read the artifacts in {repo / "docs" / "factory"}.
Documentation and the deployment checklist are free text and may describe
things that do not exist; compare them with the code.

To run the demo again, delete {repo}
(or, if you committed, just run it again: it switches back to main).
"""
    )


if __name__ == "__main__":
    main()

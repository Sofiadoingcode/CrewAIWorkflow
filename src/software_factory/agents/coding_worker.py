from crewai import Agent, Crew, Task

from software_factory.llm import coder_llm
from software_factory.tools.crew_tools import create_write_tool
from software_factory.tools.filesystem import read_repository


def create_coding_worker(
    worker_name: str,
    role: str,
    goal: str,
    repo_path: str,
) -> Agent:

    return Agent(
        role=role,
        goal=goal,
        backstory=(
            "You are a senior software engineer working inside "
            "a multi-agent software engineering factory. "
            "You make focused changes, respect architectural "
            "boundaries, write tests, and never modify unrelated "
            "parts of the repository."
        ),
        llm=coder_llm,
        tools=[create_write_tool(repo_path)],
        verbose=True,
        allow_delegation=False,
    )


def run_coding_worker(
    worker_name: str,
    role: str,
    goal: str,
    repo_path: str,
    feature_request: str,
    architecture: dict,
    tickets: dict,
) -> dict:

    worker = create_coding_worker(
        worker_name,
        role,
        goal,
        repo_path,
    )

    task = Task(
        description=f"""
Worker:

{worker_name}

Repository:

{repo_path}

Repository files:

{read_repository(repo_path)}

Feature:

{feature_request}

Architecture:

{architecture}

Tickets:

{tickets}

Implement ONLY the tickets assigned to you.

You MUST:

1. Inspect the existing repository files above.
2. Identify your assigned tickets.
3. Implement the requested functionality.
4. Modify the required source files.
5. Add or update tests.
6. Review your changes.
7. Report every modified file.
8. Report remaining risks.

Do not implement tickets belonging to another worker.

Do not modify unrelated files.

To change a file you MUST call the write_repository_file
tool with the relative path and the COMPLETE new file content.
Call it once per file. Writing code in your answer does
NOT change the repository.

Only report files you actually wrote with the tool.

Follow the architecture and ticket boundaries.
""",
        expected_output="""
Implementation report containing:

- Worker
- Tickets implemented
- Files modified
- Implementation summary
- Tests added
- Risks
- Remaining work
""",
        agent=worker,
    )

    crew = Crew(
        agents=[worker],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "worker": worker_name,
        "status": "complete",
        "result": str(result),
    }
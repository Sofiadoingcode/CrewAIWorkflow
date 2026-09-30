from crewai import Agent, Crew, Task

from software_factory.llm import local_llm


def create_coding_worker(
    worker_name: str,
    role: str,
    goal: str,
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
        llm=local_llm,
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
    )

    task = Task(
        description=f"""
Worker:

{worker_name}

Repository:

{repo_path}

Feature:

{feature_request}

Architecture:

{architecture}

Tickets:

{tickets}

Implement ONLY the tickets assigned to you.

You MUST:

1. Inspect the existing repository.
2. Identify your assigned tickets.
3. Implement the requested functionality.
4. Modify the required source files.
5. Add or update tests.
6. Run relevant tests.
7. Run static checks where available.
8. Review your changes.
9. Report every modified file.
10. Report test results.
11. Report remaining risks.

Do not implement tickets belonging to another worker.

Do not modify unrelated files.

Follow the architecture and ticket boundaries.
""",
        expected_output="""
Implementation report containing:

- Worker
- Tickets implemented
- Files modified
- Implementation summary
- Tests added
- Tests executed
- Test results
- Static analysis
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
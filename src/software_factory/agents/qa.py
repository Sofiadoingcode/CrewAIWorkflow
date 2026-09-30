from crewai import Agent, Crew, Task

from software_factory.llm import local_llm


def run_qa(
    repo_path,
    feature_request,
    architecture,
    tickets,
    worker_results,
):

    qa = Agent(
        role="QA Engineer",
        goal=(
            "Validate the implementation using tests, static analysis, "
            "acceptance criteria, and integration checks."
        ),
        backstory=(
            "You are a senior QA engineer responsible for determining "
            "whether an implementation satisfies its requirements."
        ),
        llm=local_llm,
        verbose=True,
        allow_delegation=False,
    )

    task = Task(
        description=f"""
Repository:

{repo_path}

Feature:

{feature_request}

Architecture:

{architecture}

Tickets:

{tickets}

Worker results:

{worker_results}

Validate:

1. Unit tests
2. Integration tests
3. API behavior
4. Acceptance criteria
5. Regression risks
6. Security
7. Edge cases
8. Static analysis
9. Missing tests
10. Remaining risks

IMPORTANT:

Do not claim that a test passed unless it was actually executed.
""",
        expected_output="""
Quality report containing:

- Tests executed
- Test results
- Static analysis
- Acceptance criteria coverage
- Failures
- Missing coverage
- Risks
- Recommended fixes
""",
        agent=qa,
    )

    crew = Crew(
        agents=[qa],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "report": str(result),
    }
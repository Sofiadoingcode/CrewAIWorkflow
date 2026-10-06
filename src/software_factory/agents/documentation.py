from crewai import Agent, Crew, Task

from software_factory.llm import reasoning_llm
from software_factory.tools.filesystem import read_repository


def run_documentation(
    repo_path,
    feature_request,
    architecture,
    worker_results,
    quality_report,
):

    agent = Agent(
        role="Technical Documentation Engineer",
        goal=(
            "Create accurate developer and operational documentation "
            "for the implemented feature."
        ),
        backstory=(
            "You are an experienced technical writer who documents "
            "software systems for developers and operators."
        ),
        llm=reasoning_llm,
        verbose=True,
        allow_delegation=False,
    )

    task = Task(
        description=f"""
Repository:

{repo_path}

Repository files:

{read_repository(repo_path)}

Feature:

{feature_request}

Architecture:

{architecture}

Implementation:

{worker_results}

QA:

{quality_report}

Create documentation covering:

1. README
2. Installation
3. Configuration
4. Environment variables
5. API usage
6. Architecture
7. Operational runbook
8. Troubleshooting
9. Deployment
10. Known limitations

Only document functionality that actually exists.
""",
        expected_output="""
Documentation report containing:

- README
- API documentation
- Configuration
- Environment variables
- Architecture documentation
- Runbook
- Troubleshooting
- Deployment documentation
- Known limitations
""",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "report": str(result),
    }
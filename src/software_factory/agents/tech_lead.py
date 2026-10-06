from crewai import Agent, Crew, Task

from software_factory.llm import reasoning_llm
from software_factory.tools.filesystem import read_repository


def run_tech_lead(
    repo_path: str,
    feature_request: str,
    architecture: dict,
) -> dict:

    tech_lead = Agent(
        role="Technical Lead",
        goal=(
            "Convert an architecture into small, independently "
            "implementable engineering tickets."
        ),
        backstory=(
            "You are an experienced technical lead. "
            "You specialize in decomposition, dependency management, "
            "acceptance criteria, testing strategy, and parallel "
            "engineering execution."
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

Create the implementation plan.

Every ticket MUST contain:

- ID
- Title
- Description
- Scope
- Out of scope
- Acceptance criteria
- Definition of Done
- Dependencies
- Files/directories
- Recommended worker
- Implementation order

Important:

Design tickets so multiple workers can work in parallel
where possible.

Avoid assigning the same file to multiple workers unless
there is an explicit dependency.

Identify which tickets can run concurrently.
""",
        expected_output="""
A structured implementation plan containing multiple
engineering tickets.

Each ticket contains:

ID
Title
Description
Scope
Out of scope
Acceptance criteria
Definition of Done
Dependencies
Files/directories
Recommended worker
Implementation order
Parallelization information
""",
        agent=tech_lead,
    )

    crew = Crew(
        agents=[tech_lead],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "plan": str(result),
    }
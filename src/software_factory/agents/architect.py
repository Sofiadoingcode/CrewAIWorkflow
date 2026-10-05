
from crewai import Agent, Crew, Task

from software_factory.llm import local_llm
from software_factory.tools.filesystem import read_repository


def run_architect(
    repo_path: str,
    feature_request: str,
) -> dict:

    architect = Agent(
        role="Software Architect",
        goal=(
            "Analyze an existing software repository and design a "
            "maintainable architecture for the requested feature."
        ),
        backstory=(
            "You are a senior software architect experienced in "
            "API design, distributed systems, security, testing, "
            "deployment architecture, and maintainable codebases."
        ),
        llm=local_llm,
        verbose=True,
        allow_delegation=False,
    )

    task = Task(
        description=f"""
Analyze the repository:

{repo_path}

Repository files:

{read_repository(repo_path)}

Requested feature:

{feature_request}

Produce an architecture proposal.

The proposal MUST contain:

1. Existing-system analysis
2. Component decomposition
3. Component responsibilities
4. Interfaces between components
5. API contracts
6. Data model changes
7. Deployment topology
8. Security considerations
9. Testing strategy
10. Architecture decisions
11. Risks and assumptions
12. Files/directories likely to change

The architecture must allow multiple coding workers
to implement independent parts of the feature.

Clearly identify which files should belong to which
implementation area.

Do not invent unrelated functionality.
""",
        expected_output="""
A complete architecture proposal covering:

- Existing system
- Components
- Responsibilities
- Interfaces
- API contracts
- Data model
- Deployment
- Security
- Testing
- Architecture decisions
- Risks
- Files to change
- Parallel implementation boundaries
""",
        agent=architect,
    )

    crew = Crew(
        agents=[architect],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()

    return {
        "proposal": str(result),
    }
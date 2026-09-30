from crewai import Agent, Crew, Task

from software_factory.llm import local_llm


def run_deployment(
    repo_path,
    feature_request,
    architecture,
    quality_report,
    documentation,
):

    agent = Agent(
        role="DevOps Engineer",
        goal=(
            "Validate deployment configuration and operational "
            "readiness."
        ),
        backstory=(
            "You are a senior DevOps engineer experienced with "
            "containers, configuration, health checks, deployment "
            "systems, and production operations."
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

QA:

{quality_report}

Documentation:

{documentation}

Validate:

1. Environment variables
2. Required services
3. Database requirements
4. Startup configuration
5. Health checks
6. Container configuration
7. Deployment configuration
8. Configuration validation
9. Rollback strategy
10. Operational risks

Produce a deployment validation checklist.

Inspect the actual repository rather than assuming
configuration exists.
""",
        expected_output="""
Deployment validation report containing:

- Environment requirements
- Required dependencies
- Configuration
- Health checks
- Deployment configuration
- Rollback considerations
- Operational risks
- Deployment checklist
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
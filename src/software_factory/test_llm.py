from crewai import Agent, Crew, Task

from .llm import local_llm


def main():
    agent = Agent(
        role="Software Architect",
        goal="Explain software architecture clearly.",
        backstory=(
            "You are a senior software architect "
            "with extensive software engineering experience."
        ),
        llm=local_llm,
        verbose=True,
        allow_delegation=False,
    )

    task = Task(
        description=(
            "Explain in three sentences what a software "
            "architecture document should contain."
        ),
        expected_output=(
            "Three clear sentences describing the contents "
            "of a software architecture document."
        ),
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()

    print("\n=== RESULT ===")
    print(result)


if __name__ == "__main__":
    main()
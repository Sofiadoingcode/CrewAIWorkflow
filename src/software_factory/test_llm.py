from crewai import Agent, Crew, Task

from .llm import coder_llm, reasoning_llm


def check(name, llm):
    print(f"\n=== {name}: {llm.model} at {llm.base_url} ===")

    agent = Agent(
        role="Software Architect",
        goal="Explain software architecture clearly.",
        backstory=(
            "You are a senior software architect "
            "with extensive software engineering experience."
        ),
        llm=llm,
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


def main():
    check("Endpoint 1", reasoning_llm)
    check("Endpoint 2", coder_llm)


if __name__ == "__main__":
    main()
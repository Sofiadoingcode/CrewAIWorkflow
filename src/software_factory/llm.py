from crewai import LLM


local_llm = LLM(
    model="ollama/llama3.1-16k:latest",
    base_url="http://localhost:11434",
    temperature=0.2,
    max_tokens=2048,
)

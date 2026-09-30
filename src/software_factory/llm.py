from crewai import LLM


local_llm = LLM(
    model="ollama/llama3.1:latest",
    base_url="http://localhost:11434",
)
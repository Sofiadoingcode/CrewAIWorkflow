import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


# Endpoint 1: architect, tech lead, QA, documentation, deployment
reasoning_llm = LLM(
    model="ollama/" + os.getenv("ENDPOINT_1_MODEL", "qwen2.5-3b-16k:latest"),
    base_url=os.getenv("ENDPOINT_1_URL", "http://localhost:11434"),
    temperature=0.2,
    max_tokens=2048,
)

# Endpoint 2: the coding workers
coder_llm = LLM(
    model="ollama/" + os.getenv("ENDPOINT_2_MODEL", "llama3.1-16k:latest"),
    base_url=os.getenv("ENDPOINT_2_URL", "http://localhost:11435"),
    temperature=0.2,
    max_tokens=2048,
)

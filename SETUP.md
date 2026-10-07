# Setup

How to get the CrewAI workflow running and run the demo. 

## Prerequisites

- Python 3.11 or 3.12
- Git
- uv: https://docs.astral.sh/uv/
- Ollama: https://ollama.com/download
- About 10 GB of free RAM

## 1. Install

```bash
git clone https://github.com/Sofiadoingcode/CrewAIWorkflow
cd CrewAIWorkflow
uv sync --extra dev
```

`--extra dev` installs pytest and ruff, which the workflow runs.

## 2. Start the two endpoints

Endpoint 1 is the normal Ollama on port 11434 (the Ollama app, or
`ollama serve`).

Endpoint 2 runs on port 11435. Start it in a separate terminal and leave it
open:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama serve
```

| Endpoint | Address | Model | Used by |
|---|---|---|---|
| 1 | localhost:11434 | qwen2.5 3B | architect, tech lead, QA, documentation, deployment |
| 2 | localhost:11435 | llama3.1 8B | the two coders |

## 3. Get the models

Only needed once. The Modelfiles give both models a 16k context window.
Ollama's default is too small and it cuts the prompt without any error.

```bash
ollama pull qwen2.5:3b
ollama pull llama3.1
ollama create qwen2.5-3b-16k -f Modelfile.qwen
ollama create llama3.1-16k -f Modelfile
```

## 4. Configure

```bash
cp .env.example .env
```

`.env` holds the address and model of each endpoint. The defaults match the
steps above, so you don't need to change anything.

## 5. Check that it works

```bash
uv run python -m software_factory.test_llm
```

Both endpoints should answer, and it prints the model and URL for each.

## 6. Run the demo

```bash
uv run python -m software_factory.demo
```

The demo creates a small test repo called `crewai-demo` next to this folder
and asks the agents to add a `farewell(name)` function with a test. It takes
about 10-20 minutes.

The six roles run one after another and write their output to
`docs/factory/` in the test repo:

| Step | Output |
|---|---|
| Architect | `architecture.md` |
| Tech lead | `tickets.md` |
| Two coders | the code change, `implementation.md` |
| QA (pytest and ruff run first) | `quality_report.md` |
| Documentation | `documentation.md` |
| Deployment | `deployment_checklist.md` |

At the end you see the git diff and are asked `Commit these changes? (y/n)`.
The demo then checks the result with git and pytest: all files written, code
changed, tests passing.

To run it again, answer `n` and delete the `crewai-demo` folder.

## Your own task

```bash
uv run software-factory
```

It asks for the path to a git repo and a one-line feature request. The repo
needs at least one commit and no uncommitted changes. See README.md for
details and for the results of our runs.

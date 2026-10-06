# Software Factory (CrewAI)

Contents: [Setup](#1-setup) · [Run](#2-run) · [How it works](#3-how-it-works) ·
[Changes](#4-changes-since-the-initial-commit) · [Runs and results](#5-runs-and-results) ·
[Findings](#6-findings) · [Requirements](#7-requirements-status) ·
[Open items](#8-open-items)

---

## 1. Setup

**Requirements:** macOS or Linux, ~10 GB free RAM, Python 3.11/3.12,
[uv](https://docs.astral.sh/uv/), [Ollama](https://ollama.com/download), git.
Tested on a 16 GB Apple Silicon MacBook, CrewAI 1.15.22, Python 3.12.

**Install** (the dev extra installs pytest and ruff, which QA runs):

```bash
git clone https://github.com/Sofiadoingcode/CrewAIWorkflow
cd CrewAIWorkflow
uv sync --extra dev
```

**Two model endpoints.** Both listen on localhost only and share the model
store, so models are pulled once.

| Endpoint | Address | Model | Roles |
|---|---|---|---|
| 1 | `localhost:11434` | qwen2.5 3B, 16k context | Architect, Tech Lead, QA, Documentation, Deployment |
| 2 | `localhost:11435` | llama3.1 8B, 16k context | the two coding workers |

Endpoint 1 is the normal Ollama (app or `ollama serve`). Endpoint 2 is
started by hand in its own terminal and left running:

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama serve
```

Pull the models and create the 16k-context versions (once). The Modelfiles
are needed: Ollama's default context is too small for the later phases and
it truncates the prompt without an error.

```bash
ollama pull qwen2.5:3b
ollama pull llama3.1
ollama create qwen2.5-3b-16k -f Modelfile.qwen
ollama create llama3.1-16k -f Modelfile
```

**Configuration.** `src/software_factory/llm.py` defines `reasoning_llm`
(endpoint 1) and `coder_llm` (endpoint 2). URL and model come from `.env`;
without a `.env` the defaults below are used.

```bash
cp .env.example .env
```
```
ENDPOINT_1_URL=http://localhost:11434
ENDPOINT_1_MODEL=qwen2.5-3b-16k:latest
ENDPOINT_2_URL=http://localhost:11435
ENDPOINT_2_MODEL=llama3.1-16k:latest
```

Which role uses which endpoint is set by `llm=` in each file in
`src/software_factory/agents/`. temperature 0.2 and max_tokens 2048 are set
in `llm.py`.

**Check:**

```bash
uv run python -m software_factory.test_flow   # CrewAI Flow runs
uv run python -m software_factory.test_llm    # both endpoints answer, prints model + URL
```

**Target repo.** The factory changes a separate git repo, not itself.
It must be:
- a git repo with at least one commit, a clean working tree, on its main branch
- small: the whole repo goes into every prompt, files are cut at 4000 characters
- tests using only the standard library and the repo's own files: pytest runs
  with the factory's Python, not a venv of the target. A flat layout is simplest;
  with `src/`, the tests must make their imports work themselves

Example:

```bash
mkdir ~/testcrew && cd ~/testcrew && git init
printf 'def greet(name):\n    return f"Hello {name}"\n' > greeting.py
printf 'from greeting import greet\n\n\ndef test_greet():\n    assert greet("Bob") == "Hello Bob"\n' > test_greeting.py
printf '__pycache__/\n.DS_Store\n' > .gitignore
git add . && git commit -m "Initial"
```

The `.gitignore` matters: the review step runs `git add -A`.

---

## 2. Run

### Demo (no setup of a target repo needed)

From the `CrewAIWorkflow` folder, with both endpoints running:

```bash
uv run python -m software_factory.demo            # uses crewai-demo next to CrewAIWorkflow
uv run python -m software_factory.demo ~/my-demo  # or another folder
```

The demo creates the target repo itself (`greeting.py` with `greet(name)`
and one test) if the folder does not exist, runs the six phases with the
farewell task below, and asks y/n at the review step. It ends with a
reality check done by git and pytest, not by the agents: all six artifacts
written, code changed, tests pass, a farewell test exists. To run it again,
answer n and delete the folder, or answer y and run again (it switches back to
`main`).

### Your own repo and task

```bash
uv run software-factory 2>&1 | tee run-$(date +%H%M).log
```

It asks two questions:

```
Path to target repository: /Users/<you>/testcrew
Feature request: Add a function farewell(name) in greeting.py that returns "Goodbye {name}", and a pytest test for it in test_greeting.py.
```

Use an absolute path. The request is one line; name the files and keep it small.
A run takes 7–16 minutes with two endpoints, depending on the task (about 20
with the 8B model for every role).

| Step | Who | Output in the target repo |
|---|---|---|
| start | Python | branch `factory/<timestamp>` |
| Phase 1 | Architect | `docs/factory/architecture.md` |
| Phase 2 | Tech Lead | `docs/factory/tickets.md` |
| Phase 3 | 2 workers in parallel, write files with `write_repository_file` | code changes, `implementation.md` |
| Phase 4 | Python runs pytest + ruff, then QA | `quality_report.md` |
| Phase 5 | Documentation | `documentation.md` |
| Phase 6 | Deployment | `deployment_checklist.md` |
| Review | Python | shows `git diff`, asks `Commit these changes? (y/n)` |

**Before answering y/n**, in another terminal:

```bash
cd ~/testcrew && git diff --cached --stat     # code files must be listed, not only docs/factory/
grep -c "Tool Execution Completed" run-*.log  # real tool calls
```

`y` commits on the factory branch, `n` leaves the changes uncommitted.

**Throw a run away / run again:**

```bash
git reset --hard && git clean -fd   # only after n
git checkout main && git branch -D factory/<timestamp>
```


## 3. How it works

```
feature request
  -> Architect        architecture proposal
  -> Tech Lead        tickets
  -> 2 coding workers code changes (parallel threads)
  -> QA               quality report (on real pytest + ruff output)
  -> Documentation    docs
  -> Deployment       deployment checklist
  -> Review           git diff, commit y/n
```

- A CrewAI Flow (`flow.py`) runs the phases in order. Each agent is one file in
  `agents/` with a role, goal and task prompt, run as a one-agent Crew.
- `WorkflowState` (Pydantic, `state.py`) carries every phase's output to the next.
- **Design principle: the model reasons, Python does the repository work.**
  Python reads the repo into every prompt (`read_repository()`), runs pytest and
  ruff, writes the artifacts and handles git. The only tool a model calls is
  `write_repository_file` (workers only).
- Workers share one working directory (no worktrees) and both get the whole plan.

---

## 4. Changes since the initial commit

**Starting point**. The full
pipeline existed: the flow, 6 agents, two parallel workers, `tools/` for files,
git and shell, and a demo, with `llama3.1` on one Ollama endpoint. Problems found:

- The agents had no access to the target repo. `tools/` was never used; agents
  only got the path as text, so everything they "did" was invented.
- Ollama's default context window was too small; prompts were silently cut.
- No check that the repo path exists. `tools/git.py` and `state.artifacts` unused.
- `demo.py` targeted a `../my-project` that did not exist, with a JWT-login task.
- `__pycache__`, `.pyc`, `egg-info` and `.idea` committed, no `.gitignore`, empty README.

**What changed, per file** (initial commit → now)

| File | Change |
|---|---|
| `llm.py` | One `local_llm` (`llama3.1`, no settings) → two endpoints, `reasoning_llm` (11434, qwen2.5 3B) and `coder_llm` (11435, llama3.1 8B), URL and model from `.env`; temperature 0.2, max_tokens 2048 |
| `flow.py` | Creates a branch `factory/<timestamp>` before phase 1; saves each phase's output to `docs/factory/*.md` and `state.artifacts`; new review phase shows the diff and asks before committing |
| `main.py` | Stops with a message if the repo path does not exist |
| `demo.py` | Rewritten: creates its own test repo, runs the farewell task, ends with a git/pytest reality check instead of marking phases PASS for producing text |
| `agents/*.py` (all 6) | Every prompt gets the real repo content (`read_repository()`); Architect, Tech Lead, QA, Documentation and Deployment use `reasoning_llm` |
| `agents/coding_worker.py` | Uses `coder_llm`; gets the `write_repository_file` tool and "writing code in your answer does NOT change the repository"; no longer told to run tests or static checks itself |
| `agents/qa.py` | Python runs pytest and ruff (without cache files) before the agent; the real output goes in the prompt with "base results ONLY on the runs above" |
| `tools/filesystem.py` | New `read_repository()`: the whole target repo as text, 4000 chars per file, skipping hidden files, `__pycache__` and `docs/factory/` |
| `tools/crew_tools.py` | New: `write_repository_file`, the only CrewAI tool, used by the workers |
| `test_llm.py` | Tests both endpoints and prints model and URL for each |
| `Modelfile`, `Modelfile.qwen` | New: 16k-context versions of llama3.1 and qwen2.5 3B |
| `.env.example` | New: endpoint URLs and models |
| `.gitignore` | New: `.venv`, `.env`, `__pycache__`, `*.pyc`, `egg-info`, `.idea` |
| `README.md` | Was empty; now setup, run guide, changes, runs, findings |
| `runs/` | New: logs of runs 5–7 and run 7's output |
| removed from git | 32 `.pyc`, `egg-info` and `.idea` files (still ignored locally) |

Unchanged: `state.py`, `implementation.py`, `test_flow.py`, `tools/git.py`,
`tools/shell.py`, `pyproject.toml`, `uv.lock`.

**In what order, and why**

| # | Change | Why |
|---|---|---|
| 1 | Wrapped `tools/` as CrewAI `@tool`s for all agents (later replaced by changes 2–4) | give agents real access (run 1: failed, see below) |
| 2 | `read_repository()`: Python puts every file of the target repo in every prompt, fresh each phase (skips hidden files and `__pycache__`; 4000 chars per file) | the model would not call read tools |
| 3 | QA: Python runs `pytest` before the agent and puts the real output in the prompt; "base results ONLY on this run" | QA invented test runs |
| 4 | Workers get one tool only, `write_repository_file`, plus "writing code in your answer does NOT change the repository" | fewer tools, fewer wrong choices |
| 5 | `Modelfile` → `llama3.1-16k` (num_ctx 16384) | silent truncation |
| 6 | temperature 0 → 0.2, max_tokens 2048 | at 0 the Tech Lead looped until Ollama timed out |
| 7 | `main.py` stops if the repo path does not exist; `.gitignore` added | |
| — | *committed as `ed5c685 "fix-ish"` (2026-10-05)* | |
| 8 | QA also runs `ruff check`; pytest/ruff run without cache files | static analysis requirement |
| 9 | Each phase's output saved to `docs/factory/*.md` and `state.artifacts`; `read_repository()` skips `docs/factory/` | artifacts as files, without feeding agents their own output twice |
| 10 | Branch `factory/<timestamp>` before phase 1; review phase shows the diff and asks before committing | control + reviewable diffs |
| 11 | Two endpoints: `reasoning_llm` / `coder_llm` in `llm.py` from `.env`, `Modelfile.qwen`, `.env.example`, `test_llm` checks both (2026-10-06) | match the group synopsis: same models and roles as the OpenHands setup |
| 12 | `demo.py` rewritten: creates its own target repo, runs the farewell task, ends with a git/pytest reality check (the old one targeted a missing `../my-project` with a JWT task, described unbuilt worktrees, and marked phases PASS for producing any text) | a demo a third party can run |

Cleanup (2026-10-06): the 32 `.pyc`, `egg-info` and `.idea` files from the
initial commit were untracked (`.gitignore` alone does not untrack them), and
the notes files were merged into this README.

---

## 5. Runs and results

Runs 1–6 against a tiny test repo (one function, one test), task: add a
function with a test. Run 7: a calculator from an empty repo. Runs 1–5:
llama3.1 8B for every role on one endpoint. Runs 6–7: two endpoints. Runs 1–4
are from notes taken at the time; full terminal logs of runs 5–7 are in `runs/`.

**Run 1 — tools given to all agents** (change 1). All 6 phases finished, **0
tool calls**. Llama wrote calls as text (`{"name": "list_repository_files",
"parameters": {}}`) and invented the results: the Architect "saw" README.md,
requirements.txt, utils.py and tests/ (none existed). The errors carried
through every phase: tickets for invented files, workers reporting changes
that never happened, QA "running pytest" without running anything, docs for a
non-existent API. A direct call to Ollama with a short prompt and one tool
*did* produce a real tool call; CrewAI's long prompts are what lose the small model.

**Run 2 — repo in prompt, temperature 0.** Tech Lead repeated itself for 10
minutes until Ollama returned HTTP 500; CrewAI retried with the same result.
Fixed with temperature 0.2 and max_tokens 2048. A single-worker test afterwards
called the tool and wrote correct code.

**Run 3 — changes 2–7.** ~20 min. 6 tool calls, source and test file correct,
pytest 2 passed, QA correct (and honest that integration tests and static
analysis were not run). Still wrong: a worker added a broken, unrequested
`setup.py`; Documentation and Deployment invented env vars and a `pip install`,
turning a two-line script into a "service".

**Run 4 — plus ruff, artifacts, branch, review** (changes 8–10). Branch, 6
artifacts, diff and commit worked; pytest and ruff reported correctly. But
workers made **0 tool calls** and claimed changes to 3 files and a "Greeting
Service". QA did not notice (the old test still passed). Only the git diff in
the review showed that no code changed.

**Run 5 — same setup, fresh repo** (`greeting.py`, farewell task). ~20 min.
- Architect invented a separate `farewell.py`; Tech Lead made 5 tickets for a
  two-line change, one being "Implement farewell.py".
- API Worker: 2 real tool calls, both files correct. Backend Worker: 0, wrote the
  calls as JSON text and reported them done. Both claimed tickets 1–2, none did 3–5.
- pytest 2 passed, ruff 1 error (I001 unsorted import); QA reported both correctly
  but listed the non-existent `farewell.py` with contents.
- Documentation and Deployment built on `farewell.py`, `requirements.txt` and a
  README that do not exist; Deployment marked every check "Passed".
- `git add -A` also committed `__pycache__` and `.DS_Store`.

**Run 6 — two endpoints** (change 11), same task and repo state as run 5. 7.5 min.
- Architect (qwen 3B) accurate: two files, no invented components.
- Tech Lead: 4 tickets, 3 and 4 duplicates of 1 and 2.
- 4 real tool calls: **both** workers wrote both files with identical content
  (no file ownership; last writer wins).
- Same correct diff as run 5. pytest 2 passed, ruff 1 error; QA correct, no
  invented files.
- Documentation: nothing invented, but the document repeated 3 times (250 lines).
- Deployment: generic invented checklist (Ubuntu 20.04, database, API keys,
  health-check scripts) and claimed the code was "committed and pushed" (it was not).

**Run 7 — calculator without a spec**, two endpoints. The OpenHands half of
the group built a CLI calculator from a detailed `TASK.md` with stubs and 11
ready-made tests. Run 7 gives CrewAI the same calculator with **no `TASK.md`,
no stubs, no tests**: an empty repo and a one-line request naming only the
files and functions (`src/calc/ops.py` with add/subtract/multiply/divide,
`src/calc/cli.py` with `main(argv)`, `run.py` as entry point, add tests).
Afterwards the OpenHands tests were run as hidden acceptance tests. 16 min.
Output and log in `runs/run7-output/` and `runs/run7.log`.
- Architect redesigned the request: moved `main(argv)` from `cli.py` to
  `run.py`, invented `perform_operation()` in ops.py and `execute_operation()`
  in cli.py. Tech Lead made 4 tickets from that design (`run.py` as a ticket of its own).
- Workers: 12 real tool calls; both workers wrote all six files (`ops.py`,
  `cli.py`, `run.py` and three test files). `run.py` ended up in `src/calc/`,
  not the root.
- The code runs only as `from src.calc...` imports. `main()` never converts
  the arguments to numbers: `main(["add", "2", "3"])` prints `Result: 23`
  (string concatenation). `python run.py add 2 3` does not exist;
  `python src/calc/run.py` fails with `No module named 'src'`.
- Workers' own tests: **11 passed**. But `test_run.py` never calls `main()`:
  it writes "5" to `output.txt` and reads it back. Running it created
  `output.txt` in the repo. The cli tests call `execute_operation()` with ints,
  so the string bug is never hit.
- ruff: 7 errors. QA: "No test failures were reported", no risk named
  beyond generic ones.
- Hidden OpenHands tests: **6 of 11**. All 6 ops tests pass. All 5 cli tests
  fail at import, because `cli.py` has no `main()`. (OpenHands with `TASK.md`: 10 of 11.)
- Documentation and Deployment: no invented services this time, but
  `pip install -r requirements.txt` (no such file), and the checklist treats
  the test leftover `output.txt` as part of the deployment.
- Takeaway: without a spec, the agents' own plan replaced the user's
  request, and green self-written tests hid a calculator that does not
  calculate. With a spec and fixed tests, the OpenHands pipeline got 10 of 11
  with the same models (its latest run, as reported in the group repo).

| | Run 1 | Run 3 | Run 4 | Run 5 | Run 6 (2 endpoints) | Run 7 (calculator, no spec) |
|---|---|---|---|---|---|---|
| Tool calls | 0 | 6 | 0 | 2 (1 of 2 workers) | 4 (both workers) | 12 (both workers) |
| Files changed correctly | 0 | 2 | 0 | 2 | 2 | ops.py only |
| Tests actually run | no | yes, 2 passed | yes, 1 passed | yes, 2 passed | yes, 2 passed | yes, 11 passed (own); hidden 6/11 |
| QA report correct | no | yes | no (trusted workers) | partly (invented file) | yes | no (missed broken main) |
| Invented files in analysis | yes | no | – | yes | no | invented functions, moved main() |
| Invented content in docs/deployment | yes | yes, less | yes | yes | deployment only | requirements.txt |
| Duration | – | ~20 min | ~20 min | ~20 min | 7.5 min | 16 min |

---

## 6. Findings

**What breaks first**
1. **Tool calling.** The 8B model writes the call as text instead of making it
   (run 1 all agents, run 4 both workers, run 5 one worker). Same setup gives
   6 calls one run and 0 the next.
2. **Hallucination that spreads.** Each phase builds on the last one's text. In
   run 5 `farewell.py`, invented by the Architect, reached tickets, worker
   report, QA, docs and deployment. In run 6 a correct architecture kept the
   later phases honest about files.
3. **Endless generation** at temperature 0.
4. **Silent context loss**: Ollama's default context, 4000 chars per file.
5. **Scope creep / duplication**: unrequested `setup.py` (run 3), duplicate
   tickets and both workers doing the same work (run 6).
6. **Free-text phases invent.** Documentation and Deployment are never checked
   against the code; Deployment reported checks as "Passed" that never ran (runs 5, 6).
7. **`git add -A`** commits whatever is in the target repo (run 5).

**Detection and recovery**
- Python runs tests and lint, so test results cannot be invented.
- The git diff in the review step is the only thing that catches "workers
  claimed changes but wrote nothing" (run 4). Bad run: answer n, delete the branch.
- max_tokens stops endless generation.
- Not built: Python checking the diff after the workers and giving QA the real
  list of changed files (the OpenHands pipeline does the equivalent: it checks
  each stage's expected files and re-prompts).

**Testing moved out of the agent — a tradeoff.** Python, not the QA agent, runs
pytest and ruff. Test results became impossible to fabricate, but QA is reduced
to a reporting role: no run-fix loop, the command is fixed to pytest/ruff, and
QA can still repeat invented claims from the workers (run 5). The OpenHands
setup converged on the same design (the orchestrator runs tests and
`validate.sh`, agents report on the real output), which suggests it is a
property of small local models rather than of either toolchain.

**A spec matters more than the toolchain.** In the OpenHands pipeline the
coders read only `TASK.md` ("the exact names … are in TASK.md and nowhere
else"); the Architect documents the workflow system and the Tech Lead writes
tickets, but neither changes what gets built. That gave 10/11 hidden tests.
In CrewAI the Architect and Tech Lead really decide what the workers build,
which is closer to a real multi-agent team but lets planning errors reach the
code: `farewell.py` (run 5), duplicate tickets (run 6), and in run 7 a
redesign that moved `main()` and broke 5 of 11 tests. Self-written tests do
not catch this: run 7's 11 green tests included one that never called the
code. Tradeoff: agent planning vs reliability.

**Other points**
- Moving deterministic work from the model to Python was the biggest single
  improvement: same model, from 0 to 2 correct files.
- The prompts are written for big projects (APIs, deployment, env vars). On a
  small project the model fills the gaps instead of saying "not relevant".
- Same structure every run, different outcome. Human review of the diff is still needed.
- Two endpoints with a small model for the non-coding roles was both faster
  (7.5 vs ~20 min) and, in this run, more accurate than 8B for everything.
  One run each, so not conclusive.

---

## 7. Requirements status

| Requirement | Status |
|---|---|
| 2 local endpoints, config-driven | Yes (run 6). URL/model per endpoint in `.env`; role→endpoint binding is `llm=` in code. OpenHands puts the role mapping in `.env` via LiteLLM aliases. |
| Open source | Yes: CrewAI (MIT), Ollama (MIT). Models are open weights, not OSI: Llama 3.1 (Llama community licence), Qwen2.5 3B (Qwen research licence) |
| Architecture | `architecture.md`; no separate OpenAPI file, ADRs are a section |
| Tech lead | tickets with scope, acceptance criteria, DoD, dependencies, order; free text, not parsed |
| Implementation N≥2 | 2 parallel workers, multi-file changes; shared directory, no worktrees, no file ownership |
| Testing & quality | pytest + ruff run for real, QA report; QA writes no tests, no fix loop |
| Documentation | `documentation.md`; the repo README is deliberately not touched (the agent invents) |
| Deployment validation | checklist only, no script or container build; content invented |
| Control | branch + plan + diff before commit; no ask-before-edit |
| Reproducibility | same structure every run (branch, 6 files, diff); content not reproducible |
| Context management | explicit handoff via `WorkflowState`, repo snapshot per prompt, 16k context, 2048-token answers. Breaks on real-sized repos (whole repo + earlier outputs must fit in 16k, silent 4000-char cut). Fix would be files per ticket or search. |
| Security | Ollama on localhost only, no keys; the model cannot run shell commands |

---


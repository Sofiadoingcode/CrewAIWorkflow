# demo.py

import json
import traceback
from pprint import pprint

from software_factory.flow import SoftwareFactoryFlow


# ============================================================
# Pretty printing helpers
# ============================================================

def banner(title: str):
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print(f"║ {title:<76} ║")
    print("╚" + "═" * 78 + "╝")


def section(title: str):
    print("\n" + "─" * 80)
    print(f"▶ {title}")
    print("─" * 80)


def print_value(label: str, value):
    print(f"\n{label}:")
    print("  " + "-" * 72)

    if isinstance(value, (dict, list)):
        try:
            formatted = json.dumps(value, indent=2, default=str)
            for line in formatted.splitlines():
                print("  " + line)
        except Exception:
            pprint(value)
    else:
        print(f"  {value}")

    print("  " + "-" * 72)


def check(label: str, condition: bool):
    status = "✓ PASS" if condition else "✗ EMPTY"
    print(f"  [{status}] {label}")


# ============================================================
# Main demo
# ============================================================

def main():

    banner("AI SOFTWARE FACTORY — LIVE DEMONSTRATION")

    print(
        """
This demo showcases the complete multi-agent software engineering workflow.

                  ┌──────────────────────┐
                  │   Feature Request    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   SOFTWARE ARCHITECT │
                  │                      │
                  │ Architecture + ADRs  │
                  │ APIs + Deployment    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │     TECH LEAD        │
                  │                      │
                  │ Tickets + Scope      │
                  │ Dependencies + DoD   │
                  └──────────┬───────────┘
                             │
                             ▼
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
       ┌───────────────┐             ┌───────────────┐
       │ CODING WORKER │             │ CODING WORKER │
       │       #1      │             │       #2      │
       └───────┬───────┘             └───────┬───────┘
               │                             │
               └──────────────┬──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ QA / INTEGRATION │
                    │                  │
                    │ Tests + Quality  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ DOCUMENTATION    │
                    │                  │
                    │ README + API     │
                    │ Runbook          │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ DEPLOYMENT       │
                    │ VALIDATION       │
                    │                  │
                    │ Config + Checks  │
                    └──────────────────┘

The important idea:

CrewAI performs the reasoning and agent orchestration.
Deterministic Python/Git/shell operations perform actual repository work.
"""
    )

    # ========================================================
    # Demo input
    # ========================================================

    banner("1. FEATURE REQUEST")

    repo_path = "../my-project"

    feature_request = """
Build user authentication for the application.

Requirements:

1. Users can register using email and password.
2. Users can log in using email and password.
3. The API uses JWT authentication.
4. Passwords must be securely hashed.
5. Protected API endpoints reject unauthenticated requests.
6. Add automated tests.
7. Document the authentication API.
8. Provide deployment/environment configuration.
"""

    print_value("Repository", repo_path)
    print_value("Requested feature", feature_request)

    # ========================================================
    # Create workflow
    # ========================================================

    banner("2. STARTING SOFTWARE FACTORY")

    print("Creating SoftwareFactoryFlow...")

    try:
        flow = SoftwareFactoryFlow()

        print("✓ Flow created successfully.")
        print(f"  Flow type: {type(flow).__name__}")

    except Exception as exc:
        print("✗ Could not create flow.")
        print(f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        return

    # ========================================================
    # Run workflow
    # ========================================================

    banner("3. EXECUTING MULTI-AGENT WORKFLOW")

    print(
        """
The following phases will now execute:

  [1] Architecture
  [2] Technical planning
  [3] Parallel implementation
  [4] QA / testing
  [5] Documentation
  [6] Deployment validation

CrewAI's verbose output will appear below.
"""
    )

    try:

        result = flow.kickoff(
            inputs={
                "repo_path": repo_path,
                "feature_request": feature_request,
            }
        )

        print("\n✓ FLOW EXECUTION FINISHED")

    except Exception as exc:

        print("\n✗ FLOW EXECUTION FAILED")
        print(f"\nException: {type(exc).__name__}: {exc}")

        print("\nFull traceback:")
        traceback.print_exc()

        print(
            """
The workflow failed, but we will still inspect the state that
was produced before the failure.
"""
        )

        result = None

    # ========================================================
    # Architecture
    # ========================================================

    banner("4. ARCHITECTURE ARTIFACT")

    architecture = getattr(flow.state, "architecture", None)

    if architecture:
        print_value("Architecture", architecture)

        print(
            """
This artifact demonstrates the Architecture responsibility:

  ✓ Component decomposition
  ✓ Component responsibilities
  ✓ API/interface contracts
  ✓ Deployment topology
  ✓ Architecture decisions
  ✓ Risks and assumptions
"""
        )
    else:
        print("No architecture artifact was produced.")

    # ========================================================
    # Technical planning
    # ========================================================

    banner("5. TECHNICAL LEAD / TICKET PLAN")

    tickets = getattr(flow.state, "tickets", None)

    if tickets:
        print_value("Implementation tickets", tickets)

        print(
            """
The technical lead is expected to establish:

  ✓ Incremental tickets
  ✓ Clear scope boundaries
  ✓ Out-of-scope boundaries
  ✓ Acceptance criteria
  ✓ Definition of Done
  ✓ Dependencies
  ✓ File/path ownership

This allows implementation work to be split between workers
without having every worker modify the same files.
"""
        )

    else:
        print("No ticket plan was produced.")

    # ========================================================
    # Worker results
    # ========================================================

    banner("6. PARALLEL IMPLEMENTATION WORKERS")

    worker_results = getattr(flow.state, "worker_results", None)

    if worker_results:

        print_value("Coding worker results", worker_results)

        print(
            """
The implementation stage is designed around multiple workers.

Conceptually:

       TECH LEAD
           │
           ├───────────────┐
           │               │
           ▼               ▼
      Worker #1       Worker #2
           │               │
           ▼               ▼
       Worktree #1     Worktree #2
           │               │
           └───────┬───────┘
                   ▼
              Integration

Using isolated worktrees prevents workers from accidentally
overwriting each other's changes.
"""
        )

    else:
        print(
            """
No worker results are currently stored in the state.

This is expected if the current flow.py only implements
architecture and planning so far.
"""
        )

    # ========================================================
    # Quality
    # ========================================================

    banner("7. QA / QUALITY REPORT")

    quality = getattr(flow.state, "quality_report", None)

    if quality:
        print_value("Quality report", quality)

        print(
            """
The QA stage should demonstrate:

  ✓ Automated test execution
  ✓ Test results
  ✓ Static checks
  ✓ Integration checks
  ✓ Detected risks
  ✓ Remaining issues
"""
        )

    else:
        print("No quality report was produced yet.")

    # ========================================================
    # Documentation
    # ========================================================

    banner("8. DOCUMENTATION ARTIFACT")

    documentation = getattr(flow.state, "documentation", None)

    if documentation:
        print_value("Documentation", documentation)

        print(
            """
Documentation should cover:

  ✓ README changes
  ✓ API usage
  ✓ Configuration
  ✓ Operational/runbook information
  ✓ Architecture/design documentation
"""
        )

    else:
        print("No documentation artifact was produced yet.")

    # ========================================================
    # Deployment
    # ========================================================

    banner("9. DEPLOYMENT VALIDATION")

    deployment = getattr(flow.state, "deployment_validation", None)

    if deployment:
        print_value("Deployment validation", deployment)

        print(
            """
Deployment validation should demonstrate:

  ✓ Required environment variables
  ✓ Deployment configuration
  ✓ Startup checks
  ✓ Health checks
  ✓ Configuration validation
  ✓ Deployment checklist
"""
        )

    else:
        print("No deployment validation artifact was produced yet.")

    # ========================================================
    # Final state
    # ========================================================

    banner("10. COMPLETE WORKFLOW STATE")

    print("Final state object:")

    try:
        if hasattr(flow.state, "model_dump"):
            pprint(flow.state.model_dump())

        elif hasattr(flow.state, "dict"):
            pprint(flow.state.dict())

        else:
            pprint(flow.state)

    except Exception as exc:
        print(f"Could not serialize state: {exc}")

    # ========================================================
    # Pipeline health
    # ========================================================

    banner("11. PIPELINE HEALTH CHECK")

    check(
        "Workflow object created",
        flow is not None,
    )

    check(
        "Feature request available",
        bool(getattr(flow.state, "feature_request", "")),
    )

    check(
        "Repository path available",
        bool(getattr(flow.state, "repo_path", "")),
    )

    check(
        "Architecture produced",
        bool(getattr(flow.state, "architecture", None)),
    )

    check(
        "Technical plan produced",
        bool(getattr(flow.state, "tickets", None)),
    )

    check(
        "Implementation results produced",
        bool(getattr(flow.state, "worker_results", None)),
    )

    check(
        "Quality report produced",
        bool(getattr(flow.state, "quality_report", None)),
    )

    check(
        "Documentation produced",
        bool(getattr(flow.state, "documentation", None)),
    )

    check(
        "Deployment validation produced",
        bool(getattr(flow.state, "deployment_validation", None)),
    )

    # ========================================================
    # Final summary
    # ========================================================

    banner("12. DEMO COMPLETE")

    print(
        """
Software Factory architecture demonstrated:

  FEATURE
     │
     ▼
  ARCHITECT
     │
     │ architecture / interfaces / deployment / ADRs
     ▼
  TECH LEAD
     │
     │ tickets / acceptance criteria / dependencies
     ▼
  CODING WORKERS
     │
     │ parallel implementation
     ▼
  QA
     │
     │ tests / static analysis / quality report
     ▼
  DOCUMENTATION
     │
     │ README / API docs / runbook
     ▼
  DEPLOYMENT VALIDATION
     │
     │ configuration / checks / deployment readiness
     ▼
  COMPLETED SOFTWARE CHANGE

This is the complete architecture we are building toward.
"""
    )

    print("\nRaw CrewAI result:")
    pprint(result)

    print("\n")
    print("=" * 80)
    print("END OF DEMO")
    print("=" * 80)


if __name__ == "__main__":
    main()
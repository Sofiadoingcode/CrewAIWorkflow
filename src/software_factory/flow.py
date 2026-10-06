from datetime import datetime

from crewai.flow.flow import Flow, start, listen

from .state import WorkflowState
from .tools.filesystem import write_file
from .tools.git import create_branch, git
from .implementation import run_parallel_workers

from .agents.architect import run_architect
from .agents.tech_lead import run_tech_lead
from .agents.qa import run_qa
from .agents.documentation import run_documentation
from .agents.deployment import run_deployment


class SoftwareFactoryFlow(Flow[WorkflowState]):

    def save_artifact(self, name, content):

        path = write_file(
            self.state.repo_path,
            f"docs/factory/{name}",
            str(content),
        )

        self.state.artifacts[name] = path

    @start()
    def architecture_phase(self):

        branch = "factory/" + datetime.now().strftime("%Y%m%d-%H%M%S")

        result = create_branch(self.state.repo_path, branch)

        if result["success"]:
            print(f"Working on branch {branch}")
        else:
            print(f"Could not create branch {branch}: {result['stderr'].strip()}")

        print("\n" + "=" * 80)
        print("PHASE 1 — ARCHITECTURE")
        print("=" * 80)

        architecture = run_architect(
            repo_path=self.state.repo_path,
            feature_request=self.state.feature_request,
        )

        self.state.architecture = architecture

        self.save_artifact("architecture.md", architecture["proposal"])

        return architecture

    @listen(architecture_phase)
    def planning_phase(self, architecture):

        print("\n" + "=" * 80)
        print("PHASE 2 — TECHNICAL PLANNING")
        print("=" * 80)

        tickets = run_tech_lead(
            repo_path=self.state.repo_path,
            feature_request=self.state.feature_request,
            architecture=architecture,
        )

        self.state.tickets = [tickets]

        self.save_artifact("tickets.md", tickets["plan"])

        return tickets

    @listen(planning_phase)
    def implementation_phase(self, tickets):

        print("\n" + "=" * 80)
        print("PHASE 3 — PARALLEL IMPLEMENTATION")
        print("=" * 80)

        results = run_parallel_workers(
            state=self.state,
            tickets=tickets,
        )

        self.state.worker_results = results

        self.save_artifact(
            "implementation.md",
            "\n\n".join(
                f"# {result['worker']}\n\n{result['result']}"
                for result in results
            ),
        )

        return results

    @listen(implementation_phase)
    def quality_phase(self, worker_results):

        print("\n" + "=" * 80)
        print("PHASE 4 — QUALITY ASSURANCE")
        print("=" * 80)

        report = run_qa(
            repo_path=self.state.repo_path,
            feature_request=self.state.feature_request,
            architecture=self.state.architecture,
            tickets=self.state.tickets,
            worker_results=worker_results,
        )

        self.state.quality_report = report

        self.save_artifact("quality_report.md", report["report"])

        return report

    @listen(quality_phase)
    def documentation_phase(self, quality_report):

        print("\n" + "=" * 80)
        print("PHASE 5 — DOCUMENTATION")
        print("=" * 80)

        documentation = run_documentation(
            repo_path=self.state.repo_path,
            feature_request=self.state.feature_request,
            architecture=self.state.architecture,
            worker_results=self.state.worker_results,
            quality_report=quality_report,
        )

        self.state.documentation = documentation

        self.save_artifact("documentation.md", documentation["report"])

        return documentation

    @listen(documentation_phase)
    def deployment_phase(self, documentation):

        print("\n" + "=" * 80)
        print("PHASE 6 — DEPLOYMENT VALIDATION")
        print("=" * 80)

        deployment = run_deployment(
            repo_path=self.state.repo_path,
            feature_request=self.state.feature_request,
            architecture=self.state.architecture,
            quality_report=self.state.quality_report,
            documentation=documentation,
        )

        self.state.deployment_validation = deployment

        self.save_artifact("deployment_checklist.md", deployment["report"])

        return deployment

    @listen(deployment_phase)
    def review_phase(self, deployment):

        print("\n" + "=" * 80)
        print("REVIEW — CHANGES IN TARGET REPOSITORY")
        print("=" * 80)

        repo_path = self.state.repo_path

        if not git(repo_path, "add", "-A")["success"]:
            print("Target repository is not a git repository, nothing to review.")
            return deployment

        print(git(repo_path, "diff", "--cached", "--stat")["stdout"])
        print(git(repo_path, "diff", "--cached")["stdout"])

        answer = input("Commit these changes? (y/n): ").strip().lower()

        if answer == "y":
            result = git(
                repo_path,
                "commit",
                "-m",
                f"Software factory: {self.state.feature_request.strip()}",
            )
            print(result["stdout"] or result["stderr"])
        else:
            git(repo_path, "reset")
            print("Not committed. The changes are left in the working tree.")

        return deployment
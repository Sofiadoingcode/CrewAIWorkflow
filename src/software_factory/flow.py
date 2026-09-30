from crewai.flow.flow import Flow, start, listen

from .state import WorkflowState
from .implementation import run_parallel_workers

from .agents.architect import run_architect
from .agents.tech_lead import run_tech_lead
from .agents.qa import run_qa
from .agents.documentation import run_documentation
from .agents.deployment import run_deployment


class SoftwareFactoryFlow(Flow[WorkflowState]):

    @start()
    def architecture_phase(self):

        print("\n" + "=" * 80)
        print("PHASE 1 — ARCHITECTURE")
        print("=" * 80)

        architecture = run_architect(
            repo_path=self.state.repo_path,
            feature_request=self.state.feature_request,
        )

        self.state.architecture = architecture

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

        return deployment
from typing import Any

from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    repo_path: str = ""
    feature_request: str = ""

    architecture: dict[str, Any] = Field(default_factory=dict)

    tickets: list[dict[str, Any]] = Field(
        default_factory=list
    )

    worker_results: list[dict[str, Any]] = Field(
        default_factory=list
    )

    quality_report: dict[str, Any] = Field(
        default_factory=dict
    )

    documentation: dict[str, Any] = Field(
        default_factory=dict
    )

    deployment_validation: dict[str, Any] = Field(
        default_factory=dict
    )

    artifacts: dict[str, str] = Field(
        default_factory=dict
    )
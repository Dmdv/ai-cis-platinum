"""
Tool contract — every external action an agent can take is wrapped in a Tool.

Tools declare a `risk_level` that the Supervisor enforces. `dangerous` tools
require explicit chemist approval before execution, regardless of the agent's
plan. The audit log records every invocation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Generic, Literal, Protocol, TypeVar

from pydantic import BaseModel


RiskLevel = Literal["safe", "moderate", "dangerous"]


class AuditRecord(BaseModel):
    tool_name: str
    invoked_by_agent: str
    invoked_at: datetime
    request: dict
    response: dict
    risk_level: RiskLevel
    approved_by_user_id: str | None
    duration_ms: int


Req = TypeVar("Req", bound=BaseModel, contravariant=True)
Res = TypeVar("Res", bound=BaseModel, covariant=True)


class Tool(Protocol, Generic[Req, Res]):
    name: str
    description: str
    risk_level: RiskLevel
    requires_human_approval: bool

    def call(self, request: Req) -> Res: ...
    def explain(self, request: Req) -> str: ...
    def audit(self) -> AuditRecord: ...

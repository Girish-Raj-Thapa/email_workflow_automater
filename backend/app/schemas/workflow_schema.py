from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlmodel import SQLModel


class WorkflowItemRead(SQLModel):
    id: UUID
    email_id: UUID
    analysis_id: UUID
    workflow_type: str
    assigned_team: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime


class WorkflowLogRead(SQLModel):
    id: UUID
    workflow_item_id: UUID
    step: str
    details: str
    created_at: datetime


class WorkflowDetailRead(WorkflowItemRead):
    logs: list[WorkflowLogRead]


class WorkflowStatusUpdate(SQLModel):
    status: Literal[
        "open",
        "in_progress",
        "resolved",
        "closed",
        "awaiting_review",
        "escalated",
    ]
    note: str | None = None

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class WorkflowItem(SQLModel, table=True):
    __tablename__ = "workflow_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email_id: UUID = Field(foreign_key="emails.id", unique=True, index=True)
    analysis_id: UUID = Field(foreign_key="ai_email_analyses.id", unique=True, index=True)

    workflow_type: str = Field(max_length=50)
    assigned_team: str = Field(max_length=50)
    priority: str = Field(max_length=20)
    status: str = Field(default="open", max_length=50)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class WorkflowLog(SQLModel, table=True):
    __tablename__ = "workflow_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    workflow_item_id: UUID = Field(foreign_key="workflow_items.id", index=True)

    step: str = Field(max_length=100)
    details: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

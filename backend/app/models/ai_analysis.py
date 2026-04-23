from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, JSON
from sqlmodel import Field, SQLModel


class AIEmailAnalysis(SQLModel, table=True):
    __tablename__ = "ai_email_analyses"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email_id: UUID = Field(foreign_key="emails.id", unique=True, index=True)

    category: str = Field(max_length=50)
    priority: str = Field(max_length=20)
    recommended_action: str = Field(max_length=100)
    assigned_team: str = Field(max_length=50)
    requires_human_review: bool = Field(default=False)
    confidence: float

    extracted_entities: dict[str, Any] = Field(
        sa_column=Column(JSON, nullable=False)
    )
    draft_reply: str

    analyzed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    
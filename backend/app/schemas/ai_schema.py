from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr
from sqlmodel import SQLModel

from app.schemas.email_schema import EmailRead
from app.schemas.reply_schema import ReplyRead
from app.schemas.workflow_schema import WorkflowItemRead


class ExtractedEntities(BaseModel):
    customer_email_in_body: EmailStr | None = None
    mentioned_amount: float | None = None
    payment_method: Literal[
        "credit_card",
        "debit_card",
        "bank_transfer",
        "paypal",
        "unknown",
    ] | None = None
    affected_feature: str | None = None
    subscription_reference: str | None = None


class AIEmailAnalysisBase(SQLModel):
    category: Literal[
        "leave_request",
        "support_issue",
        "billing_issue",
        "general_inquiry",
    ]
    priority: Literal["low", "medium", "high"]
    recommended_action: Literal[
        "create_leave_case",
        "create_support_ticket",
        "create_billing_case",
        "mark_for_manual_review",
    ]
    assigned_team: Literal[
        "hr",
        "technical_support",
        "finance",
        "manual_review",
    ]
    requires_human_review: bool
    confidence: float
    extracted_entities: ExtractedEntities
    draft_reply: str


class AIEmailAnalysisCreate(AIEmailAnalysisBase):
    pass


class AIEmailAnalysisRead(AIEmailAnalysisBase):
    id: UUID
    email_id: UUID
    analyzed_at: datetime


class AnalyzeEmailResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis: AIEmailAnalysisRead
    workflow: WorkflowItemRead | None = None
    reply: ReplyRead | None = None
    filtered: bool = False
    filter_reason: str | None = None


class ProcessEmailResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailRead
    analysis: AIEmailAnalysisRead
    workflow: WorkflowItemRead | None = None
    reply: ReplyRead | None = None
    filtered: bool = False
    filter_reason: str | None = None
    auto_send_executed: bool = False
    auto_send_reason: str | None = None

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel

from app.schemas.email_schema import EmailRead
from app.schemas.reply_schema import SentReplyRead
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
    ] = "unknown"
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


class AnalyzeEmailResult(SQLModel):
    analysis: AIEmailAnalysisRead
    workflow: WorkflowItemRead
    reply: SentReplyRead


class ProcessEmailResult(SQLModel):
    email: EmailRead
    analysis: AIEmailAnalysisRead
    workflow: WorkflowItemRead
    reply: SentReplyRead

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.exceptions import ConflictError
from app.models.ai_analysis import AIEmailAnalysis
from app.models.emails import Email
from app.models.workflow import WorkflowItem, WorkflowLog


ACTION_TO_WORKFLOW_TYPE = {
    "create_leave_case": "leave_case",
    "create_support_ticket": "support_ticket",
    "create_billing_case": "billing_case",
    "mark_for_manual_review": "manual_review",
}


def get_initial_status(priority: str, requires_human_review: bool) -> str:
    if requires_human_review:
        return "awaiting_review"

    if priority == "high":
        return "escalated"

    return "open"


async def create_workflow_from_analysis(
    session: AsyncSession,
    email: Email,
    analysis: AIEmailAnalysis,
) -> WorkflowItem:
    existing_statement = select(WorkflowItem).where(
        WorkflowItem.email_id == email.id
    )
    existing_result = await session.execute(existing_statement)
    existing_workflow = existing_result.scalar_one_or_none()

    if existing_workflow is not None:
        raise ConflictError("Workflow already exists for this email")

    workflow_type = ACTION_TO_WORKFLOW_TYPE.get(
        analysis.recommended_action,
        "manual_review",
    )

    workflow = WorkflowItem(
        email_id=email.id,
        analysis_id=analysis.id,
        workflow_type=workflow_type,
        assigned_team=analysis.assigned_team,
        priority=analysis.priority,
        status=get_initial_status(
            priority=analysis.priority,
            requires_human_review=analysis.requires_human_review,
        ),
    )

    session.add(workflow)
    await session.flush()

    logs = [
        WorkflowLog(
            workflow_item_id=workflow.id,
            step="workflow_created",
            details=f"Workflow created from AI analysis with type '{workflow_type}'.",
        ),
        WorkflowLog(
            workflow_item_id=workflow.id,
            step="assigned_team",
            details=f"Assigned to team '{analysis.assigned_team}'.",
        ),
        WorkflowLog(
            workflow_item_id=workflow.id,
            step="priority_set",
            details=f"Priority set to '{analysis.priority}'.",
        ),
    ]

    if workflow.status == "escalated":
        logs.append(
            WorkflowLog(
                workflow_item_id=workflow.id,
                step="workflow_escalated",
                details="Workflow was automatically escalated due to high priority.",
            )
        )

    if workflow.status == "awaiting_review":
        logs.append(
            WorkflowLog(
                workflow_item_id=workflow.id,
                step="human_review_required",
                details="Workflow requires human review based on AI analysis.",
            )
        )

    for log in logs:
        session.add(log)

    email.processing_status = "routed"
    session.add(email)

    await session.commit()
    await session.refresh(workflow)

    return workflow

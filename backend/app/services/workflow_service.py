from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.exceptions import NotFoundError
from app.models.workflow import WorkflowItem, WorkflowLog
from app.schemas.workflow_schema import WorkflowStatusUpdate


async def list_workflows(session: AsyncSession) -> list[WorkflowItem]:
    statement = select(WorkflowItem).order_by(WorkflowItem.created_at.desc())
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_workflow_by_id(session: AsyncSession, workflow_id: UUID) -> WorkflowItem:
    statement = select(WorkflowItem).where(WorkflowItem.id == workflow_id)
    result = await session.execute(statement)
    workflow = result.scalar_one_or_none()

    if workflow is None:
        raise NotFoundError("Workflow not found")

    return workflow


async def get_workflow_logs(
    session: AsyncSession,
    workflow_id: UUID,
) -> list[WorkflowLog]:
    statement = (
        select(WorkflowLog)
        .where(WorkflowLog.workflow_item_id == workflow_id)
        .order_by(WorkflowLog.created_at.asc())
    )
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_workflow_detail(
    session: AsyncSession,
    workflow_id: UUID,
) -> dict:
    workflow = await get_workflow_by_id(session=session, workflow_id=workflow_id)
    logs = await get_workflow_logs(session=session, workflow_id=workflow_id)

    return {
        **workflow.model_dump(),
        "logs": logs,
    }


async def update_workflow_status(
    session: AsyncSession,
    workflow_id: UUID,
    payload: WorkflowStatusUpdate,
) -> WorkflowItem:
    workflow = await get_workflow_by_id(session=session, workflow_id=workflow_id)

    old_status = workflow.status
    workflow.status = payload.status
    workflow.updated_at = datetime.now(timezone.utc)

    details = f"Workflow status changed from '{old_status}' to '{payload.status}'."
    if payload.note:
        details += f" Note: {payload.note}"

    log = WorkflowLog(
        workflow_item_id=workflow.id,
        step="status_updated",
        details=details,
    )

    session.add(workflow)
    session.add(log)

    await session.commit()
    await session.refresh(workflow)

    return workflow

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.workflow_schema import (
    WorkflowDetailRead,
    WorkflowItemRead,
    WorkflowStatusUpdate,
)
from app.services.workflow_service import (
    get_workflow_detail,
    list_workflows,
    update_workflow_status,
)

router = APIRouter()


@router.get("/workflows", response_model=list[WorkflowItemRead])
async def list_workflows_endpoint(
    session: AsyncSession = Depends(get_session),
):
    return await list_workflows(session=session)


@router.get("/workflows/{workflow_id}", response_model=WorkflowDetailRead)
async def get_workflow_detail_endpoint(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await get_workflow_detail(session=session, workflow_id=workflow_id)


@router.patch("/workflows/{workflow_id}/status", response_model=WorkflowItemRead)
async def update_workflow_status_endpoint(
    workflow_id: UUID,
    payload: WorkflowStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await update_workflow_status(
        session=session,
        workflow_id=workflow_id,
        payload=payload,
    )

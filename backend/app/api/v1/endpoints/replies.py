from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.reply_schema import ReplyRead
from app.schemas.reply_send_schema import ApproveSendReplyRequest
from app.services.reply_send_workflow import approve_and_send_reply, retry_send_reply
from app.services.reply_service import get_reply_by_id, list_replies

router = APIRouter()


@router.get("/replies", response_model=list[ReplyRead])
async def list_replies_endpoint(session: AsyncSession = Depends(get_session)):
    return await list_replies(session=session)


@router.get("/replies/{reply_id}", response_model=ReplyRead)
async def get_reply_by_id_endpoint(reply_id: UUID, session: AsyncSession = Depends(get_session)):
    return await get_reply_by_id(session=session, reply_id=reply_id)


@router.post(
    "/replies/{reply_id}/approve-and-send",
    response_model=ReplyRead,
    status_code=status.HTTP_200_OK,
)
async def approve_and_send_reply_endpoint(
    reply_id: UUID,
    payload: ApproveSendReplyRequest,
    session: AsyncSession = Depends(get_session),
):
    return await approve_and_send_reply(
        session=session,
        reply_id=reply_id,
        approved_by=payload.approved_by,
    )


@router.post(
    "/replies/{reply_id}/retry-send",
    response_model=ReplyRead,
    status_code=status.HTTP_200_OK,
)
async def retry_send_reply_endpoint(
    reply_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await retry_send_reply(
        session=session,
        reply_id=reply_id,
    )

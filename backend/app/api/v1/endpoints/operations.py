from fastapi import APIRouter, status

from app.services.mail_sync_runner import run_mail_sync_once

router = APIRouter()


@router.post("/operations/run-mail-sync", status_code=status.HTTP_202_ACCEPTED)
async def run_mail_sync_endpoint():
    await run_mail_sync_once()
    return {"detail": "Mail sync cycle completed"}
    
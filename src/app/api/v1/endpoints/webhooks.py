from fastapi import APIRouter, Request, Header, HTTPException
from aiogram import types

from app.core.security import verify_hmac_signature
from bots.bot import client_bot, client_dp, worker_bot, worker_dp

router = APIRouter()


@router.post(
    "/client",
    summary="Webhook for the client Telegram bot",
    description="Receives updates from the client Telegram bot. Requests must be signed with an HMAC signature in the `X-Signature` header.",
)
async def client_webhook(request: Request, x_signature: str | None = Header(None)):
    body = await request.body()
    if not verify_hmac_signature(x_signature, body):
        raise HTTPException(status_code=401, detail="Unauthorized")

    update = types.Update(**await request.json())
    await client_dp.feed_update(client_bot, update)
    return {"status": "ok"}


@router.post(
    "/worker",
    summary="Webhook for the worker Telegram bot",
    description="Receives updates from the worker Telegram bot. Requests must be signed with an HMAC signature in the `X-Signature` header.",
)
async def worker_webhook(request: Request, x_signature: str | None = Header(None)):
    body = await request.body()
    if not verify_hmac_signature(x_signature, body):
        raise HTTPException(status_code=401, detail="Unauthorized")

    update = types.Update(**await request.json())
    await worker_dp.feed_update(worker_bot, update)
    return {"status": "ok"}

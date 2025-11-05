from __future__ import annotations

from fastapi import FastAPI, Request
from sqlalchemy import select

from app.bot_app import bot_auth, bot_main, dp_auth, dp_main
from app.config import settings
from app.db import SessionLocal
from app.models.admins import Admin, AdminRole
from app.routers import auth, broadcasts, cashiers, settings as settings_router, users
from app.services.telegram_service import TelegramService

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    if settings.APP_ENV == "prod":
        await TelegramService.set_main_webhook()
        await TelegramService.set_auth_webhook()

    db = SessionLocal()
    try:
        stmt = select(Admin).where(Admin.telegram_id == settings.FIRST_SUPERADMIN_TG_ID)
        super_admin = (await db.execute(stmt)).scalars().first()
        if super_admin is None:
            super_admin = Admin(
                telegram_id=settings.FIRST_SUPERADMIN_TG_ID,
                role=AdminRole.owner,
                is_active=True,
            )
            db.add(super_admin)
            await db.commit()
    finally:
        await db.close()


@app.get("/health")
async def read_health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/bot/main/webhook")
async def main_bot_webhook(request: Request) -> dict[str, str]:
    update = await request.json()
    await dp_main.feed_update(bot_main, update)
    return {"status": "accepted"}


@app.post("/bot/auth/webhook")
async def auth_bot_webhook(request: Request) -> dict[str, str]:
    update = await request.json()
    await dp_auth.feed_update(bot_auth, update)
    return {"status": "accepted"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cashiers.router)
app.include_router(broadcasts.router)
app.include_router(settings_router.router)

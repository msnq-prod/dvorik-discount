from __future__ import annotations

from app.schemas.common import SettingsPatch

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


@router.get("/")
async def list_settings(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_admin_with_role("readonly")),
) -> Dict[str, Any]:
    stmt = select(Setting)
    settings = (await db.execute(stmt)).scalars().all()
    return {setting.key: setting.value for setting in settings}


@router.patch("/")
async def update_settings(
    payload: SettingsPatch,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_with_role("marketing")),
) -> Dict[str, Any]:
    result: dict[str, Any] = {}
    for key, new_value in payload.model_dump(exclude_unset=True).items():
        stmt = select(Setting).where(Setting.key == key)
        setting = (await db.execute(stmt)).scalars().first()
        if setting is None:
            setting = Setting(key=key, value=new_value)
            old_value = None
        else:
            old_value = setting.value
            setting.value = new_value

        result[key] = setting.value

        audit_log = AuditLog(
            admin_id=admin.id,
            action="update_setting",
            payload={"key": key, "old": old_value, "new": new_value},
        )
        db.add(setting)
        db.add(audit_log)

    await db.commit()
    return result

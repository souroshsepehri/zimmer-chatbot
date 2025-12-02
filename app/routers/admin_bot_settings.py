from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies import verify_admin

router = APIRouter()

# مسیر فایل تنظیمات در روت پروژه
SETTINGS_PATH = Path(__file__).resolve().parent.parent.parent / "bot_settings.json"


class BotSettings(BaseModel):
    bot_name: str
    welcome_message: str
    fallback_message: str
    language: str


@router.post(
    "/api/admin/bot-settings",
    dependencies=[Depends(verify_admin)],
    status_code=status.HTTP_200_OK,
)
async def save_bot_settings(settings: BotSettings) -> Dict[str, Any]:
    """
    ذخیره تنظیمات ربات در فایل bot_settings.json کنار backend.
    اگر مشکلی در نوشتن فایل پیش بیاید، 500 برمی‌گردانیم.
    """
    try:
        # ذخیره به صورت JSON با یونیکد درست
        SETTINGS_PATH.write_text(
            settings.model_dump_json(ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save bot settings.",
        ) from exc

    return {"status": "ok", "settings": settings.model_dump()}

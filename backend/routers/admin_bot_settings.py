from fastapi import APIRouter, Request, Depends

from models.bot_settings import BotSettings

from services.bot_settings_service import load_bot_settings, save_bot_settings
from core.admin_auth import require_admin


router = APIRouter(
    prefix="/api/admin",
    tags=["admin-bot-settings"],
)


@router.get("/bot-settings", response_model=BotSettings)
def get_bot_settings(request: Request, _: None = Depends(require_admin)):
    return load_bot_settings()


@router.put("/bot-settings", response_model=BotSettings)
def update_bot_settings(settings: BotSettings, request: Request, _: None = Depends(require_admin)):
    save_bot_settings(settings)
    return settings


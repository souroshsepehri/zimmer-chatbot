from fastapi import APIRouter

from models.bot_settings import BotSettings

from services.bot_settings_service import load_bot_settings, save_bot_settings


router = APIRouter(
    prefix="/api/admin",
    tags=["admin-bot-settings"],
)


@router.get("/bot-settings", response_model=BotSettings)
def get_bot_settings():
    return load_bot_settings()


@router.put("/bot-settings", response_model=BotSettings)
def update_bot_settings(settings: BotSettings):
    save_bot_settings(settings)
    return settings


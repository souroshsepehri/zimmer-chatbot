"""
Admin Bot Settings API

Endpoints for managing bot settings via admin panel.
"""

from fastapi import APIRouter, HTTPException
from models.bot_settings import BotSettings
from services.bot_settings_service import load_bot_settings, save_bot_settings

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-bot-settings"],
)


@router.get("/bot-settings", response_model=BotSettings)
def get_bot_settings():
    """
    Get current bot settings.
    
    Returns:
        BotSettings instance with current configuration
    """
    return load_bot_settings()


@router.put("/bot-settings", response_model=BotSettings)
def update_bot_settings(settings: BotSettings):
    """
    Update bot settings.
    
    Args:
        settings: New BotSettings to save
        
    Returns:
        Saved BotSettings instance
    """
    save_bot_settings(settings)
    return settings


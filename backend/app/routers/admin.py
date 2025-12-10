import json
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.dependencies import verify_admin_token

router = APIRouter()

BOT_SETTINGS_FILE = Path("bot_settings.json")


class BotSettings(BaseModel):
    bot_name: str = Field(..., min_length=1)
    welcome_message: str = Field(..., min_length=1)
    fallback_message: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


def get_default_settings():
    return {
        "bot_name": "Zimmer AI",
        "welcome_message": "Welcome to Zimmer AI. How can I help you today?",
        "fallback_message": "I apologize, but I could not understand your request. Please try rephrasing your question.",
        "language": "fa"
    }


def load_bot_settings():
    if not BOT_SETTINGS_FILE.exists():
        default_settings = get_default_settings()
        save_bot_settings(default_settings)
        return default_settings
    
    try:
        with open(BOT_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        default_settings = get_default_settings()
        save_bot_settings(default_settings)
        return default_settings


def save_bot_settings(settings: dict):
    with open(BOT_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


@router.get("/bot-settings")
async def get_bot_settings(admin_verified: bool = Depends(verify_admin_token)):
    settings = load_bot_settings()
    return settings


@router.post("/bot-settings")
async def update_bot_settings(
    settings: BotSettings,
    admin_verified: bool = Depends(verify_admin_token)
):
    settings_dict = {
        "bot_name": settings.bot_name,
        "welcome_message": settings.welcome_message,
        "fallback_message": settings.fallback_message,
        "language": settings.language
    }
    save_bot_settings(settings_dict)
    return {"message": "Bot settings updated successfully", "settings": settings_dict}


























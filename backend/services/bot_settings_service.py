"""
Bot Settings Service

Handles loading and saving bot settings from/to a JSON file.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from models.bot_settings import BotSettings

logger = logging.getLogger(__name__)

SETTINGS_FILE = Path(__file__).resolve().parent.parent / "data" / "bot_settings.json"


def load_bot_settings() -> BotSettings:
    """
    Load bot settings from JSON file.
    
    If file doesn't exist or loading fails, returns default settings
    and saves them to disk.
    
    Returns:
        BotSettings instance
    """
    try:
        if SETTINGS_FILE.exists():
            raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return BotSettings(**raw)
    except Exception as e:
        logger.warning("Failed to load bot settings: %s", e)

    # Return default settings and save them
    settings = BotSettings()
    save_bot_settings(settings)
    return settings


def save_bot_settings(settings: BotSettings) -> None:
    """
    Save bot settings to JSON file.
    
    Creates the data directory if it doesn't exist.
    
    Args:
        settings: BotSettings instance to save
    """
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        settings.model_dump_json(ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    logger.info("Bot settings saved to %s", SETTINGS_FILE)


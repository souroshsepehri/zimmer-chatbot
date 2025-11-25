import json
import logging
from pathlib import Path

from models.bot_settings import BotSettings

logger = logging.getLogger(__name__)

SETTINGS_FILE = Path(__file__).resolve().parent.parent / "data" / "bot_settings.json"


def load_bot_settings() -> BotSettings:
    try:
        if SETTINGS_FILE.exists():
            raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return BotSettings(**raw)
    except Exception as e:
        logger.warning("Failed to load bot settings: %s", e)

    # fallback to defaults
    settings = BotSettings()
    save_bot_settings(settings)
    return settings


def save_bot_settings(settings: BotSettings) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        settings.model_dump_json(indent=2),
        encoding="utf-8",
    )
    logger.info("Bot settings saved to %s", SETTINGS_FILE)


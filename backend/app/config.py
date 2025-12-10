from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ADMIN_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


_settings_instance = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


























from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str = ""
    global_owner_id: int = 0
    database_url: str = "sqlite+aiosqlite:///./master_x.db"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

from app.config import Settings

def test_settings_defaults():
    cfg = Settings(_env_file=None)
    assert cfg.database_url.startswith("sqlite+aiosqlite://")
    assert cfg.global_owner_id == 0

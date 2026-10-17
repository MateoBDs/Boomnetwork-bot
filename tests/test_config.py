from pathlib import Path

import pytest

from boombot.config import PROJECT_ROOT, ConfigError, Settings, load_settings

FAKE_TOKEN = "TOKEN_FALSO_" + "x" * 50


def test_missing_token_raises_without_leaking():
    with pytest.raises(ConfigError) as exc:
        load_settings({})
    assert "DISCORD_TOKEN" in str(exc.value)


@pytest.mark.parametrize("bad", ["   ", "con espacios dentro", '"entre comillas"', "'comillas'"])
def test_invalid_token_formats(bad):
    with pytest.raises(ConfigError):
        load_settings({"DISCORD_TOKEN": bad})


def test_defaults():
    s = load_settings({"DISCORD_TOKEN": FAKE_TOKEN})
    assert s.guild_id is None
    assert s.sync_commands is True
    assert s.log_level == "INFO"
    assert s.log_dir == PROJECT_ROOT / "logs"


def test_values_are_parsed():
    s = load_settings(
        {
            "DISCORD_TOKEN": FAKE_TOKEN,
            "DISCORD_GUILD_ID": "123456789012345678",
            "SYNC_COMMANDS": "false",
            "LOG_LEVEL": "debug",
            "LOG_DIR": "/tmp/boom-logs",
        }
    )
    assert s.guild_id == 123456789012345678
    assert s.sync_commands is False
    assert s.log_level == "DEBUG"
    assert s.log_dir == Path("/tmp/boom-logs")


@pytest.mark.parametrize(
    "key,value",
    [("DISCORD_GUILD_ID", "abc"), ("DISCORD_GUILD_ID", "-5"), ("SYNC_COMMANDS", "quizas"), ("LOG_LEVEL", "LOUD")],
)
def test_invalid_values(key, value):
    with pytest.raises(ConfigError):
        load_settings({"DISCORD_TOKEN": FAKE_TOKEN, key: value})


def test_token_never_in_repr_or_str():
    s = Settings(token=FAKE_TOKEN)
    assert FAKE_TOKEN not in repr(s)
    assert FAKE_TOKEN not in str(s)

import logging

from boombot.logging_setup import RedactingFormatter, configure_logging

SECRET = "SECRETO_SUPER_PRIVADO_123"


def test_formatter_redacts_secret():
    fmt = RedactingFormatter("%(message)s", secrets=[SECRET])
    record = logging.LogRecord("t", logging.INFO, __file__, 1, f"token={SECRET}", None, None)
    out = fmt.format(record)
    assert SECRET not in out
    assert "[REDACTED]" in out


def test_configure_logging_writes_file_without_secret(tmp_path):
    configure_logging("INFO", tmp_path, secrets=[SECRET])
    logging.getLogger("boombot.test").info("hola %s", SECRET)
    for handler in logging.getLogger().handlers:
        handler.flush()
    content = (tmp_path / "bot.log").read_text(encoding="utf-8")
    assert "hola [REDACTED]" in content
    assert SECRET not in content


def test_configure_logging_is_idempotent(tmp_path):
    configure_logging("INFO", tmp_path)
    configure_logging("INFO", tmp_path)
    ours = [h for h in logging.getLogger().handlers if getattr(h, "_boombot_handler", False)]
    assert len(ours) == 2  # consola + archivo, sin duplicados


def test_voice_notices_are_filtered(tmp_path):
    configure_logging("INFO", tmp_path)
    logger = logging.getLogger("discord.client")
    logger.warning("PyNaCl is not installed, voice will NOT be supported")
    logger.warning("otro aviso importante")
    for handler in logging.getLogger().handlers:
        handler.flush()
    content = (tmp_path / "bot.log").read_text(encoding="utf-8")
    assert "voice will NOT be supported" not in content
    assert "otro aviso importante" in content

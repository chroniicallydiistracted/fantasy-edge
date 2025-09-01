import logging
from app.logging import configure_logging


def test_logging_masks_secrets(caplog):
    configure_logging()
    logging.getLogger().addHandler(caplog.handler)
    logger = logging.getLogger("test")
    with caplog.at_level(logging.INFO):
        logger.info("access_token=abcd email=user@example.com secret=123")
    record = caplog.records[0]
    assert "access_token=***" in record.message
    assert "secret=***" in record.message
    assert "<redacted>@example.com" in record.message

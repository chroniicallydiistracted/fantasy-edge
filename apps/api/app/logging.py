import logging
import re

SECRET_FIELDS = ["token", "secret", "password"]
EMAIL_RE = re.compile(r"([\w.\-+]+)@([\w.\-]+)")

class MaskingFilter(logging.Filter):
    """Filter that masks secrets and emails in log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for field in SECRET_FIELDS:
            message = re.sub(rf"({field}=)[^\s&]+", r"\1***", message, flags=re.IGNORECASE)
        message = EMAIL_RE.sub(r"<redacted>@\2", message)
        record.msg = message
        record.args = ()
        return True

def configure_logging() -> None:
    """Configure root logger with masking filter."""
    handler = logging.StreamHandler()
    handler.addFilter(MaskingFilter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any


logger = logging.getLogger("aegis.audit")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_request_id() -> str:
    return f"req-{uuid.uuid4().hex[:12]}"


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _sanitize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_sanitize(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def log_event(
    event_type: str,
    payload: dict[str, Any] | None = None,
    *,
    status: str = "success",
    message: str | None = None,
) -> None:
    event = {
        "timestamp": _utc_now(),
        "event_type": event_type,
        "status": status,
        "message": message or event_type,
        "details": _sanitize(payload or {}),
    }
    logger.info(json.dumps(event, ensure_ascii=False))


def log_error(
    event_type: str,
    error: Exception,
    payload: dict[str, Any] | None = None,
    *,
    message: str | None = None,
) -> None:
    details = dict(payload or {})
    details["error_type"] = type(error).__name__
    details["error_message"] = str(error)

    event = {
        "timestamp": _utc_now(),
        "event_type": event_type,
        "status": "error",
        "message": message or str(error),
        "details": _sanitize(details),
    }
    logger.error(json.dumps(event, ensure_ascii=False))

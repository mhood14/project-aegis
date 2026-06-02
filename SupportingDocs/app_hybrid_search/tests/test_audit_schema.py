import json

from aegis_app.services import audit


def test_log_event_emits_sentinel_friendly_json(monkeypatch):
    records = []
    monkeypatch.setattr(audit.logger, "info", lambda message: records.append(message))

    audit.log_event(
        "authorization_denied",
        {"request_id": "req-123", "user_id": "user@example.com", "requested_scope": "top-level"},
        status="denied",
        message="Authorization denied",
    )

    assert len(records) == 1
    event = json.loads(records[0])
    assert event["event_type"] == "authorization_denied"
    assert event["status"] == "denied"
    assert event["message"] == "Authorization denied"
    assert event["details"]["request_id"] == "req-123"
    assert event["details"]["requested_scope"] == "top-level"
    assert "timestamp" in event


def test_log_error_includes_error_metadata(monkeypatch):
    records = []
    monkeypatch.setattr(audit.logger, "error", lambda message: records.append(message))

    audit.log_error("application_error", ValueError("bad input"), {"request_id": "req-456"})

    event = json.loads(records[0])
    assert event["event_type"] == "application_error"
    assert event["status"] == "error"
    assert event["details"]["request_id"] == "req-456"
    assert event["details"]["error_type"] == "ValueError"
    assert event["details"]["error_message"] == "bad input"

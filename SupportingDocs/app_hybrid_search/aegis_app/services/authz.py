from __future__ import annotations

from flask import current_app

from .audit import log_event


TOP_LEVEL_SCOPES = {"security-docs", "top-level"}
BASE_SCOPES = {"public-docs", "internal-docs", "security-tests"}


def _normalize_scope(scope: str | None) -> str:
    return (scope or "").strip().lower()


def _normalize_user(user_id: str | None) -> str:
    return (user_id or "").strip().lower()


def _is_security_admin(user_context: dict) -> bool:
    user_id = _normalize_user(user_context.get("user_id"))
    roles = {str(r).strip().lower() for r in user_context.get("roles", []) if r}

    if "security-admin" in roles:
        return True

    if user_id and user_id in current_app.config["SECURITY_ADMIN_USERS"]:
        return True

    return False


def get_allowed_scopes(user_context: dict) -> set[str]:
    if not user_context.get("is_authenticated"):
        return set()

    allowed = set(BASE_SCOPES)

    user_id = _normalize_user(user_context.get("user_id"))
    if current_app.config["INTERNAL_USERS"] and user_id not in current_app.config["INTERNAL_USERS"] and not _is_security_admin(user_context):
        allowed = {"public-docs"}

    if _is_security_admin(user_context):
        allowed.update(TOP_LEVEL_SCOPES)

    return allowed


def authorize_scope_or_raise(user_context: dict, scope: str, request_id: str | None = None) -> bool:
    normalized_scope = _normalize_scope(scope)
    user_id = user_context.get("user_id", "unknown-user")

    if current_app.config["AUTH_REQUIRE_SIGN_IN"] and not user_context.get("is_authenticated"):
        log_event(
            "authorization_denied",
            {
                "request_id": request_id,
                "user_id": user_id,
                "requested_scope": normalized_scope,
                "reason": "authentication_required",
            },
            status="denied",
            message="Authorization denied",
        )
        raise PermissionError("Authentication is required.")

    allowed_scopes = get_allowed_scopes(user_context)

    if normalized_scope in allowed_scopes:
        log_event(
            "authorization_allowed",
            {
                "request_id": request_id,
                "user_id": user_id,
                "requested_scope": normalized_scope,
                "allowed_scopes": sorted(allowed_scopes),
                "reason": "security_admin_top_level_access" if normalized_scope in TOP_LEVEL_SCOPES else "scope_allowed",
            },
            message="Authorization allowed",
        )
        return True

    log_event(
        "authorization_denied",
        {
            "request_id": request_id,
            "user_id": user_id,
            "requested_scope": normalized_scope,
            "allowed_scopes": sorted(allowed_scopes),
            "reason": "top_level_scope_requires_security_admin" if normalized_scope in TOP_LEVEL_SCOPES else "scope_not_permitted",
        },
        status="denied",
        message="Authorization denied",
    )
    raise PermissionError(f"User is not authorized for scope '{normalized_scope}'")
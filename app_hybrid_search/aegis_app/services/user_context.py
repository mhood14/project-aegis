from __future__ import annotations

import base64
import json
from typing import Any

from flask import current_app, request


def _decode_client_principal(encoded_value: str | None) -> dict[str, Any]:
    if not encoded_value:
        return {}

    try:
        decoded = base64.b64decode(encoded_value)
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


def _claims_to_dict(claims: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for claim in claims or []:
        typ = claim.get("typ")
        val = claim.get("val")
        if not typ or val is None:
            continue
        result.setdefault(typ, []).append(val)
    return result


def get_authenticated_user(req=request) -> dict[str, Any]:
    principal_name = req.headers.get(current_app.config["CLIENT_PRINCIPAL_NAME_HEADER"], "").strip()
    principal_id = req.headers.get(current_app.config["CLIENT_PRINCIPAL_ID_HEADER"], "").strip()
    idp = req.headers.get(current_app.config["CLIENT_PRINCIPAL_IDP_HEADER"], "").strip()

    principal_blob = req.headers.get(current_app.config["CLIENT_PRINCIPAL_HEADER"])
    principal = _decode_client_principal(principal_blob)

    claims = principal.get("claims", [])
    claims_by_type = _claims_to_dict(claims)

    # Common role/group claim candidates
    role_values = []
    for key in ("roles", "http://schemas.microsoft.com/ws/2008/06/identity/claims/role"):
        role_values.extend(claims_by_type.get(key, []))

    group_values = claims_by_type.get("groups", [])

    is_authenticated = bool(principal_name or principal_id or principal_blob)

    return {
        "is_authenticated": is_authenticated,
        "user_id": principal_name or principal_id or "anonymous",
        "principal_id": principal_id,
        "principal_name": principal_name,
        "identity_provider": idp,
        "roles": sorted(set(role_values)),
        "groups": sorted(set(group_values)),
        "claims": claims_by_type,
    }


def build_user_context(req=request) -> dict[str, Any]:
    user = get_authenticated_user(req)
    return {
        "is_authenticated": user["is_authenticated"],
        "user_id": user["user_id"],
        "principal_id": user["principal_id"],
        "principal_name": user["principal_name"],
        "identity_provider": user["identity_provider"],
        "roles": user["roles"],
        "groups": user["groups"],
        "claims": user["claims"],
    }

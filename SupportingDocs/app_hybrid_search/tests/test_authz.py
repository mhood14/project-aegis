import pytest

from aegis_app import create_app
from aegis_app.services.authz import authorize_scope_or_raise, get_allowed_scopes


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        AUTH_REQUIRE_SIGN_IN=True,
        INTERNAL_USERS={"analyst@example.com"},
        SECURITY_ADMIN_USERS={"admin@example.com"},
    )
    return app


def test_anonymous_user_has_no_allowed_scopes(app):
    with app.app_context():
        assert get_allowed_scopes({"is_authenticated": False}) == set()


@pytest.mark.parametrize("scope", ["public-docs", "internal-docs", "security-tests"])
def test_internal_user_allowed_base_scopes(app, scope):
    user = {"is_authenticated": True, "user_id": "analyst@example.com", "roles": []}

    with app.app_context():
        assert scope in get_allowed_scopes(user)
        assert authorize_scope_or_raise(user, scope, request_id="req-test") is True


def test_non_internal_user_restricted_to_public_docs(app):
    user = {"is_authenticated": True, "user_id": "external@example.com", "roles": []}

    with app.app_context():
        assert get_allowed_scopes(user) == {"public-docs"}
        assert authorize_scope_or_raise(user, "public-docs", request_id="req-test") is True
        with pytest.raises(PermissionError):
            authorize_scope_or_raise(user, "internal-docs", request_id="req-test")


@pytest.mark.parametrize("user", [
    {"is_authenticated": True, "user_id": "admin@example.com", "roles": []},
    {"is_authenticated": True, "user_id": "anyone@example.com", "roles": ["security-admin"]},
])
def test_security_admin_allowed_top_level_scopes(app, user):
    with app.app_context():
        allowed = get_allowed_scopes(user)
        assert {"security-docs", "top-level"}.issubset(allowed)
        assert authorize_scope_or_raise(user, "top-level", request_id="req-test") is True


def test_unauthenticated_user_denied_when_sign_in_required(app):
    user = {"is_authenticated": False, "user_id": None, "roles": []}

    with app.app_context(), pytest.raises(PermissionError):
        authorize_scope_or_raise(user, "public-docs", request_id="req-test")

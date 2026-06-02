from aegis_app.services.retrieval import _build_filter


def test_scope_filter_escapes_single_quotes():
    assert _build_filter("team's-docs") == "scope eq 'team''s-docs' and is_test_document eq false"


def test_security_test_scope_includes_test_documents():
    assert _build_filter("security-tests") == "scope eq 'security-tests'"


def test_normal_scopes_exclude_prompt_injection_test_documents():
    assert _build_filter("internal-docs") == "scope eq 'internal-docs' and is_test_document eq false"

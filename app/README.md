# Application source

The Project Aegis Flask application currently lives at:

```text
SupportingDocs/app_hybrid_search/
```

That directory contains the deployable app package, Azure service integrations, authorization logic, retrieval pipeline, prompt-injection sanitizer, structured audit logger, and tests.

This pointer exists so reviewers can discover the engineering artifact from the repository root while the existing GitHub Pages and supporting-evidence layout remains intact.

Recommended review path:

1. `SupportingDocs/app_hybrid_search/aegis_app/services/authz.py` - server-side scope authorization.
2. `SupportingDocs/app_hybrid_search/aegis_app/services/retrieval.py` - Azure AI Search scope filters.
3. `SupportingDocs/app_hybrid_search/aegis_app/services/llm.py` - grounded answer prompt and sanitizer.
4. `SupportingDocs/app_hybrid_search/aegis_app/services/audit.py` - structured JSON security telemetry.
5. `SupportingDocs/app_hybrid_search/tests/` - regression tests for core security behavior.

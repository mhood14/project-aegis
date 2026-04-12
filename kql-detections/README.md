# Project Aegis KQL Detections

This folder contains KQL detections, hunting queries, and detection engineering notes built around Project Aegis, a secure Azure-based AI document retrieval application.

The detections are aligned to the **actual Project Aegis audit schema** emitted by the app in `SupportingDocs/app_hybrid_search/aegis_app/services/audit.py`, `authz.py`, `llm.py`, `upload.py`, and `ingest.py`.

## Project context

Project Aegis combines:
- Entra ID-backed sign-in and scoped authorization
- Azure App Service-hosted application telemetry
- Azure OpenAI for grounded responses
- Azure AI Search for retrieval
- Microsoft Sentinel / Log Analytics for monitoring and investigation

## Detection goals

These detections focus on:
- repeated authorization denials
- suspicious scope probing and cross-scope behavior
- AI safety and content-filter events
- unusual upload or ingestion activity
- identity-related authentication failures

## Important logging note

The application emits JSON log records to stdout in this shape:

```json
{
  "timestamp": "2026-04-12T14:00:00Z",
  "event_type": "authorization_denied",
  "status": "denied",
  "message": "Authorization denied",
  "details": {
    "request_id": "req-123456789abc",
    "user_id": "user@contoso.com",
    "requested_scope": "security-docs",
    "allowed_scopes": ["public-docs"],
    "reason": "top_level_scope_requires_security_admin"
  }
}
```

In Azure Monitor / Log Analytics, these records are expected to land in **`AppServiceConsoleLogs`** with the JSON payload in **`ResultDescription`**.

## Repo layout

- `detections/app/` - app-specific analytic rules for Aegis events
- `detections/data/` - data upload / ingestion monitoring
- `detections/identity/` - Entra ID identity detections
- `hunting/` - proactive hunts and exploratory queries
- `workbooks/` - workbook notes and future visuals
- `images/` - documentation placeholder for detection screenshots

## Recommended deployment targets

These queries can be adapted into:
- Microsoft Sentinel scheduled analytics rules
- Sentinel hunting queries
- Defender custom detections where applicable
- workbook visualizations and investigation pivots

## Existing evidence already in this repo

Existing screenshots that support the detection story already live under:
- `SupportingDocs/AppPictures/AuthorizationDeniedAlert.png`
- `SupportingDocs/AppPictures/ContentFilterAlert.png`
- `SupportingDocs/AppPictures/log-content-filter-query.png`
- `SupportingDocs/AppPictures/log-request-id-trace-query.png`
- `SupportingDocs/AppPictures/log-request-trace-query.png`
- `SupportingDocs/AppPictures/log-security-docs-scope-query.png`

## Detection set in v1

1. Authorization Denied
2. Content Filter Triggered
3. Suspicious Scope Usage
4. Unusual Upload Activity
5. Repeated Authentication Failures

## Source references

Detection logic was tuned to these files:
- `SupportingDocs/app_hybrid_search/aegis_app/services/audit.py`
- `SupportingDocs/app_hybrid_search/aegis_app/services/authz.py`
- `SupportingDocs/app_hybrid_search/aegis_app/services/llm.py`
- `SupportingDocs/app_hybrid_search/aegis_app/routes/upload.py`
- `SupportingDocs/app_hybrid_search/aegis_app/services/ingest.py`

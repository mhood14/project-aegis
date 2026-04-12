# Unusual Upload Activity

## Purpose
Detect spikes in Aegis upload activity that may indicate bulk ingestion abuse, poisoning attempts, repeated malformed requests, or aggressive testing.

## Data Source
- Azure App Service Console Logs
- Log Analytics / Microsoft Sentinel
- Table: `AppServiceConsoleLogs`

## Actual Aegis fields used
- `event_type`
- `details.request_id`
- `details.user_id`
- `details.uploaded_by`
- `details.scope`
- `details.filename`
- `details.byte_count`
- `details.reason`

## MITRE ATT&CK
- T1565 - Data Manipulation
- T1190 - Exploit Public-Facing Application
- T1499 - Endpoint Denial of Service

## Detection Logic
This query looks for bursts of upload-related events, including:
- `document_upload_started`
- `upload_size_exceeded`
- `invalid_upload_request`

It flags users with high upload volume, many distinct files, multiple scopes, or unusually large byte totals.

## Why it matters
Aegis relies on document ingestion and retrieval quality. Upload abuse can degrade trust in the retrieval pipeline or be used to stage adversarial content.

## Tuning notes
- Adjust thresholds to match your expected testing volume.
- Separate successful uploads from denied uploads if you want different severities.
- Watch for activity crossing from normal scopes into `security-tests`.

## Investigation steps
1. Identify the actor and upload window.
2. Review filenames, scopes, and byte counts.
3. Determine whether the activity was expected bulk testing.
4. Check for related document-processing failures.
5. Review if uploaded content later triggered sanitizer or content-filter events.

## Response actions
- Temporarily block abusive upload activity.
- Review file validation and quota settings.
- Remove suspicious documents from indexed scopes if necessary.

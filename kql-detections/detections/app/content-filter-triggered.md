# Content Filter Triggered

## Purpose
Detect AI-safety relevant events in Project Aegis, including sanitized retrieved content, preflight blocks, and Azure OpenAI content-filter blocks.

## Data Source
- Azure App Service Console Logs
- Log Analytics / Microsoft Sentinel
- Table: `AppServiceConsoleLogs`

## Actual Aegis fields used
- `event_type`
- `status`
- `details.request_id`
- `details.chunk_count`
- `details.removed_line_groups`
- `details.reason`
- `details.document_ids`

## MITRE ATT&CK
- T1565 - Data Manipulation
- T1190 - Exploit Public-Facing Application
- T1580 - Cloud Infrastructure Discovery

## Detection Logic
The query groups together three related Aegis safety events:
- `retrieved_content_sanitized`
- `llm_request_blocked_preflight`
- `llm_request_blocked_content_filter`

This makes it easier to monitor prompt-injection indicators and unsafe retrieval patterns as one workflow.

## Why it matters
This is one of the strongest Aegis-specific detections because it demonstrates monitoring for AI misuse, unsafe retrieved content, and model safety enforcement rather than only standard infrastructure events.

## Tuning notes
- Convert to separate rules if you want dedicated severity by event type.
- Raise severity when repeated events involve the same `request_id` chain or the same document set.
- Pay special attention to events generated from `security-tests`, where adversarial content may be intentionally stored.

## Investigation steps
1. Identify the affected request IDs.
2. Review whether sanitization happened before a model call.
3. Check whether the request was preflight-blocked or model-blocked.
4. Review the related document IDs and scope.
5. Determine whether the activity was a deliberate test or suspicious user behavior.

## Response actions
- Remove or isolate malicious test content from production-accessible scopes.
- Review prompt-injection test coverage and sanitizer patterns.
- Increase monitoring around affected users or scopes.
- Document lessons learned for future AI safety tuning.

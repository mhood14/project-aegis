# Agentic security considerations

Project Aegis is positioned as a secure AI document retrieval system and a foundation for discussing agentic security. The key design principle is that model output is never treated as an authorization decision.

## Design principle

AI can help retrieve, summarize, explain, and recommend. It should not independently bypass access control, modify security state, approve access, close incidents, or execute privileged actions without deterministic authorization and human approval.

## Allowed behavior

- Answer questions using only authorized retrieved context.
- Cite source chunks or documents.
- Recommend analyst next steps.
- Explain why an access request was denied at a high level.
- Log the user, request ID, selected scope, retrieved references, and model outcome.

## Disallowed behavior

- Retrieve content outside the user’s authorized scope.
- Follow instructions inside retrieved documents that conflict with the system prompt or application policy.
- Modify Entra groups, role assignments, Conditional Access, storage permissions, Sentinel rules, or document classifications.
- Approve access requests or close security incidents based only on model output.
- Export sensitive data in bulk.

## Human approval boundaries

These actions require human approval and separate authorization checks before any future automation is added:

- Granting, changing, or removing access.
- Privileged remediation actions.
- Incident closure or severity downgrade.
- Document reclassification or quarantine release.
- Bulk export or external sharing.
- Changes to Sentinel analytics, KQL detections, or logging pipelines.

## Risks addressed

| Risk | Scenario | Control |
| --- | --- | --- |
| Prompt injection | A user or document instructs the model to ignore policy | Retrieved content is framed as untrusted data; suspicious content is sanitized/logged; access is enforced outside the model |
| Indirect prompt injection | A malicious uploaded document attempts to influence future answers | Prompt-injection test documents, content-filter telemetry, and suspicious document handling roadmap |
| Excessive agency | A future agent executes sensitive actions without oversight | Recommendation-only design, human approval gates, and separate authorization checks |
| Retrieval abuse | User probes unauthorized scopes | Server-side scope enforcement and Sentinel detections for repeated authorization failures |
| Weak auditability | Analysts cannot reconstruct what happened | Request IDs, user/scope logging, document references, model outcomes, and KQL pivots |

## Sentinel investigation signals

Useful event types and fields include:

- `authorization_denied`
- `retrieved_content_sanitized`
- `llm_request_blocked_content_filter`
- `question_answering_completed`
- `details.request_id`
- `details.user_id`
- `details.requested_scope`
- `details.document_id`
- `details.filename`
- `details.status`

These support investigations into unauthorized access attempts, prompt-injection testing, suspicious document uploads, and abnormal AI usage patterns.

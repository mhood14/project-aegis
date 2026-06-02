# Threat model summary

Project Aegis models risks across the Azure environment, identity boundary, application layer, retrieval pipeline, AI model interaction, and detection/response process.

## Primary assets

- Internal documents uploaded to Azure Blob Storage.
- Processed chunks indexed in Azure AI Search.
- User identity and authorization context from Microsoft Entra/App Service auth.
- Azure OpenAI prompts, retrieved excerpts, responses, and citations.
- Audit events shipped to Log Analytics / Sentinel.
- Azure service identities, RBAC assignments, and configuration.

## Trust boundaries

- Browser/user input to Flask application.
- Authenticated user identity to server-side authorization logic.
- Application to Azure AI Search.
- Application to Azure OpenAI.
- Application to Blob Storage.
- Application logs to Log Analytics / Sentinel.
- Retrieved document content to model prompt context.

The most important AI-specific boundary is that retrieved document text is not trusted simply because it came from an internal index.

## Key risks

| Risk | Why it matters | Current mitigation | Next step |
| --- | --- | --- | --- |
| Prompt injection in retrieved documents | Malicious text may try to override model instructions or exfiltrate data | Retrieved excerpts framed as untrusted; sanitizer removes obvious patterns; content-filter events are logged | Add quarantine/provenance workflow and stronger suspicious-document scoring |
| Authorization abuse / scope probing | Users may try to access elevated scopes | Server-side scope authorization and Sentinel detections | Add Entra group-to-scope mapping and more tests |
| Document poisoning | Uploaded content may pollute retrieval results | Scoped upload authorization and prompt-injection test corpus | Add malware scanning, MIME validation, review queues, and parser isolation |
| Overprivileged identities | Compromised service/user identity could access too much | Managed identity/RBAC design emphasis | Codify least privilege assignments in IaC |
| Monitoring blind spots | Security events may not become actionable alerts | Structured audit logs and KQL detection package | Automate Sentinel rule deployment and workbook dashboards |
| Error detail leakage | User-facing errors could expose internals | Known limitation documented | Return generic errors with request IDs and log full details server-side |
| CSRF on authenticated forms | Browser-authenticated POST routes can be abused cross-site | Known limitation documented | Add CSRF tokens or explicit CSRF mitigation |

## Existing detection coverage

The `kql-detections/` package covers:

- Repeated authorization denials.
- Content-filter / prompt-injection-triggered behavior.
- Suspicious scope usage and scope probing.
- Unusual upload activity.
- Repeated authentication failures.
- Hunting queries for anomalous user behavior.

## Production hardening priorities

1. Add CSRF protection for POST routes.
2. Map Entra group object IDs to app scopes.
3. Add upload quarantine, scanning, content-type validation, and rate limiting.
4. Add infrastructure-as-code for Azure resources and RBAC.
5. Deploy Sentinel analytic rules as code.
6. Expand regression tests around identity parsing, upload validation, and detection schema compatibility.
7. Add demo video evidence because the live app is intentionally protected by Microsoft sign-in.

## Interview framing

A strong way to explain the threat model:

> Project Aegis treats secure AI retrieval as both a cloud security problem and an application security problem. The Azure design reduces exposure and secret risk, while the app enforces scoped retrieval, treats retrieved content as untrusted, and emits telemetry that Sentinel can turn into investigation-ready alerts.

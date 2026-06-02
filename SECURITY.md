# Security Policy

Project Aegis is a portfolio and reference implementation for secure AI document retrieval on Microsoft Azure. It demonstrates practical security controls, logging, detection engineering, and threat modeling, but it should not be treated as production-ready without the hardening items below.

## Security assumptions

- The application is intended for authenticated internal users.
- Microsoft Entra ID / App Service authentication is the expected front door.
- Server-side authorization is the source of truth for document scope access.
- Retrieved documents and user prompts are untrusted inputs.
- Azure services should be accessed through managed identity or Azure identity flows, not embedded credentials.
- Logs should be shipped to Log Analytics / Sentinel for investigation and detection.

## Data classification and access model

The demo uses document scopes to represent data boundaries:

- `public-docs`: least sensitive scope.
- `internal-docs`: general internal content.
- `security-tests`: adversarial or test documents used for prompt-injection validation.
- `security-docs` and `top-level`: elevated scopes for security administrators.

The UI may let a user request a scope, but `aegis_app/services/authz.py` enforces the final server-side decision.

## AI-specific risks addressed

- Prompt injection through retrieved documents.
- Document poisoning.
- Unauthorized scope retrieval.
- Model content-filter triggers.
- Over-trusting retrieved context.
- Lack of citations or provenance.
- Insufficient audit trails for AI interactions.

Project Aegis treats prompt-injection filtering as defense-in-depth. Pattern-based sanitization is useful for demonstration and logging, but it does not fully solve prompt injection.

## Current controls

- Microsoft identity-backed application access.
- Server-side scope checks before upload and question answering.
- Scope filters applied during Azure AI Search retrieval.
- Retrieved excerpts framed as untrusted data in the system prompt.
- Structured JSON audit events with request IDs.
- KQL detections for authorization denials, content-filter events, suspicious scope usage, unusual uploads, and repeated authentication failures.
- Environment-driven configuration for Azure endpoints and app behavior.
- Local debug mode disabled by default.

## Known limitations

- CSRF protection is not yet implemented for browser POST forms.
- Entra group-to-scope mapping should be expanded beyond role/user allowlists.
- Upload validation should add MIME detection, malware scanning, quarantine, parser isolation, and per-user rate limits.
- Infrastructure-as-code is not yet included for the full Azure environment.
- Sentinel rule deployment is documented by KQL artifacts but not fully automated as code.
- The live app is protected by Microsoft sign-in, so external reviewers need screenshots or a demo video to validate behavior.

## Production hardening backlog

1. Add CSRF tokens or another explicit CSRF mitigation for authenticated browser flows.
2. Use Entra group object IDs mapped to allowed scopes.
3. Add upload scanning and quarantine workflow.
4. Add rate limits and per-user quotas.
5. Move Sentinel analytics rules and Azure resources into Bicep or Terraform.
6. Add secrets scanning and dependency scanning to CI.
7. Expand tests for upload validation, EasyAuth parsing, and KQL schema compatibility.
8. Add a data retention and privacy note for audit logs.

## Responsible disclosure

If you find a security issue in this repository or the hosted demo, please contact the repository owner privately instead of opening a public issue with exploit details.

# Project Aegis: Secure AI Document Retrieval on Microsoft Azure

Project Aegis is a security engineering portfolio project that demonstrates how to design, build, monitor, and threat model a secure AI document retrieval system on Microsoft Azure.

The project combines Azure cloud security architecture, Microsoft Entra identity controls, scoped retrieval-augmented generation, structured application audit logging, Microsoft Sentinel detection engineering, and agentic security design. It is built to support an interview narrative around Microsoft security, cloud security, Zero Trust, secure AI, agentic security, and detection/response.

## Problem statement

Internal teams want to ask questions over internal documents with AI, but the system must avoid the common failure modes of insecure RAG systems:

- Users should only retrieve documents from scopes they are authorized to access.
- Retrieved document text must be treated as untrusted content, not as instructions.
- Prompt injection and unsafe retrieved content should be visible in logs and detections.
- Authentication, authorization, and application activity should be traceable for investigations.
- The cloud design should use Microsoft security primitives instead of embedded secrets or flat networking.

## What this project demonstrates

- Microsoft Entra-backed app access and identity-aware authorization.
- Scope-based document access controls enforced server-side.
- Azure OpenAI and Azure AI Search for grounded answers with citations.
- Azure Blob Storage separation of raw and processed documents.
- Managed identity-oriented Azure service access.
- Hub-and-spoke Azure networking with private endpoint-oriented design.
- Structured JSON audit events designed for Log Analytics and Sentinel.
- Custom KQL detections for authorization abuse, prompt/content-filter events, scope probing, unusual uploads, and repeated authentication failures.
- Threat modeling for AI-specific and cloud-specific risks including prompt injection, indirect prompt injection, data poisoning, authorization abuse, excessive agency, egress, DNS/routing, and monitoring gaps.
- Agentic security documentation covering recommendation-versus-execution boundaries, human approval gates, and AI action auditability.

## Live portfolio site

GitHub Pages site:

https://mhood14.github.io/project-aegis/

Live app note: the Azure Web App is intentionally protected by Microsoft sign-in. Recruiters and interviewers may not be able to access it directly, so this repository includes screenshots, architecture artifacts, KQL detections, and implementation notes as validation evidence.

## Repository map

```text
.
├── index.html, case-study.html, ai-security.html, architecture.html, logging.html, artifacts.html, about.html
│   └── GitHub Pages portfolio site
├── SupportingDocs/
│   ├── app_hybrid_search/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── aegis_app/
│   │   │   ├── routes/
│   │   │   └── services/
│   │   └── tests/
│   │       └── pytest coverage for authorization, sanitizer, audit schema, and retrieval filters
│   ├── AppPictures/
│   │   └── app and Sentinel evidence screenshots
│   ├── PromptInjection/
│   │   └── adversarial prompt-injection test documents
│   └── architecture, threat-model, egress, IP, and build evidence artifacts
├── kql-detections/
│   ├── detections/
│   ├── hunting/
│   └── workbooks/
├── docs/
│   ├── architecture-summary.md
│   ├── threat-model-summary.md
│   ├── secure-ai-case-study.md
│   ├── agentic-security.md
│   └── ai-security-test-plan.md
├── app/
│   └── README.md pointer to the application source package
├── SECURITY.md
└── .github/workflows/ci.yml
```

The source app currently remains in `SupportingDocs/app_hybrid_search/` to preserve the existing portfolio artifact layout. The top-level `app/README.md` mirrors the app location so the engineering artifact is discoverable from the repository root.

## Application flow

1. User authenticates through Microsoft identity / App Service auth.
2. App derives the user identity and claims from EasyAuth headers.
3. User selects a document scope and submits a question or upload.
4. Server-side authorization validates the requested scope.
5. Retrieval queries Azure AI Search using a scope filter.
6. Retrieved excerpts are sanitized for obvious prompt-injection lines and treated as untrusted data in the system prompt.
7. Azure OpenAI returns a grounded answer using only retrieved excerpts.
8. The response includes citations to retrieved chunks.
9. Audit events are emitted as structured JSON for Log Analytics/Sentinel.
10. KQL detections convert suspicious behavior into triage-ready security signals.

## Security controls and design choices

- Server-side scope enforcement is the source of truth; UI scope selection does not grant access.
- `DefaultAzureCredential` and Azure identity patterns avoid hard-coded service secrets.
- Raw and processed document storage are separated.
- Retrieved AI content is explicitly treated as untrusted.
- Prompt-injection filtering is implemented as defense-in-depth, not as a complete solution.
- Request IDs support investigation across app logs, retrieval, model calls, and detections.
- Sentinel detections are aligned to actual application audit event fields.

## Detection engineering package

The `kql-detections/` directory contains application, data, identity, and hunting queries. Examples include:

- Authorization denied activity.
- Content-filter / prompt-injection-triggered events.
- Suspicious scope usage and scope probing.
- Unusual upload activity.
- Repeated authentication failures.
- Anomalous user activity hunts.

These detections are intentionally tied to emitted audit events such as `authorization_denied`, `retrieved_content_sanitized`, `llm_request_blocked_content_filter`, and `question_answering_completed`.

## Recruiter and interviewer framing

Project Aegis is optimized to support resume bullets and interview discussion around secure AI in Microsoft cloud environments. The quickest review path is:

1. `case-study.html` / `docs/secure-ai-case-study.md` - one-page secure AI case study.
2. `ai-security.html` / `docs/agentic-security.md` - agentic security boundaries and controls.
3. `docs/ai-security-test-plan.md` - AI security scenarios, expected behavior, and detection signals.
4. `logging.html` and `kql-detections/` - Sentinel/KQL evidence and investigation workflow.

Resume-aligned themes demonstrated by the project:

- Secure RAG architecture using Microsoft Entra-backed access, Azure OpenAI, Azure AI Search, Blob Storage, scoped retrieval, and managed identity-oriented service access.
- Agentic security controls including recommendation-versus-execution boundaries, human-in-the-loop approval, least-privilege AI behavior, and AI action auditability.
- AI security testing for prompt injection, indirect prompt injection, unauthorized retrieval, sensitive-data requests, document poisoning, and citation/grounding validation.
- Security operations visibility through structured audit logs, Microsoft Sentinel detections, KQL hunting queries, and request-level investigation workflows.

## Run the Flask app locally

```bash
cd SupportingDocs/app_hybrid_search
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Required for real Azure-backed operation:
export AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="<chat-deployment>"
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="<embedding-deployment>"
export STORAGE_ACCOUNT_URL="https://<account>.blob.core.windows.net"
export AZURE_SEARCH_ENDPOINT="https://<search-service>.search.windows.net"

python app.py
```

`FLASK_DEBUG` defaults to false and `FLASK_RUN_HOST` defaults to `127.0.0.1`. Set `FLASK_DEBUG=true` only for local development. Set `FLASK_RUN_HOST=0.0.0.0` only when you intentionally need the local server reachable from another host.

## Run tests and quality checks

```bash
cd SupportingDocs/app_hybrid_search
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
ruff check .
bandit -q -r aegis_app app.py
pip-audit -r requirements.txt
```

GitHub Actions runs the same core checks on pull requests and pushes.

## Known limitations and production next steps

- Add CSRF protection for browser POST forms before presenting the app as production-ready.
- Use Entra group IDs mapped to scopes instead of relying primarily on user allowlists.
- Add malware scanning, MIME validation, quarantine/review workflow, and upload rate limits.
- Expand infrastructure-as-code coverage with Bicep or Terraform for repeatable deployment.
- Deploy Sentinel analytic rules as code.
- Treat pattern-based prompt-injection filtering as defense-in-depth and continue investing in provenance, quarantine, and suspicious-document workflows.
- Add a short demo video/GIF because the live app is intentionally protected by Microsoft sign-in.
- Expand agentic security testing for future tool-use workflows, approval gates, and AI action audit events.

## Interview talking points

- Cloud security architecture: hub/spoke, private endpoints, private DNS, managed identity, Key Vault, Sentinel, Defender, Conditional Access, and Zero Trust access design.
- Secure AI application design: scoped retrieval, grounded answers, citations, untrusted retrieved content, prompt-injection test cases, and explicit authorization boundaries.
- Agentic security design: recommendation-versus-execution separation, human approval gates, excessive-agency risk, and auditability of future AI actions.
- Detection and response: JSON audit telemetry, Log Analytics queries, Sentinel analytic rules, investigation workflows, and alert evidence.
- Risk communication: executive threat model, prioritized risk table, current controls, and production next steps.

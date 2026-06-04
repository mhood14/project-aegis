# Architecture summary

Project Aegis is designed as a secure Microsoft-cloud AI document retrieval system. The architecture story is intentionally bigger than the Flask app: it demonstrates how identity, networking, data, AI, and monitoring controls fit together in Azure.

## Core architecture goals

- Protect access with Microsoft Entra identity and Conditional Access.
- Avoid flat networking by using a hub-and-spoke design.
- Prefer private endpoints and private DNS for platform services.
- Use managed identities and Azure RBAC instead of embedded credentials.
- Separate raw document storage from processed retrieval chunks.
- Enforce document scopes before retrieval and before upload.
- Emit audit events that can be investigated in Microsoft Sentinel.

## Logical components

```text
User
  -> Microsoft sign-in / App Service auth
  -> Flask web app
  -> Scope authorization
  -> Azure AI Search retrieval
  -> Azure OpenAI grounded answer generation
  -> Structured audit logs
  -> Log Analytics / Microsoft Sentinel detections
```

## Microsoft security services represented

- Microsoft Entra ID for identity and app access.
- Conditional Access for MFA and legacy-auth blocking design.
- Azure App Service for the web application.
- Azure OpenAI for answer generation.
- Azure AI Search for indexed document retrieval.
- Azure Blob Storage for raw and processed document data.
- Azure Key Vault and managed identity patterns for secret reduction.
- Log Analytics and Microsoft Sentinel for detection and investigation.
- Microsoft Defender ecosystem references for security operations context.

## Network design narrative

The architecture evidence describes a hub-and-spoke pattern with centralized routing and private connectivity. In production, this model would support:

- Segmented application, AI, data, and shared-service boundaries.
- Private endpoint access to storage/search/AI services where supported.
- Private DNS zones for endpoint resolution.
- Centralized egress monitoring/control through the hub.
- Reduced public exposure of sensitive platform services.

## Application security flow

1. App receives identity context from App Service authentication headers.
2. User-selected scope is normalized server-side.
3. Authorization logic checks whether the user can access the requested scope.
4. Search filters include the authorized scope and exclude prompt-injection test documents from normal scopes.
5. Retrieved content is treated as untrusted data inside the LLM prompt.
6. Suspicious retrieved lines are removed and logged.
7. Grounded answers cite source chunks.
8. Request-level audit events are emitted for investigation.

## Why this matters for Microsoft security interviews

This project connects multiple security disciplines in one coherent build:

- Cloud security architecture.
- Identity and access management.
- Zero Trust access boundaries.
- Secure AI/RAG application design.
- Detection engineering with KQL.
- SOC investigation workflow.
- Threat modeling and risk prioritization.


## Agentic security extension

Project Aegis is currently a secure retrieval and recommendation workflow, not an autonomous execution platform. That boundary is intentional. Future agentic capabilities should preserve deterministic authorization, least-privilege tool access, explicit human approval for privileged actions, and audit events that show what the AI saw, recommended, and attempted to do.

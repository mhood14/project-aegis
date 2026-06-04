# Project Aegis case study: secure AI on Microsoft Azure

## Problem

Internal teams want to use AI over private documents, but insecure retrieval-augmented generation (RAG) can create new security failures:

- Unauthorized users may retrieve sensitive documents through weak scope enforcement.
- Prompt injection in user input or retrieved documents may try to override system instructions.
- A future AI agent may take actions beyond its intended authority.
- Security teams may lack enough logging to reconstruct what the AI saw, returned, or recommended.

## Solution

Project Aegis is a secure Azure-based AI document retrieval platform that demonstrates how identity, authorization, retrieval, logging, and detection can be built into an AI workflow from the beginning.

Core services and concepts:

- Microsoft Entra-backed access / App Service authentication.
- Azure OpenAI for grounded answer generation.
- Azure AI Search for indexed document retrieval.
- Azure Blob Storage for raw and processed document data.
- Managed identity-oriented service access and least-privilege design.
- Structured JSON audit logging for retrieval, authorization, and model events.
- Microsoft Sentinel and KQL detections for suspicious application and AI activity.

## Security controls demonstrated

- Server-side scope authorization before retrieval or upload.
- Scoped RAG using authorized document filters.
- Retrieved content treated as untrusted data, not model instructions.
- Prompt-injection/content-filter events logged for investigation.
- Request IDs to connect application behavior to Sentinel investigation workflows.
- KQL detections for authorization denials, suspicious scope usage, unusual uploads, repeated authentication failures, and content-filter events.
- Threat modeling for prompt injection, indirect prompt injection, document poisoning, retrieval abuse, excessive agency, and weak auditability.

## Agentic security framing

Project Aegis is currently a recommendation and retrieval system, not an autonomous execution system. That distinction is intentional.

Allowed AI behavior:

- Answer questions using authorized retrieved context.
- Cite source chunks.
- Recommend investigation next steps.
- Log user, request, scope, and retrieved references.

Not allowed without deterministic controls and human approval:

- Bypass authorization boundaries.
- Retrieve content outside the user’s allowed scope.
- Modify access policies.
- Execute privileged security or administrative actions.
- Export sensitive data in bulk.

## Resume-ready framing

Project Aegis supports concise bullets such as:

- Designed a secure RAG-based document retrieval platform on Microsoft Azure using Microsoft Entra-backed access, Azure OpenAI, Azure AI Search, Blob Storage, managed identity-oriented service access, and scoped authorization controls.
- Built structured audit logging, Sentinel detection scenarios, and KQL hunting queries for unauthorized retrieval, prompt-injection/content-filter events, suspicious scope usage, unusual uploads, and repeated authorization failures.
- Documented agentic security controls covering prompt injection, indirect prompt injection, excessive agency, human-in-the-loop approval, retrieval authorization, and AI action auditability.

## Production hardening roadmap

- Map Entra group object IDs directly to document scopes.
- Add private endpoints and private DNS for sensitive platform services where supported.
- Deploy infrastructure and Sentinel analytics rules as code.
- Add upload quarantine, malware scanning, content-type validation, and rate limiting.
- Add AI evaluation tests for prompt injection, grounding, citation accuracy, and sensitive-data requests.
- Add Security Copilot-style promptbooks or analyst workflows for investigating AI abuse scenarios.

# Authorization Denied

## Purpose
Detect repeated `authorization_denied` events in Project Aegis that may indicate scope probing, broken access attempts, or a user repeatedly trying to access restricted data.

## Data Source
- Azure App Service Console Logs
- Log Analytics / Microsoft Sentinel
- Table: `AppServiceConsoleLogs`

## Actual Aegis fields used
- `event_type`
- `status`
- `details.request_id`
- `details.user_id`
- `details.requested_scope`
- `details.allowed_scopes`
- `details.reason`

## MITRE ATT&CK
- T1078 - Valid Accounts
- T1087 - Account Discovery
- T1190 - Exploit Public-Facing Application

## Detection Logic
This query looks for multiple denied authorization events for the same user and requested scope within a one-hour window.

## Why it matters
Aegis is intentionally built around scoped access control. Repeated denied requests against restricted scopes such as `security-docs` or `top-level` are a strong indicator of probing or misuse.

## Tuning notes
- Increase the threshold if your testing generates many expected denials.
- Exclude developer or admin test identities when needed.
- Prioritize denials for `security-docs` and `top-level`.
- Correlate with sign-in activity and IP context where possible.

## Investigation steps
1. Identify the user and requested scope.
2. Review whether the scope is expected for that identity.
3. Check if the user targeted multiple scopes in the same period.
4. Pivot on `request_id` to reconstruct the request path.
5. Review Entra sign-in activity for suspicious IPs or failed sign-ins.

## Response actions
- Challenge or block the user session if activity is suspicious.
- Validate Entra role/group membership.
- Review whether authorization logic or documentation encouraged accidental misuse.
- Escalate if repeated probing crosses multiple restricted scopes.

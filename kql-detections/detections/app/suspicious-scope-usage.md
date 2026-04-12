# Suspicious Scope Usage

## Purpose
Detect users interacting with an unusual number of Aegis scopes in a short period, especially when that activity includes repeated denials.

## Data Source
- Azure App Service Console Logs
- Log Analytics / Microsoft Sentinel
- Table: `AppServiceConsoleLogs`

## Actual Aegis fields used
- `event_type`
- `details.user_id`
- `details.requested_scope`
- `details.reason`
- `details.request_id`

## MITRE ATT&CK
- T1078 - Valid Accounts
- T1087 - Account Discovery
- T1526 - Cloud Service Discovery

## Detection Logic
The query summarizes both allowed and denied authorization events per user per day and flags users that:
- touched three or more scopes in a day, or
- generated repeated denials while moving across scopes

## Why it matters
Scoped retrieval is central to Aegis. Cross-scope behavior is normal only for a small number of privileged users. For most users, broad scope usage is a useful anomaly signal.

## Tuning notes
- Adjust the threshold if security admins routinely use many scopes.
- Exclude known `security-admin` accounts if they create noise.
- Raise severity when the scope set includes `security-docs` or `top-level`.

## Investigation steps
1. Review the user’s normal role and allowed scopes.
2. Check whether the activity mixed allowed and denied scope requests.
3. Pivot to request traces for the affected period.
4. Review sign-in locations and devices.
5. Determine whether the behavior was testing, admin work, or probing.

## Response actions
- Investigate suspicious cross-scope access.
- Confirm role assignments and least-privilege boundaries.
- Restrict access or step up authentication if needed.

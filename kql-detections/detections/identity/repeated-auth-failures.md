# Repeated Authentication Failures

## Purpose
Detect repeated Entra ID sign-in failures that may indicate password spraying, user targeting, or failed attempts to reach the Aegis application.

## Data Source
- Microsoft Entra ID sign-in logs
- Log Analytics / Microsoft Sentinel
- Table: `SigninLogs`

## MITRE ATT&CK
- T1110 - Brute Force
- T1078 - Valid Accounts

## Detection Logic
This query identifies users with five or more failed sign-ins in one hour and preserves the IPs, apps, and result descriptions for triage.

## Why it matters
This rounds out the Aegis repo with a Microsoft-native identity detection that pairs well with the application-specific detections.

## Tuning notes
- Raise or lower the threshold based on tenant noise.
- Filter to Aegis-related app names if you want a tighter identity scope.
- Correlate with `authorization_denied` activity for stronger confidence.

## Investigation steps
1. Review the failed sign-in reasons.
2. Identify suspicious IP reuse across accounts.
3. Confirm whether the target app was Project Aegis.
4. Check for successful sign-ins before or after the failure burst.

## Response actions
- Trigger MFA or conditional access review.
- Block suspicious IPs where appropriate.
- Investigate possible password spray activity.

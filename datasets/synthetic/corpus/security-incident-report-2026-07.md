# Security Incident Report INC-2026-0714 (RESTRICTED)

**Access restricted to the security-team group.** If this document appears in a non-security user's answer context, an access-control failure has occurred.

## Summary

On 2026-07-14, an internal file-share service accepted an upload with a crafted filename that bypassed path validation. The flaw was discovered during a routine audit, before any observed exploitation.

## Impact

No customer data was accessed. Internal test fixtures were temporarily exposed to employees with the shared-link role.

## Timeline

09:12 — Audit script flags anomalous filename handling. 09:40 — Service disabled by the on-call engineer. 11:05 — Patch deployed; path validation hardened. 14:00 — Post-incident review scheduled.

## Actions

The service now rejects filenames containing traversal sequences at the gateway. Audit coverage for path-handling endpoints was added to the weekly scan.

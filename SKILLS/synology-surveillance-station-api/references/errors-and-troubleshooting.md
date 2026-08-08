# Errors and troubleshooting

## Common codes

The guide's common WebAPI table includes:

| Code | Meaning |
|---:|---|
| 100 | Unknown error |
| 101 | Invalid/missing API parameters |
| 102 | API does not exist |
| 103 | Method does not exist |
| 104 | API version unsupported |
| 105 | Permission denied |
| 106 | Session timeout |
| 107 | Duplicate-login interruption |

API families contain their own error tables; numeric meanings can be contextual. Consult the exact family section before remediation.

## Diagnostic sequence

1. Capture package version, API/method/version/path, HTTP status/content type, numeric code, and redacted response.
2. Rediscover API metadata for 102–104.
3. Verify the session with `SurveillanceStation.Info.GetInfo` or another harmless authorized read.
4. For 105, inspect Surveillance Station privilege assignment, camera/server ownership, CMS routing, license/capability, and object scope; do not jump directly to an admin account.
5. Resolve target IDs fresh and verify they belong to the intended server/camera/category.
6. Check package/license/device connectivity, storage/quota/retention/lock state, and task status.
7. For media endpoints, detect JSON error bodies masquerading behind an expected binary request.
8. For ambiguous timeout, reconcile whether the server operation continued before retrying.
9. Retry only idempotent reads/status calls unless operation-specific evidence proves replay is safe.

## Common failure classes

- Camera offline/credential/capability mismatch.
- Unsupported vendor feature or stream profile.
- CMS owner-server redirection or stale IDs.
- Insufficient license/quota/storage.
- Locked/retained recording or snapshot.
- Task already running, expired, or partially complete.
- Time-range/time-zone mismatch.
- Notification provider authentication/network failure.
- External service/TLS/DNS failure.
- Account privilege differs by camera/group/device.

Preserve logs and evidence before clearing alerts/logs/recordings during an incident.

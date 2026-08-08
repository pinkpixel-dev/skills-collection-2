---
name: synology-surveillance-station-api
description: Build, audit, troubleshoot, and document secure clients and automations for Synology Surveillance Station WebAPI 3.11. Use for API discovery/authentication, cameras and groups, snapshots, PTZ, live/event streams, recordings and exports, CMS, logs/licenses, action rules, e-maps, notifications, alerts, VisualStation, access controllers, I/O modules, Home Mode, transactions, archiving, YouTube Live, IVA analytics, face recognition/results, bookmarks, error handling, privacy, and safe mutation verification.
---

# Surveillance Station WebAPI

Use the official version 3.11 guide as a comprehensive protocol reference while treating live `SYNO.API.Info` and the installed Surveillance Station version as authoritative.

## Critical safety and privacy boundary

- Treat cameras, recordings, snapshots, faces, access-control logs, transactions, analytics, and location/e-map data as highly sensitive personal/security data.
- Begin with read-only discovery and least-privilege accounts.
- Obtain explicit authorization before adding/deleting/disabling cameras, formatting SD cards, deleting/truncating/unlocking recordings, changing notification/action rules, moving PTZ, controlling doors/outputs, triggering external events, altering Home Mode, deleting face data, publishing to YouTube, or changing CMS/archiving.
- Never use `Recording.DeleteAll`, `DeleteFilter`, bulk snapshot/IVA/face deletion, `Camera.Delete`, or `FormatSDCard` without exact target resolution, retention/backup review, and explicit destructive authorization.
- Never expose camera credentials, DSM credentials, session IDs, stream URLs, tokens, notification secrets, SMTP/SMS credentials, access-card data, faces, or video URLs in logs or reports.
- Use verified HTTPS and private LAN/VPN/Access routing. Do not publicly expose DSM or raw surveillance endpoints merely because streaming works.
- Preserve evidence during security incidents; separate containment from deletion.

## Read references selectively

- Read [references/protocol-and-client.md](references/protocol-and-client.md) for discovery, auth, requests, responses, version negotiation, polling, binary/stream handling, and client design.
- Read [references/api-catalog.md](references/api-catalog.md) for all 59 documented API families and method groups.
- Read [references/media-retention-and-privacy.md](references/media-retention-and-privacy.md) for recordings, snapshots, exports, streams, retention, analytics, faces, access control, and verification.
- Read [references/errors-and-troubleshooting.md](references/errors-and-troubleshooting.md) for common errors and diagnostic workflow.
- Read [references/source-notes.md](references/source-notes.md) for provenance, guide revision, and extraction/navigation details.
- Consult [assets/Surveillance_Station_Web_API.pdf](assets/Surveillance_Station_Web_API.pdf) for exact parameter tables, versions, response objects, valid-value appendix, and API-specific errors.
- Use [scripts/surveillance_client.py](scripts/surveillance_client.py) as a dependency-free discovery/auth/request reference client. Mutating calls require an explicit `mutation=True` acknowledgment.

## Required workflow

1. Classify the requested operation by privacy, physical-security, availability, and destructiveness impact.
2. Verify installed Surveillance Station version, package health, DSM origin/TLS, and account privileges.
3. Query fixed `/webapi/query.cgi` with `SYNO.API.Info`; discover Auth and every requested API's live path and version range.
4. Negotiate only versions implemented by the client; the guide warns old versions may be dropped.
5. Authenticate a dedicated least-privilege session named `SurveillanceStation`; retain cookie or SID only in protected memory.
6. Resolve exact camera/recording/task/group/face/device IDs with a fresh read before mutation.
7. Explain effects and obtain explicit authorization where required.
8. Send encoded POST requests with timeouts, bounded responses, redaction, and idempotency-aware retries.
9. Poll asynchronous search/export/import/archiving tasks to a terminal result and clean/reconcile them.
10. Verify through a separate read/list/status/snapshot check; inspect collateral recording, notification, stream, and device state.
11. Log out and clear all tokens/URLs.

## Mutation gates

### Camera/PTZ/I/O/access control

- Confirm physical device, owner server, ID, current state, affected views/rules, and human safety.
- PTZ or door/output operations can cause real-world movement/access; require explicit scope and avoid loops.
- SD formatting is permanent media destruction.

### Recordings/snapshots/analytics/faces

- Identify exact IDs/time ranges/categories and lock/retention state.
- Confirm legal/privacy/incident-hold requirements and backup/export readability.
- Never unlock evidence merely to make deletion succeed.
- Verify only intended objects changed.

### Streaming/publication/notifications

- Treat stream URLs as bearer secrets.
- Bound stream duration/bandwidth and close connections.
- Redact recipient/provider credentials.
- YouTube Live or external notification changes create external disclosure and require explicit approval.

## Code-generation standard

- Separate transport, discovery, authentication, version negotiation, typed API operations, task polling, media streaming, and redaction.
- Stream binary/video data to controlled destinations; never buffer unbounded media.
- Reject redirects to unexpected origins and unexpected JSON vs binary content types.
- Use finite pagination and stable filters.
- Retry only idempotent reads/status calls by default.
- Test against fixtures/fake servers, never live cameras or production recordings.

## Completion standard

Report live package/API versions, exact redacted target IDs, authorization boundary, operation result, independent verification, media/retention impact, privacy exposure, task cleanup, and rollback/recovery state. HTTP success alone is insufficient.

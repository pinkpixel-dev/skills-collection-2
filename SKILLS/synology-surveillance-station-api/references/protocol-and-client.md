# Protocol and client workflow

## Discovery and operation flow

The guide defines `/webapi/query.cgi` as the fixed unauthenticated `SYNO.API.Info` endpoint. Flow:

```text
Info.Query -> Auth.login -> target API calls -> Auth.logout
```

Info descriptors include path and version range. Use the discovered path; do not assume every API remains at `entry.cgi`.

Logical request:

```text
GET|POST /webapi/<path>?api=<api>&method=<method>&version=<version>&_sid=<sid>&...
```

Prefer POST form bodies so SIDs, device identifiers, and sensitive filters do not enter URLs/logs. Use verified HTTPS. The guide's examples use historical HTTP/private IPs and are not deployment guidance.

## Authentication

Discover `SYNO.API.Auth`, then login with account, password, session `SurveillanceStation`, and supported format. Use a dedicated account with only required Surveillance Station privileges. Never recommend admin merely to bypass error 105 without investigating the privilege model.

Log out after use. Clear SID/cookies even when logout fails.

## Response handling

JSON calls use a `success` envelope with `data` or `error`. Validate HTTP status, content type, JSON shape, and Boolean success. Binary endpoints (snapshots, downloads, streams, e-map images, photos) can return media; detect JSON error payloads before writing output.

Preserve contextual API/method/version and numeric error code while redacting request secrets. Inspect per-item errors and task status for partial failure.

## Version negotiation

Select:

```text
min(server.maxVersion, client_highest_supported)
```

and require it to be at least both client and server minimums. Do not automatically adopt newer versions without handling parameter/response differences. The document itself warns that old versions can be dropped.

## Asynchronous operations

Camera/VisualStation/I/O searches, recording range exports, archiving batch edits, and similar jobs return task/progress state. Use bounded polling with backoff and a deadline. On timeout, reconcile server state before retrying or starting another job. Cancel/stop only when explicitly intended.

## Pagination and time ranges

Use finite `start`/`offset` and `limit`, stable filters, and returned totals. Time units and interval semantics vary by API; consult the exact method table. Convert time zones explicitly and verify inclusive/exclusive endpoints to avoid deleting/exporting the wrong footage.

## Media responses

- Stream to a temporary controlled file or directly to an authorized client.
- Cap expected size/duration and enforce timeouts.
- Validate MIME type and magic where practical.
- Do not trust Content-Disposition filenames.
- Use restrictive permissions and retention cleanup.
- Never embed a SID or stream URL in long-lived HTML/logs.

## Safe client structure

1. Transport with TLS/origin pinning, timeouts, size limits, and redaction.
2. Discovery cache scoped to DSM origin/package version.
3. Auth lifecycle.
4. Typed read-only operations.
5. Mutation layer requiring explicit acknowledgment and exact IDs.
6. Task polling/reconciliation.
7. Binary/stream sink with cleanup.
8. Audit record containing no media or secrets.

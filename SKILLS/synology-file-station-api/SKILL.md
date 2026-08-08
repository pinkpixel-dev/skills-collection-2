---
name: synology-file-station-api
description: Build, audit, troubleshoot, and document clients and automations for the Synology DSM File Station WebAPI. Use for SYNO.API.Info, SYNO.API.Auth, and SYNO.FileStation APIs; DSM file listing, search, upload, download, sharing, folders, rename, copy/move, delete, archive extraction/compression, favorites, checksums, thumbnails, virtual folders, permissions, asynchronous background tasks, request encoding, authentication, version negotiation, and File Station error handling.
---

# Synology File Station API

Use the official 2023.03 File Station API guide as the protocol authority while treating the target NAS's live `SYNO.API.Info` response as the authority for supported paths and versions.

## Safety boundary

- Treat the DSM as a live, stateful system.
- Begin with discovery and read-only calls.
- Obtain explicit authorization before deleting files, overwriting existing data, moving irreplaceable data, stopping tasks, or changing public exposure.
- Resolve and verify every affected DSM path before mutation. Never infer a shared-folder path from a local filesystem path.
- Avoid broad recursive operations and wildcard-like path construction.
- Preserve recoverability for consequential changes. Prefer copy plus verification before move or delete.
- Never print passwords, session IDs, cookies, OTPs, sharing credentials, or secret query strings.
- Use HTTPS. Do not disable TLS verification except for a clearly scoped diagnostic on a trusted LAN, and state the risk.
- Log out in a `finally`/cleanup path. The guide says SIDs expire after seven days by default; do not rely on expiry as cleanup.

## Source routing

Read only what the task needs:

- Read [references/protocol-and-workflows.md](references/protocol-and-workflows.md) for discovery, authentication, request construction, encoding, responses, pagination, asynchronous tasks, upload/download, and secure client design.
- Read [references/api-catalog.md](references/api-catalog.md) for API families, versions, methods, parameters, response shapes, and operational cautions.
- Read [references/errors-and-troubleshooting.md](references/errors-and-troubleshooting.md) for common and API-specific error codes and a diagnostic sequence.
- Read [references/source-notes.md](references/source-notes.md) for document provenance, release history, extraction facts, and scope limitations.
- Consult [assets/Synology_File_Station_API_Guide.pdf](assets/Synology_File_Station_API_Guide.pdf) when exact wording, availability by version, or a field omitted from the condensed references matters. Extract a narrow section with `pdftotext -layout`, then search it; do not load the entire document unless necessary.
- Use [scripts/filestation_client.py](scripts/filestation_client.py) as a dependency-free Python reference client for discovery, version negotiation, SID authentication, JSON calls, bounded multipart upload, streamed download, and cleanup.

## Required workflow

1. Identify whether the request is read-only, stateful, destructive, or security-sensitive.
2. Discover live API metadata with `SYNO.API.Info` at `/webapi/query.cgi`; do not hard-code a File Station CGI path or assume the guide's maximum version exists on the target DSM.
3. Select the highest version supported by both the client behavior and `minVersion..maxVersion` returned by the NAS.
4. Authenticate through `SYNO.API.Auth` using a dedicated least-privilege account and a session name such as `FileStation`.
5. Construct requests with a real URL/form encoder. Preserve DSM path semantics and encode parameters exactly once.
6. Validate the response envelope before reading `data`.
7. For non-blocking operations, persist `taskid`, poll at a bounded interval, recognize terminal state, stop only when authorized, and clean search state when required.
8. Verify the outcome end to end: inspect returned metadata and independently list/stat/download the target when appropriate.
9. Log out and redact authentication material from diagnostics.

## Request rules

- Use `/webapi/query.cgi` only to discover APIs. Use the returned `path` for every other API.
- Include `api`, `version`, and `method` on every call.
- Pass authentication using either `_sid` or the DSM `id` cookie. Prefer keeping it out of persistent URLs and logs.
- Send passwords only in encoded POST form data, never in a logged command line or URL.
- Represent multiple DSM paths using the format required by the live API/version. The guide commonly shows a JSON-like bracketed list serialized into one parameter; use a standards-based encoder rather than manual percent escapes.
- Treat timestamps carefully: most search/file metadata uses Unix seconds, while Upload `mtime`, `crtime`, and `atime` use Unix milliseconds.
- For list methods, page with `offset` and a finite `limit`; stop using the response's total/offset count, not an empty-page guess alone.
- Request only necessary `additional` fields because metadata expansion can be expensive.

## Response rules

Expect a JSON envelope:

```json
{"success": true, "data": {}}
```

or:

```json
{"success": false, "error": {"code": 105}}
```

- Test `success` first.
- Preserve numeric `error.code`, API name, method, HTTP status, and a redacted correlation context.
- Inspect nested per-path `errors` when an aggregate operation reports partial failure.
- Do not mistake HTTP 200 for operation success.
- Treat binary thumbnail/download responses separately from JSON envelopes.

## Mutation gates

Before Upload, CreateFolder, Rename, CopyMove, Delete, Extract, Compress, Sharing mutation, or task cancellation:

1. Enumerate exact source and destination paths.
2. Confirm account permissions and available space where relevant.
3. Decide collision behavior explicitly; never omit `overwrite` accidentally.
4. Explain whether the method blocks or returns a task.
5. Preserve or verify a backup when the source is important.
6. Execute the narrowest call.
7. Verify both expected outputs and source retention/removal behavior.

For deletion, require explicit authorization for the exact paths and recursive behavior. A successful Delete API response is not proof that unrelated paths were unaffected; relist the parent and confirm narrowly.

## Code-generation standard

When generating a client:

- Separate transport, authentication, API discovery, version selection, and operation logic.
- Use timeouts, TLS verification, bounded retries with jitter, and idempotency-aware retry rules.
- Retry discovery/list/status calls for transient transport errors; do not blindly retry upload, rename, move, delete, extraction, compression, or sharing mutation.
- Stream uploads/downloads rather than loading large files into memory.
- Put the multipart binary file part last for `SYNO.FileStation.Upload` as required by the guide.
- Write downloads to a temporary sibling path, flush/sync if durability matters, validate status/content type/size, then atomically rename.
- Redact `_sid`, cookies, account passwords, archive passwords, and sharing passwords in logs.
- Make tests use a fake HTTP server or fixtures; never point tests at production DSM data.

## Completion standard

Report:

- Live API path and negotiated version used.
- Operation performed and exact scoped DSM paths, with secrets redacted.
- Response and end-to-end verification result.
- Background task completion/cleanup state.
- Any partial failures, rollback data, or unresolved version differences.

Do not claim success from request completion alone.

# Protocol and workflows

## Contents

- Discovery and version negotiation
- Authentication lifecycle
- Request construction and encoding
- Response handling
- Pagination and metadata expansion
- Non-blocking operations
- Upload and download
- Secure implementation pattern
- Verification recipes

## Discovery and version negotiation

Start at the fixed endpoint:

```http
GET /webapi/query.cgi?api=SYNO.API.Info&version=1&method=query&query=all
```

Each returned API object contains `path`, `minVersion`, and `maxVersion`. Build the endpoint as `/webapi/` plus the returned path. Discovery prevents brittle assumptions across DSM releases.

Select a version with:

```text
selected = min(server.maxVersion, client_highest_implemented_version)
require selected >= server.minVersion
```

Do not automatically select a higher version unless client parameter and response handling supports its semantics. Upload collision behavior, for example, differs across versions.

## Authentication lifecycle

Call the discovered `SYNO.API.Auth` path with `method=login`.

Core fields:

| Field | Meaning |
|---|---|
| `account` | DSM account name |
| `passwd` | Account password |
| `session` | Logical session name; use `FileStation` |
| `format` | `sid` returns the SID in JSON; `cookie` sets the `id` cookie |
| `otp_code` | Reserved/version-dependent in the guide; do not assume modern DSM behavior without live verification |

Use POST form data over verified HTTPS. Keep credentials out of shell history, URLs, exception text, and debug logs. Pass `_sid` on subsequent calls or retain the `id` cookie. Log out with `SYNO.API.Auth`, `method=logout`, and the same session name.

Authentication errors 400–404 are API-specific and overlap numerically with File Station errors. Interpret a code in the context of the API that returned it.

## Request construction and encoding

Logical request shape:

```text
/webapi/<discovered-path>?api=<name>&version=<n>&method=<method>&<parameters>
```

Use `application/x-www-form-urlencoded` POST for JSON-style operations unless a binary endpoint requires otherwise. GET examples in the guide illustrate semantics but are not a security recommendation.

Important encoding rules:

- URL-encode once with a library.
- Treat DSM paths as strings beginning with a shared-folder component, for example `/video/example.mkv`.
- Several multi-value fields are serialized as a bracketed list within one form field. Generate the list representation first, then form-encode it.
- The guide also describes comma-separated values and escaping commas/backslashes. Prefer actual behavior discovered/tested against the selected API version and avoid hand-building percent escapes.
- Keep passwords opaque; do not apply path-list escaping to password fields.
- Boolean examples use lowercase `true`/`false`.
- Search time criteria are Unix seconds. Upload file times are Unix milliseconds.

## Response handling

JSON calls use an envelope with a Boolean `success`. On success, `data` may be absent, an object, or a list container. On failure, `error.code` is present and an API may add nested details.

Implementation sequence:

1. Validate HTTP status and response content type.
2. Decode JSON with a size limit appropriate to the operation.
3. Require a Boolean `success`.
4. If false, map the code using both common and current-API tables.
5. Inspect nested `errors` for per-item failures.
6. Return typed/validated `data`, not the raw envelope, when building a reusable library.

Binary endpoints such as Download and Thumb must not be passed through the JSON parser. A server-side failure may still arrive as JSON, so inspect status and content type before streaming to the final destination.

## Pagination and metadata expansion

List-style methods generally expose `offset`, `limit`, sorting, and a returned total. Use stable sort criteria where possible. Page until the next offset reaches the returned total. Protect against a server returning the same page repeatedly.

The `additional` parameter can request metadata such as real path, size, owner, time, permissions, mount point type, type, and sync/share information depending on the API. Request only needed fields and tolerate unsupported additions when targeting varied DSM generations.

## Non-blocking operations

Search, directory-size calculation, MD5 calculation, CopyMove, Delete, Extract, and Compress expose asynchronous workflows. Common lifecycle:

```text
start -> taskid -> status/list polling -> terminal state -> optional cleanup
```

Search is special:

```text
start -> taskid -> list (possibly repeatedly) -> stop if cancelling -> clean when finished
```

Search results remain in a temporary database until `clean` is called. Treat cleanup as part of successful completion.

Polling guidance:

- Poll every 1–3 seconds initially and back off for long jobs.
- Set a total deadline appropriate to data size.
- Do not equate `finished=true` with success without checking error/result fields.
- Persist task IDs only as long as needed and avoid exposing them publicly.
- On client cancellation, ask the API to stop only if stopping the server operation is intended.
- Use `SYNO.FileStation.BackgroundTask.list` to reconcile copy/move/delete/extract/compress jobs when client state is lost.

## Upload

Upload uses `multipart/form-data` and RFC 1867-style construction. Required/important fields include destination `path`, `create_parents`, collision `overwrite`, optional file timestamps, and the binary file part.

The binary file data must be the last multipart part. Ensure `Content-Length` is correct when the HTTP client emits it. Stream the body for large files.

Collision semantics vary by version:

- Version 2 examples use Boolean `true`/`false`.
- Version 3 documents string-like `overwrite`/`skip` behavior.
- Omitting a collision choice can produce error 1805 when a target exists.

Preflight with `SYNO.FileStation.CheckPermission.write` when useful, but still handle races between preflight and upload.

## Download

Download accepts a DSM file path and returns binary content. Stream to a temporary local file. Reject unexpected JSON/HTML responses, validate expected length or checksum when available, then rename into place.

Do not use a browser-facing Content-Disposition filename as an unchecked local path. Normalize it to a basename or use a caller-supplied destination.

## Secure implementation pattern

- Use a dedicated DSM account with access only to required shared folders.
- Keep the DSM management endpoint LAN/VPN/private-tunnel scoped.
- Validate TLS with a trusted certificate or explicit private CA.
- Configure connect and read timeouts independently.
- Bound response sizes for JSON and thumbnails.
- Retry only idempotent calls by default.
- Serialize destructive requests with an operation record containing target paths and authorization context.
- Redact URL query parameters and cookies from transport traces.

## Verification recipes

### Read-only listing

1. Discover List path/version.
2. Call `list_share` or `list` with a finite limit.
3. Confirm returned offset/total logic.
4. Compare a sample entry with DSM File Station or a second API request.

### Upload

1. Check local source size/hash.
2. Verify destination folder and collision policy.
3. Upload with file part last.
4. List destination and compare size.
5. Optionally calculate remote MD5 and compare.

### Copy or move

1. List exact sources and destination.
2. Record collision and `remove_src` behavior.
3. Start task and poll status.
4. Confirm every destination exists.
5. For move, confirm sources are absent only after destination verification.

### Delete

1. Obtain explicit authorization for exact paths and recursion.
2. Record/relist targets immediately before the call.
3. Start and poll, or use blocking delete only for small, controlled work.
4. Re-list the parent directories and confirm only intended entries disappeared.

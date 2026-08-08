# API catalog

## Contents

- Base APIs
- Read and metadata APIs
- Search and calculation APIs
- Transfer and sharing APIs
- Filesystem mutation APIs
- Archive and background-task APIs
- Shared response objects and field notes

The version numbers below are the guide's documented maxima, not a promise about a live NAS. Discover the supported range with `SYNO.API.Info` and negotiate it.

## Base APIs

### `SYNO.API.Info` — version 1, DSM 4.0+

`query`: Discover API names, CGI paths, and supported version ranges. `query=all` returns everything; a comma-separated subset limits results. Response objects include `path`, `minVersion`, and `maxVersion`.

### `SYNO.API.Auth` — documented through version 3

- `login`: Authenticate using `account`, `passwd`, `session`, optional `format`, and version-dependent `otp_code`. `format=sid` returns `data.sid`; cookie format sets the DSM `id` cookie.
- `logout`: End the named `session`.

The guide documents versions 2 (DSM 4.1+) and 3 (DSM 4.2+) and states that an SID expires after seven days by default. Modern DSM authentication behavior can evolve; verify live support.

## Read and metadata APIs

### `SYNO.FileStation.Info` — version 2, DSM 6.0+

`get`: Return File Station capability information such as administrator status, supported virtual protocols, sharing support, and DSM hostname.

### `SYNO.FileStation.List` — version 2, DSM 6.0+

- `list_share`: List shared folders. Supports `offset`, `limit`, `sort_by`, `sort_direction`, `onlywritable`, and `additional` metadata.
- `list`: Enumerate a `folder_path`. Supports pagination, sorting, optional glob `pattern`, `filetype` (`file`, `dir`, `all`), and `additional` metadata.

Common sort keys include `name`, `user`, `group`, `mtime`, `atime`, `ctime`, `crtime`, and `posix`. Response list objects generally include `offset`, `total`, and entries containing `name`, `path`, `isdir`, plus requested `additional` fields.

### `SYNO.FileStation.VirtualFolder` — version 2, DSM 6.0+

`list`: List virtual filesystem mount points for `type` such as `nfs`, `cifs`, or `iso`; supports pagination, sorting, and additional metadata. Treat protocol value casing as version-sensitive.

### `SYNO.FileStation.Favorite` — version 2, DSM 6.0+

- `list`: List the current user's favorites, with pagination, sorting, and optional metadata.
- `add`: Add a favorite using a DSM folder `path` and display `name`.
- `delete`: Remove one or more favorite paths.
- `clear_broken`: Remove favorites whose targets no longer exist.
- `edit`: Change favorite path/name metadata.

Favorite mutation changes user configuration, not underlying file content, but still verify the intended user's session.

### `SYNO.FileStation.Thumb` — version 2, DSM 6.0+

`get`: Return a thumbnail for a file `path`. Size/rotation/cache-related parameters vary; treat the response as binary and validate content type and maximum size.

### `SYNO.FileStation.CheckPermission` — version 3, DSM 6.0+

`write`: Check whether the session may create `filename` under folder `path`. Optional `overwrite` chooses collision behavior; `create_only` defaults true. Success means permission is currently acceptable, but it cannot eliminate a race with the following write.

## Search and calculation APIs

### `SYNO.FileStation.Search` — version 2, DSM 6.0+

- `start`: Start a search in one or more `folder_path` values. Criteria include `recursive`, filename `pattern`, `extension`, `filetype`, `size_from`, `size_to`, time ranges, owner/group, and additional filters documented by the selected version. Multiple criteria are ANDed.
- `list`: Page through results for `taskid`, with sorting and optional metadata expansion.
- `stop`: Cancel the search task.
- `clean`: Delete the search task's temporary result database. Call this after consuming results.

Glob behavior is case-insensitive in the guide. If a name pattern contains no `?` or `*`, DSM adds surrounding wildcards for partial matching. Extensions can contain comma-separated patterns.

### `SYNO.FileStation.DirSize` — version 2, DSM 6.0+

- `start`: Begin recursive size calculation for one or more DSM paths; returns `taskid`.
- `status`: Return task progress/result.
- `stop`: Cancel calculation.

### `SYNO.FileStation.MD5` — version 2, DSM 6.0+

- `start`: Begin MD5 calculation for a DSM file path; returns `taskid`.
- `status`: Return progress and digest when complete.
- `stop`: Cancel calculation.

MD5 is useful for transfer-integrity checks but is not collision-resistant and must not be used as a security authenticity proof.

## Transfer and sharing APIs

### `SYNO.FileStation.Upload` — version 2 in overview; later semantics documented

`upload`: Multipart upload to destination folder `path`. Fields include `create_parents`, `overwrite`, optional millisecond timestamps (`mtime`, `crtime`, `atime`), and binary file content. The binary file part must be last. Collision values differ by API version; inspect the live range and use explicit semantics.

### `SYNO.FileStation.Download` — version 2, DSM 6.0+

`download`: Stream a file from DSM `path`. Handle as binary, but detect JSON error envelopes before committing output.

### `SYNO.FileStation.Sharing` — version 3, DSM 6.0+

- `list`: List sharing links, typically with pagination and sorting/filtering.
- `create`: Create links for one or more DSM paths. Depending on version, options may include link password, validity/expiry, and destination behavior.
- `delete`: Remove sharing links by IDs/paths.
- `edit`: Modify sharing-link configuration.

Sharing links can create external access. Before `create` or `edit`, verify authentication, expiry, password policy, reverse-proxy behavior, and intended public reachability. Never log sharing passwords or full secret-bearing URLs.

## Filesystem mutation APIs

### `SYNO.FileStation.CreateFolder` — version 2, DSM 6.0+

`create`: Create one or more `name` values under `folder_path`; `force_parent` can create missing parents. Response may contain created folder objects and nested errors. Validate each name and avoid unintended parent creation.

### `SYNO.FileStation.Rename` — version 2, DSM 6.0+

`rename`: Rename one or more source `path` entries to corresponding `name` entries. Preserve ordering between parallel lists. Inspect per-item errors and verify the old/new paths.

### `SYNO.FileStation.CopyMove` — version 3, DSM 6.0+

- `start`: Start copy/move for one or more source `path` values to `dest_folder_path`; returns `taskid`.
- `status`: Poll progress and result.
- `stop`: Cancel the task.

Key controls:

| Parameter | Purpose |
|---|---|
| `overwrite` | Explicit overwrite, skip, or error-on-collision behavior depending on version |
| `remove_src` | `false` copies; `true` moves |
| `accurate_progress` | More detailed recursive accounting at a performance cost |
| `search_taskid` | Update/reconcile related search results |

For moves, do not report success until destination verification and source absence checks both pass.

### `SYNO.FileStation.Delete` — version 2, DSM 6.0+

- `start`: Non-blocking delete; returns `taskid`.
- `status`: Poll deletion progress/result.
- `stop`: Cancel a running deletion.
- `delete`: Blocking deletion that returns only after completion.

Important fields include one or more `path` values, `recursive`, `accurate_progress`, and optional `search_taskid`. Deletion requires explicit authorization for the exact targets and recursion behavior. Never assume File Station deletion enters a recoverable recycle bin.

## Archive and background-task APIs

### `SYNO.FileStation.Extract` — version 2, DSM 6.0+

- `start`: Extract `file_path` into `dest_folder_path`; returns `taskid`.
- `status`: Poll extraction.
- `stop`: Cancel extraction.
- `list`: Enumerate archive items and obtain `item_id` values for selective extraction.

Controls include `overwrite`, `keep_dir`, `create_subfolder`, `codepage`, optional archive `password`, and selected `item_id` values. The guide lists zip, gz, tar, tgz, tbz, bz2, rar, 7z, and iso support. Treat archive extraction as untrusted input: avoid destination escape, verify resulting paths, and do not log passwords.

### `SYNO.FileStation.Compress` — version 3, DSM 6.0+

- `start`: Compress source `path` values to `dest_file_path`; returns `taskid`.
- `status`: Poll compression.
- `stop`: Cancel compression.

`level`: `moderate`, `store`, `fastest`, or `best`.

`mode`: `add`, `update`, `refreshen`, or `synchronize`.

`format`: `zip` or `7z`. An optional archive `password` is sensitive.

### `SYNO.FileStation.BackgroundTask` — version 3, DSM 6.0+

`list`: List copy, move, delete, extract, and compress jobs. Supports `offset`, `limit`, `sort_by` (`crtime`/`finished`), `sort_direction`, and `api_filter` containing relevant API names.

Use this API for reconciliation and monitoring. Cancel through the originating API's `stop` method because BackgroundTask itself is a listing interface in this guide.

## Shared response objects and field notes

File entries commonly contain:

| Field | Meaning |
|---|---|
| `name` | Entry basename |
| `path` | DSM File Station path |
| `isdir` | Directory flag |
| `additional` | Requested expanded metadata object |

Frequently available additions include `real_path`, `size`, `owner`, `time`, `perm`, `mount_point_type`, `type`, and sharing/synchronization data. Exact availability depends on API and version.

Time objects may expose modification, access, change, and creation times. POSIX permissions and DSM ACL authorization are not interchangeable; a write preflight or actual API result is more authoritative than reasoning from mode bits alone.

For list-like responses, preserve server-reported `offset` and `total`. For task responses, preserve `taskid`, completion flag, progress, and any nested result/error fields. For multi-path operations, verify cardinality and ordering of parallel arrays before submission.

# Errors and troubleshooting

## Contents

- Interpretation rules
- Common WebAPI errors
- Common File Station errors
- API-specific errors
- Diagnostic sequence

## Interpretation rules

Interpret error codes in the context of the API and method that returned them. Codes 400–404 are overloaded: `SYNO.API.Auth` assigns authentication meanings, while File Station operations assign filesystem meanings.

Do not discard nested `errors` on aggregate operations. A top-level CopyMove, CreateFolder, Rename, or Delete failure may point to per-path detail.

## Common WebAPI errors

| Code | Meaning |
|---:|---|
| 100 | Unknown error |
| 101 | Missing API, method, or version parameter |
| 102 | Requested API does not exist |
| 103 | Requested method does not exist |
| 104 | Requested version does not support the function |
| 105 | Session lacks permission |
| 106 | Session timed out |
| 107 | Session interrupted by duplicate login |
| 119 | SID not found |

For 102–104, repeat live `SYNO.API.Info` discovery and inspect the selected path/version. For 105, verify both DSM account rights and shared-folder ACLs. For 106/107/119, authenticate again once; do not loop indefinitely.

## Common File Station errors

| Code | Meaning |
|---:|---|
| 400 | Invalid file-operation parameter |
| 401 | Unknown file-operation error |
| 402 | System too busy |
| 403 | Invalid user for this operation |
| 404 | Invalid group for this operation |
| 405 | Invalid user and group |
| 406 | Cannot get account-server user/group information |
| 407 | Operation not permitted |
| 408 | No such file or directory |
| 409 | Unsupported filesystem |
| 410 | Failed to connect an internet-based filesystem such as CIFS |
| 411 | Read-only filesystem |
| 412 | Filename too long on non-encrypted filesystem |
| 413 | Filename too long on encrypted filesystem |
| 414 | File already exists |
| 415 | Disk quota exceeded |
| 416 | No space left on device |
| 417 | Input/output error |
| 418 | Illegal name or path |
| 419 | Illegal filename |
| 420 | Illegal filename on FAT filesystem |
| 421 | Device or resource busy |
| 599 | No such file-operation task |

Treat 417 as potentially serious storage evidence; avoid retries that could amplify damage. For 410, diagnose the remote mount separately. For 599, reconcile with BackgroundTask and confirm whether the task expired or belongs to another session.

## API-specific errors

### Authentication

| Code | Meaning |
|---:|---|
| 400 | No such account or incorrect password |
| 401 | Account disabled |
| 402 | Permission denied |
| 403 | Two-step verification code required |
| 404 | Two-step verification authentication failed |

### Favorite

| Code | Meaning |
|---:|---|
| 800 | Folder path already exists in favorites |
| 801 | Favorite name conflicts with an existing favorite path/name |
| 802 | Too many favorites |

### Upload

| Code | Meaning |
|---:|---|
| 1800 | Missing Content-Length or received size mismatch |
| 1801 | Timed out waiting for client data; guide notes a 3600-second default |
| 1802 | Last content part lacks filename information |
| 1803 | Upload connection cancelled |
| 1804 | Oversized file for FAT filesystem |
| 1805 | Existing target cannot be overwritten/skipped because collision behavior was omitted |

### Sharing

| Code | Meaning |
|---:|---|
| 2000 | Sharing link does not exist |
| 2001 | Too many sharing links to create another |
| 2002 | Failed to access sharing links |

### CreateFolder and Rename

| Code | Meaning |
|---:|---|
| 1100 | Folder creation failed; inspect nested `errors` |
| 1101 | Parent folder would exceed the system folder-count limit |
| 1200 | Rename failed; inspect nested `errors` |

### CopyMove

| Code | Meaning |
|---:|---|
| 1000 | Copy failed; inspect nested `errors` |
| 1001 | Move failed; inspect nested `errors` |
| 1002 | Destination error; inspect nested `errors` |
| 1003 | Existing target encountered without overwrite/skip behavior |
| 1004 | File/folder type collision prevents overwrite |
| 1006 | FAT32 rejects special characters in source name |
| 1007 | FAT32 rejects a file larger than 4 GiB |

### Delete

| Code | Meaning |
|---:|---|
| 900 | Delete failed; inspect nested `errors` |

### Extract

| Code | Meaning |
|---:|---|
| 1400 | Extraction failed |
| 1401 | Cannot open input as an archive |
| 1402 | Archive data read failed |
| 1403 | Wrong archive password |
| 1404 | Failed to enumerate archive contents |
| 1405 | Archive item ID not found |

### Compress

| Code | Meaning |
|---:|---|
| 1300 | Compression failed |
| 1301 | Archive name is too long |

## Diagnostic sequence

1. Record API name, method, selected version, discovered path, HTTP status, response content type, and redacted error envelope.
2. Repeat `SYNO.API.Info` discovery for 102–104 or unexplained routing failures.
3. Verify the session once using a harmless read-only call.
4. Confirm the exact DSM path, shared-folder visibility, and account ACLs.
5. Check destination existence and collision policy.
6. Check free space/quota and filesystem limits for 409–420 and FAT-related errors.
7. For task failures, poll the originating API and reconcile `BackgroundTask.list` before assuming the task vanished.
8. For multipart failures, inspect part order, filename disposition, boundary, byte count, timeout, and whether a proxy buffered/truncated the body.
9. Retry only if the failure is transient and the method is safe to repeat.
10. Verify end state before reporting failure or success; a timed-out client may leave a server task running.

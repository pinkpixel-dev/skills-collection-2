# Synology hexadecimal error numbers

## Interpretation

The guide lists internal symbolic errors in hexadecimal increments. A shell exit status may be truncated to 8 bits and is not necessarily the full Synology error value. Preserve stderr/stdout and command context. Do not infer a specific symbol from exit status alone unless the utility documents that mapping.

## High-value categories

| Range/examples | Category | Response |
|---|---|---|
| `0x0000` | Success | Still verify end state |
| `0x0100`–`0x0500` | Memory/locking | Check pressure and conflicting process; avoid blind retries |
| `0x0600`–`0x0D00` | Paths/files/parameters | Resolve target and validate live syntax |
| `0x0E00`–`0x1F00` | Server/domain/share/group/user | Verify naming, existence, limits, and authority |
| `0x2400`–`0x2900` | Quota/space/seek/stat | Check volume health, quota, space, and filesystem evidence |
| `0x2A00`–`0x3D00` | Operation/device/file mutation | Preserve evidence; inspect mounts and dependencies |
| `0x4000` | Format error | Treat as high risk; do not retry formatting |
| `0x5000`–`0x5600` | Backup/application import-export | Verify backup configuration and data before changes |
| `0x6000`–`0x6D00` | Volumes/disks/RAID/I/O | Stop risky mutation and investigate storage health |
| `0x7100`–`0x7B00` | Internal UDP daemon/maintenance | Inspect exact caller and service logs |
| `0x8000`–`0x8400` | Unknown/volume limit/not found/read-only | Gather context; avoid claiming a root cause |
| `0x9000`–`0x9900` | NIS/quota/fork/RAID enumeration/path | Inspect directory service, filesystem, and process limits |
| `0xA000`–`0xAC00` | Services/path/FAT/cancel/encryption | Respect cancellation and protect encryption keys |
| `0xB000`–`0xC300` | Database/reserved identities/domain/interface/name/filesystem | Verify internal DB and identity/network constraints |

## Critical symbols

- `ERR_DISK_IO_FAILED` (`0x6C00`) and `ERR_BAD_DISKSECTOR` (`0x6D00`): preserve evidence and assess storage health before write-heavy retries.
- `ERR_BROKEN_RAID_CONF` (`0x6800`) and `ERR_BROKEN_DISK_INFO` (`0x6B00`): do not attempt ad-hoc repair from this guide.
- `ERR_FORMAT_ERROR` (`0x4000`) and `ERR_FORMAT_FAIL` (`0x6600`): never respond by rerunning formatting.
- `ERR_ENCKEY_VERIFY` (`0xAB00`) and `ERR_ENCKEY_LOST` (`0xAC00`): protect keys and backups; do not rotate/delete evidence casually.
- `ERR_VOLUME_READ_ONLY` (`0x8400`): determine why the filesystem is read-only before remounting or modifying it.
- `ERR_NOT_ENOUGH_VOLUME_SPACE` (`0x2500`) and quota errors: distinguish volume capacity, user quota, metadata exhaustion, and reserved space.

## Diagnostic sequence

1. Capture command path, exact redacted arguments, DSM build, exit status, stdout, and stderr.
2. Check whether a full hexadecimal code was printed separately from shell status.
3. Read live `--help` and confirm syntax.
4. Inspect the target and dependent DSM object.
5. For storage/I/O/encryption errors, stop mutation and preserve logs/state.
6. For existence/name errors, do not delete the conflicting object automatically.
7. Apply the smallest corrective action and independently verify.

Consult the PDF's Chapter 3 for the complete symbol-by-symbol table.

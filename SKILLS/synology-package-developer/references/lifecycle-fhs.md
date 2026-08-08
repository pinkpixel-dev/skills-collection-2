# Lifecycle scripts, FHS, upgrades, and data safety

## Contents

- Script contracts
- Execution order
- Environment variables
- FHS
- Idempotency
- Upgrade design
- Uninstall design

## Script contracts

Required lifecycle scripts commonly include:

- `preinst`, `postinst`
- `preuninst`, `postuninst`
- `preupgrade`, `postupgrade`
- `start-stop-status`

Optional replacement hooks include `prereplace` and `postreplace`.

Use preflight scripts to validate conditions without side effects:

- `preinst`
- `preuninst`
- `preupgrade`

A nonzero preflight exit aborts the operation. Post-stage failures can leave a package corrupted; make them small, idempotent, and recoverable.

`start-stop-status` handles:

- `start`
- `stop`
- `status`
- optionally `prestart` and `prestop` when enabled

Status codes documented in the supplied guide:

| Code | Meaning |
|---|---|
| `0` | running |
| `1` | process dead, PID file exists |
| `2` | process dead, lock file exists |
| `3` | not running |
| `4` | unknown |
| `150` | broken; reinstall indicated |

Return the exact semantics expected by the target framework. Do not use `0` for status merely because the script executed.

## Execution order

Model operations explicitly:

- install: preflight → resource acquisition/hooks → postinstall → optional prestart/start
- upgrade: old pre-stop/stop → new preupgrade → old uninstall hooks → replacement hooks → new install hooks → new postupgrade → new prestart/start
- uninstall: prestop/stop → preuninst → postuninst
- boot: prestart may run on DSM 7 before start
- shutdown: prestop behavior differs from an interactive stop

Exact worker timing interleaves with scripts. Consult the selected resource worker's acquisition/release timing before choosing a hook.

## Environment variables

Common variables include:

- `SYNOPKG_PKGNAME`, `SYNOPKG_PKGVER`, `SYNOPKG_OLD_PKGVER`
- `SYNOPKG_PKGDEST`, `SYNOPKG_PKGDEST_VOL`
- `SYNOPKG_PKGVAR`, `SYNOPKG_PKGTMP`, `SYNOPKG_PKGHOME`
- `SYNOPKG_PKGINST_TEMP_DIR`
- `SYNOPKG_TEMP_UPGRADE_FOLDER`
- `SYNOPKG_TEMP_LOGFILE`, `SYNOPKG_PKG_PROGRESS_PATH`
- `SYNOPKG_TEMP_SPKFILE`
- `SYNOPKG_DSM_LANGUAGE`
- DSM version and architecture variables
- `SYNOPKG_PKG_STATUS`
- `SYNOPKG_USERNAME`

Treat all as external input:

```sh
: "${SYNOPKG_PKGNAME:?missing package name}"
test -n "${SYNOPKG_PKGVAR:-}" || exit 1
```

Do not echo their values indiscriminately; wizard values and paths can contain sensitive material.

## Package FHS

Stable links under `/var/packages/PACKAGE` point to volume or system storage:

| Link | Purpose | Lifecycle |
|---|---|---|
| `target` | immutable installed payload | replaced on upgrade |
| `etc` | persistent configuration | retained |
| `var` | persistent mutable application data/logs | retained |
| `tmp` | disposable temporary data | removed during upgrade/uninstall |
| `home` | private package home, normally mode `0700` | retained |

On volume installs, backing directories are generally under `@appstore`, `@appconf`, `@appdata`, `@apptemp`, and `@apphome`. Never hard-code `/volume1`; use framework paths.

Do not modify files in `target` at runtime when the state belongs in `etc`, `var`, or `home`. Target content may be replaced during upgrade.

## Idempotency and process control

- Starting an already-running service should not spawn duplicates.
- Stopping an already-stopped service should succeed safely.
- Use stable PID handling and verify PID ownership/executable before signaling.
- Avoid `killall` and broad process matches.
- Wait for graceful shutdown, then use a narrowly scoped escalation if documented.
- Write state atomically with restrictive umask.
- Use file locking for concurrent lifecycle operations.
- Never recursively chown paths derived from untrusted input.

## Upgrade design

1. Define supported source versions and schema transitions.
2. Refuse unsupported upgrade paths before mutation.
3. Back up configuration and databases using appropriate native tools.
4. Verify the backup exists and is readable.
5. Stage migrations separately from the live dataset when practical.
6. Make each migration versioned, resumable, and safe to rerun.
7. Preserve the old data until new-version health is proven.
8. Detect disk-space requirements before copying/migrating.
9. Restore service state: a previously stopped package should remain stopped.
10. Test failure at every boundary.

Never copy live database files as the sole backup unless the database's documented procedure says it is consistent.

## Uninstall design

Normal uninstall should:

- stop owned processes;
- remove framework-owned registrations and disposable files;
- preserve user-generated content, database exports, configuration, and shares by default;
- avoid deleting shared folders, Docker volumes, or external paths;
- remove only package-owned links/artifacts;
- report retained data and how to remove it separately.

If offering “remove all data”:

1. require an explicit wizard choice;
2. name every affected path/database/share;
3. validate each target;
4. refuse volume roots, share roots, empty paths, symlink surprises, and active mounts;
5. back up when appropriate;
6. distinguish upgrade from uninstall with `SYNOPKG_PKG_STATUS`;
7. log what was removed without exposing secrets.

Never hide permanent deletion in `postuninst`.

---
name: synology-dsm-admin-cli-guide
description: Safely inspect, plan, execute, and troubleshoot Synology DSM administrative command-line operations documented for synouser, synogroup, synoshare, synonet, synoservice, synowin, and Synology hexadecimal error numbers. Use for local users/groups, shared-folder configuration and ACLs, network settings, service state, workgroup or Active Directory membership, and interpreting DSM CLI errors, especially when auditing legacy scripts against DSM 7.
---

# Synology DSM administration CLI guide

Use the bundled 2021 Synology guide as a historical command reference, never as proof that a command or argument is supported on the live DSM release.

## Hard safety boundary

- Run the narrowest applicable `nas-context` mode before substantial NAS administration.
- Begin with read-only discovery: resolve command path, inspect `--help`, current objects, dependencies, privileges, and DSM version.
- Treat these CLIs as privileged, internal DSM interfaces. Do not assume backward compatibility.
- Obtain explicit authorization before deleting users/groups/shares, deleting shared-folder data, changing access, joining/leaving a domain, altering networking, or stopping/disabling services.
- Never pass passwords on a command line when a supported safer interface exists. Command arguments may appear in process listings, shell history, audit logs, or task definitions.
- Never run `synoshare --del TRUE` without explicit authorization for permanent deletion of the named share and its data.
- Never change the active interface, gateway, DNS, hostname, SSH, HTTPS, or authentication path without an out-of-band recovery route and a rollback command.
- Back up consequential DSM-managed configuration through supported means; do not blindly copy/restore internal databases.
- Preserve Synology ACLs and extended attributes. Do not substitute recursive `chmod`/`chown` for DSM ACL management.

## Read references selectively

- Read [references/commands.md](references/commands.md) for documented syntax, restrictions, side effects, and per-command verification.
- Read [references/errors.md](references/errors.md) to interpret the guide's hexadecimal error symbols and escalation categories.
- Read [references/legacy-and-safety.md](references/legacy-and-safety.md) for DSM 7 compatibility hazards, secrets, rollback, and remote-access protection.
- Read [references/source-notes.md](references/source-notes.md) for provenance and document completeness.
- Consult [assets/Synology_DiskStation_Administration_CLI_Guide.pdf](assets/Synology_DiskStation_Administration_CLI_Guide.pdf) for exact historical tables.

## Required workflow

1. Classify the request as read-only, reversible, disruptive, destructive, or access-sensitive.
2. Run the narrowest `nas-context` mode: `host`, `network`, `storage`, or `services` as appropriate.
3. Resolve the executable with `command -v` and known Synology paths; do not assume `/usr/syno/sbin` without checking.
4. Capture the live command's `--help` output and compare it with the bundled guide.
5. Inspect the exact target and dependencies using supported DSM commands and configuration surfaces.
6. Record current state, backup/rollback material, and verification criteria.
7. Explain material risk before mutation and obtain any required explicit authorization.
8. Execute one narrow change at a time. Capture exit status and stderr without exposing secrets.
9. Verify through an independent read path and check collateral service/access effects.
10. Report persistence, rollback, and any guide/live syntax divergence.

## Command selection

| Area | Historical CLI | Principal risk |
|---|---|---|
| Local users | `synouser` | Account deletion, password exposure, lockout |
| Local groups | `synogroup` | Membership replacement, lost access |
| Shared folders | `synoshare` | Data deletion, ACL loss, auto-restoration behavior |
| Networking | `synonet` | Immediate SSH/DSM disconnection |
| Services | `synoservice` | Service interruption or persistence change |
| Workgroup/ADS | `synowin` | Domain trust and credential exposure |

Prefer DSM GUI/API or current supported Synology tooling when it provides a safer, version-aware path. Use the historical CLI only after confirming it exists and its live help matches the intended operation.

## Mutation gates

### User or group

- Confirm the account/group is local, not directory-backed or package-owned.
- Check memberships, shared-folder permissions, application ownership, scheduled tasks, and service dependencies.
- Never delete system, administrator, guest, package, or backup principals casually.
- For membership replacement, record the complete before-list and ensure required admin access remains.

### Shared folder

- Resolve the share name and backing path; check mount/bind/package/Docker references and data size.
- Capture ACLs, encryption state, recycle-bin/snapshot/backup status, and share configuration.
- Distinguish removing share configuration from deleting its data.
- Verify the target is not a volume or shared-folder root selected by an unresolved variable.

### Network or service

- Confirm which interface and route carry the current SSH session.
- Maintain DSM console/LAN/out-of-band recovery.
- Use delayed rollback when practical.
- Verify listeners, routes, DNS, DSM access, SSH access, and dependent applications after change.

## Completion standard

State the live DSM version, actual executable/help syntax, exact scoped object, operation result, independent verification, service/access impact, persistence, backup, and rollback. Do not report success solely because the process exited zero.

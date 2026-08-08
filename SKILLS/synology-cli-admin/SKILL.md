---
name: synology-cli-admin
description: Safely inspect, diagnose, and administer Synology DSM/NAS systems from the command line. Use for Synology local users and groups, shared folders and ACLs, DSM services and packages, hostname and network settings, workgroup or Active Directory membership, Synology CLI error codes, and compatibility checks involving synouser, synogroup, synoshare, synonet, synowin, synosystemctl, synopkg, or legacy synoservice commands.
---

# Synology CLI Administrator

Operate Synology DSM conservatively. Treat the bundled 2021 CLI material as a legacy reference, not proof that a command is present or compatible with the running DSM release.

## Start safely

1. Read the nearest applicable `AGENTS.md`.
2. Run `date` before creating documentation, backups, or timestamped artifacts.
3. Run the narrowest relevant `nas-context` mode:
   - `host` for DSM/version/identity work
   - `network` for interfaces, DNS, routes, listeners, hostname, or directory services
   - `storage` for shares, paths, volumes, mounts, or permissions
   - `services` for packages, services, or processes
   - `tools` for CLI availability
   - `quick` for a substantial cross-domain task
4. For the legacy utilities, read [references/legacy-cli.md](references/legacy-cli.md). For a returned hexadecimal error, read [references/error-codes.md](references/error-codes.md).
5. Run `scripts/inspect-cli-surface.sh` when command locations or DSM compatibility are uncertain.

## Establish authority

Use current host output in this order:

1. Installed binary and its own `--help` or safe list/detail output
2. Current official Synology documentation for the installed DSM version
3. Existing DSM/application configuration
4. Bundled legacy reference

Search current official Synology documentation before version-sensitive, security-sensitive, or unfamiliar changes. Do not transplant Ubuntu/systemd advice onto DSM without verifying that it applies.

Some `/usr/syno/sbin/*` tools are executable only by root. Do not interpret a failed non-root help probe as absence. Inspect existence and mode first. Use `sudo` only when authorized and necessary; never expose passwords in command arguments, logs, or reports.

## Classify the operation

Treat listing, existence checks, metadata inspection, and help output as read-only.

Treat user/group modification, ACL changes, share creation or rename, package/service state, workgroup/domain membership, hostname, DNS, gateway, MTU, or interface changes as stateful.

Treat account/share deletion, `synoshare --del TRUE`, permission replacement with `=`, service disablement, domain departure/join, and remote network changes as destructive or lockout-prone. Obtain explicit authorization for deletion of any user data, share data, database, volume, backup, or archive.

## Use the execution loop

1. Define the exact desired state and affected objects.
2. Inspect the current state without printing secret values.
3. Resolve the actual binary path with `command -v`, `type -a`, or known `/usr/syno/{bin,sbin}` paths.
4. Capture the installed command's help or safe detail/list output. Never assume the legacy syntax.
5. Inspect dependencies:
   - users: UID, group memberships, homes, quotas, application access, scheduled tasks
   - groups: members, share ACLs, application permissions
   - shares: resolved path, volume, filesystem, mounts, encryption, snapshots, recycle bin, ACLs, Docker/package references, size
   - services/packages: dependents, listeners, restart policy, active sessions
   - network/domain: interfaces, routes, DNS, listeners, SSH path, alternate recovery access
6. Back up consequential configuration with a timestamp and preserve ownership, mode, ACLs, and extended attributes where relevant. Verify readability.
7. Prefer DSM Control Panel or supported Synology interfaces when they preserve DSM-managed state better than a private CLI.
8. Execute the narrowest possible command. Avoid opaque one-liners and force flags.
9. Check exit status and decode known Synology errors.
10. Verify the desired state end-to-end and check nearby services, access, persistence, and unintended exposure.
11. Report the change, verification, unresolved issues, and rollback path.

## Guardrails by domain

### Users and groups

- Never place a plaintext password in shell history, process arguments, saved logs, or chat output.
- Prefer an interactive or supported API/UI workflow when a legacy utility requires the password as an argument.
- Refuse empty passwords unless explicitly required and risk-accepted.
- Inspect whether an account is a system, admin, package, domain, or service identity before changing it.
- Remember that `synogroup --member` replaces the complete member list on legacy DSM; capture the existing list first.
- Verify effective access, not only database membership.

### Shared folders

- Resolve and inspect the share path before any change.
- Treat `synoshare --del TRUE` as data deletion. Never run it without explicit authorization, dependency inspection, and a recovery plan.
- Do not assume `--del FALSE` is harmless; it removes DSM configuration and may change behavior after reboot.
- Never recursively `chmod` or `chown` a shared-folder root. Preserve Synology ACLs and extended attributes.
- Account for permission precedence: No Access overrides Read/Write, which overrides Read Only.
- Do not use the legacy CLI for Hybrid Share unless current official documentation explicitly supports the operation.

### Services and packages

- Do not assume `synoservice` exists on DSM 7. Discover the supported service/package mechanism.
- Inspect with safe list/status/detail operations before start, stop, restart, enable, disable, or package mutation.
- Do not restart a service merely as a diagnostic experiment.
- Protect SSH and the current Codex session. Before touching SSH, networking, firewall, reverse proxy, or authentication, preserve an alternate recovery path.

### Network, hostname, and directory services

- Treat remote changes as lockout-prone. Capture interfaces, addresses, routes, DNS, listeners, and the active SSH path.
- Validate that a static IP, mask, gateway, DNS server, VLAN, bond, or interface name matches the current topology.
- Never assume interfaces are only `eth0` or `eth1`; DSM may use bonds, bridges, VLANs, Open vSwitch, or renamed devices.
- Prefer DSM-supported configuration paths. Do not manually edit generated network files unless no supported path exists and a verified rollback is ready.
- Never pass a domain administrator password directly on the CLI if a safer supported workflow exists.
- Verify DNS, time synchronization, domain-controller reachability, name resolution, authentication, and share access after domain changes.

## Verification minimums

For every stateful task, verify:

- the target object now has the intended state;
- the relevant service/package remains healthy;
- expected local or LAN behavior works;
- no unintended listener or public exposure appeared;
- the change survives or is configured to survive restart when required;
- the current SSH/Codex control path remains usable.

Do not claim success from exit code alone.

# Legacy compatibility and safety

## Guide-age implications

The bundled document is copyright 2021 and includes legacy products and interfaces. Treat every command as internal and version-sensitive. DSM 7 may retain, replace, wrap, or remove commands and service aliases.

Decision order:

1. Current host output and live `--help`.
2. Supported DSM UI/API and current Synology tooling.
3. Existing automation known to work on the same DSM build.
4. Bundled guide as historical syntax context.

## Secrets

`synouser` and `synowin` historical forms place passwords in argv. Prefer DSM GUI/API, stdin/file-descriptor mechanisms supported by the live tool, or a tightly controlled temporary process. Never echo, log, commit, or save real credentials in scripts. Inspect task schedulers and shell history after an authorized secret-bearing test.

## Backup and rollback

- Users/groups: record identifiers, membership, application privileges, ACL references, and home metadata.
- Shares: export/record share configuration, path, ACL/xattrs, encryption, snapshot and backup state; data backup is separate from configuration backup.
- Network: record interfaces, IP/mask, routes, DNS, gateway, MTU, bonds/VLANs, firewall, proxy, and a rollback path usable without the changed network.
- Services: record enabled and runtime state, package ownership, dependencies, and listeners.
- Domain: preserve a local administrator path and record directory/DNS/time configuration.

## Remote session protection

Before a networking, SSH, HTTPS, firewall, authentication, or domain change:

- Identify the interface and listener carrying the current session.
- Keep a second verified session when safe.
- Ensure DSM console or trusted LAN access exists.
- Stage a delayed rollback where supported.
- Do not restart the NAS as an exploratory step.

## Destructive share semantics

`synoshare --del TRUE` is a data-deletion instruction, not merely configuration cleanup. Do not run it based on the guide alone. Resolve the share, backing directory, mount state, consumers, size, backup readability, and exact authorization first.

`--del FALSE` is still stateful and can change access/exposure after restart. The historical guide says retained directories may cause shares to reappear with default privileges, so validate persistence and ACL behavior.

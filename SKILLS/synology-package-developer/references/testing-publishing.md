# Testing, review, publishing, and support

## Contents

- Static validation
- Build matrix
- Runtime matrix
- Security review
- Observability
- Publishing
- Support

## Static validation

Run:

```sh
scripts/validate_package.py PROJECT --target-dsm VERSION
scripts/inspect_spk.py PACKAGE.spk
```

Also run project-native:

- shell syntax and lint;
- JSON/INI/YAML validation;
- formatting;
- unit/integration tests;
- dependency audit;
- license/SBOM generation;
- secret scanning;
- ELF and dynamic-link inspection;
- container/Compose validation;
- reproducible-build checks.

Manually review every delete, ownership/mode change, privileged operation, network request, database migration, and lifecycle branch.

## Build matrix

Build each declared:

- DSM major/minor/build family;
- package architecture family/platform;
- native ABI variant;
- provider dependency combination.

Do not publish an architecture in INFO unless its artifact was built and tested. For `noarch`, test multiple materially different architectures when invoked runtimes/providers can vary.

## Runtime matrix

Use expendable DSM test systems or snapshots:

| Area | Minimum scenarios |
|---|---|
| Install | clean, offline if claimed, low disk, missing provider, port collision |
| Start | normal, dependency unavailable, stale PID/lock, boot |
| Stop | graceful, hung process, shutdown |
| Status | running, stopped, crashed, stale state |
| Upgrade | every supported predecessor, stopped/running states, migration failure |
| Repair | damaged/missing payload and preserved state |
| Move | supported volume-to-volume move, low space |
| Uninstall | preserve data, optional explicit purge, provider unavailable |
| Reinstall | with retained state and without retained state |
| UI | admin/user, locale, invalid input, session expiry |
| Network | bind addresses, firewall, reverse proxy, TLS, WebSocket/upload |

Verify persistence across reboot where relevant.

## Security review

Check:

- package runs as its internal user;
- files, sockets, and secrets use least permissions;
- no setuid/setgid surprise;
- capabilities are minimal;
- lifecycle arguments/environment are safely parsed;
- package cannot escape allowed paths through symlinks;
- no shell injection, command substitution, unsafe `eval`, or unquoted expansions;
- web/API authorization is server-side;
- no session/token leakage;
- no unexpected outbound connections during install;
- dependencies/images are pinned and scanned;
- no Docker socket/privileged container;
- AppArmor/security logs have no unexplained denies;
- no coredumps with secrets;
- uninstallation leaves no process/listener but preserves user data as declared.

## Observability

Use:

- `/var/log/packages/PACKAGE.log`
- `/var/log/synopkg.log`
- `/var/log/messages`
- package logs under `/var/packages/PACKAGE/var/log`
- Container Manager/container logs
- service status and Resource Monitor

Log timestamps, versions, migration stages, and actionable errors. Redact credentials, cookies, authorization headers, database DSNs, tokens, and wizard secrets.

Provide health checks that validate application function, not merely PID existence.

## Publishing

Before submission:

1. freeze and tag the exact source;
2. build from clean, recorded inputs;
3. calculate SHA-256;
4. complete the test/review matrix;
5. prepare release notes and upgrade/recovery guidance;
6. confirm metadata, support URL/email, screenshots, licenses, and privacy disclosures;
7. confirm package remains installable offline if claimed;
8. retain symbols, logs, provenance, and rollback artifacts.

Synology review themes from the supplied guide include required/nondeprecated INFO fields, lower privilege, complete lifecycle behavior, offline install, network behavior, security/antivirus scans, cleanup, port registration/conflict, clean logs, AppArmor, coredumps, and ad-hoc testing.

## Support

After publication:

- maintain a supported DSM/model/provider matrix;
- publish known issues and recovery steps;
- respond without requesting raw secret-bearing logs;
- provide a redaction guide;
- reproduce on the matching platform;
- issue upgrades with monotonically increasing versions;
- never overwrite an artifact under an existing version;
- preserve rollback compatibility or clearly document irreversible migrations;
- plan end-of-life and data export.

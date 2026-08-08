# Security, privilege, and resource workers

## Contents

- DSM 7 privilege model
- Privilege configuration
- Resource-worker model
- Common workers
- Secrets and capabilities
- Logging and notifications

## DSM 7 privilege model

DSM 7 requires explicit lower privilege. Begin with:

```json
{
  "defaults": {
    "run-as": "package"
  }
}
```

Do not use DSM 6 `run-as: system`. A package requiring root may need Synology approval/development-token handling and a strong justification. Prefer resource workers for privileged integration.

Threat-model:

- lifecycle scripts;
- network listeners;
- DSM APIs and session authentication;
- web UI and CGI;
- filesystem access;
- capabilities;
- database credentials;
- container runtime access;
- supply-chain downloads;
- upgrade data parsing.

## Privilege configuration

`conf/privilege` controls script identity and installed payload ownership/mode. Optional fields can define package username/group, control-script actions, executables, and tools.

Use the narrowest per-file declaration. Example:

```json
{
  "defaults": {
    "run-as": "package"
  },
  "tool": [
    {
      "relpath": "bin/helper",
      "user": "package",
      "group": "package",
      "permission": "0700"
    }
  ]
}
```

Rules:

- Keep relative paths under package `target`.
- Reject traversal and absolute paths.
- Do not add setuid/setgid bits.
- Assign Linux capabilities only when unavoidable and document why.
- Never grant broad capabilities such as `cap_sys_admin` as a shortcut.
- Verify resulting owner, mode, and capabilities on the installed NAS.

Package users are internal identities. They can still appear in ACL editors and some DSM UIs. Use stable package-owned identities; do not impersonate built-in users.

## Resource-worker model

`conf/resource` declares privileged integrations. A worker acquires/releases a resource at documented lifecycle timings. Failure behavior varies; account for rollback and partial release.

Before using a worker:

1. verify provider package/version;
2. verify target DSM availability;
3. understand acquisition and release timing;
4. determine whether it supports update;
5. design behavior if an existing resource collides;
6. test install, upgrade, repair, stop/start, uninstall, and provider outage.

Some updateable workers are refreshed through `synopkghelper update PACKAGE RESOURCE_ID`; confirm exact installed syntax and never guess.

## Common workers

### Data share

Creates a share or grants package access. The documented worker deliberately does not delete the share on uninstall because it may contain user data.

- Use stable share names.
- Decide whether creation is first-start-only.
- Use least-privilege RO/RW assignments.
- Never assume the share is empty or package-exclusive.
- Use the framework's `/var/packages/PACKAGE/shares` link where supported.

### `/usr/local` linker

Links selected package payload files into `/usr/local/bin`, `/usr/local/lib`, or `/usr/local/etc`.

- Ensure basenames cannot collide.
- Declare only necessary files.
- Do not use it to overwrite unrelated commands.
- Test release and rollback.

### Port config

Registers a `.sc` service definition for DSM firewall and port-forwarding UIs. It does not necessarily create or bind the listener.

- Register every destination port/protocol.
- Use correct source-port declarations only when required.
- Check actual listeners and Docker publications.
- Parse `servicetool --conf-port-conflict-check` output; its exit code does not represent conflict according to the supplied guide.

### Systemd user unit

DSM 7 can install package units. Use package user units where possible. Package-provided system units require tighter review.

- Put services in `PACKAGE.slice` so Resource Monitor can attribute them.
- Use `synosystemctl` inside package scripts where documented.
- Do not assume ordinary distribution `systemctl` behavior.
- Declare dependencies instead of referencing arbitrary system units.

### Syslog config

Use package log paths under persistent package state, e.g. `/var/packages/PACKAGE/var/log`. Provide rotation and verify that logs do not contain secrets, tokens, database passwords, session cookies, or full request bodies.

### Web, nginx, and port workers

Use the dedicated worker instead of editing generated DSM nginx/firewall files. Worker schemas and provider versions are release-sensitive; see `integrations.md`.

### Docker and Docker project

Prefer `docker-project` for DSM 7.2.1+ Container Manager when full Compose semantics are needed. See `integrations.md`.

### Database

Treat resource configuration containing admin/user passwords as highly sensitive. Prefer wizard/runtime secret handling and avoid artifact-embedded credentials. See `integrations.md`.

## Secrets and capabilities

- Never store live secrets in INFO, `conf/resource`, Compose YAML, images, package payload, Git, or logs.
- Pass sensitive wizard values only to the smallest necessary lifecycle scope.
- Write secrets with restrictive permissions into package-private persistent storage.
- Avoid command-line password arguments.
- Rotate credentials after suspected exposure.
- Scan source, staged payload, and finished SPK.
- Use checksums/signatures for downloaded artifacts and pin sources.

## Messages and notifications

Lifecycle scripts can write a concise user-facing message to `SYNOPKG_TEMP_LOGFILE`. Do not treat it as a debug dump.

For desktop/system notifications:

- define localized strings;
- register notification resources;
- use documented notification commands;
- sanitize interpolation values;
- avoid sensitive content;
- rate-limit noisy events;
- classify severity correctly.

Test notifications for administrators and ordinary users. Never use notifications as the sole error log or recovery instruction.

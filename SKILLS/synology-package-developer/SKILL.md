---
name: synology-package-developer
description: Design, scaffold, build, audit, migrate, package, test, and publish third-party Synology DSM packages and SPK files. Use for DSM 7 package framework work involving INFO or INFO.sh, package.tgz, SynoBuildConf, PkgCreate.py, pkgscripts-ng, cross-compilation, lifecycle scripts, conf/privilege, resource workers, package FHS, DSM desktop apps, Web Station, nginx, ports, notifications, Docker or Container Manager projects, databases, wizard UI files, upgrades, architecture compatibility, Package Center review, or DSM 6-to-7 migration.
---

# Synology Package Developer

Build DSM packages as production software for an appliance, not as ordinary Linux tarballs. Prefer current official Synology documentation and repositories over the bundled guide-derived notes.

## Establish the target

1. Read the nearest applicable `AGENTS.md`.
2. Run `date`.
3. Determine:
   - exact DSM release and build;
   - model, CPU architecture, Synology platform, and package architecture family;
   - required Package Center providers and minimum package versions;
   - whether the package is script-only, native, web, container-backed, or mixed;
   - supported install, upgrade, downgrade, repair, move, stop, and uninstall behavior;
   - persistent data, configuration, secrets, ports, shares, and recovery requirements.
4. Use `nas-context host`, `nas-context tools`, and the narrowest additional mode when targeting the current NAS.
5. Search current official Synology documentation, the `SynologyOpenSource/pkgscripts-ng` branch for the target DSM, `SynologyOpenSource/ExamplePackages`, and the matching official toolchain before version-sensitive implementation.

Do not install the Package Toolkit directly onto DSM. Use a dedicated 64-bit Linux build environment or an isolated container/VM. Never run foreign `apt` instructions directly on the NAS.

## Choose the workflow

- Read [references/package-format.md](references/package-format.md) for SPK layout, INFO fields, versioning, dependencies, and metadata.
- Read [references/build-toolkit.md](references/build-toolkit.md) for `pkgscripts-ng`, `EnvDeploy`, `PkgCreate.py`, cross-compilation, platforms, and reproducible builds.
- Read [references/lifecycle-fhs.md](references/lifecycle-fhs.md) for control scripts, environment variables, lifecycle order, FHS storage, upgrade migration, and uninstall safety.
- Read [references/security-resources.md](references/security-resources.md) for DSM 7 lower privilege, capabilities, resource workers, shares, ports, services, logging, and notifications.
- Read [references/integrations.md](references/integrations.md) for DSM desktop UI, localization, help, authentication, web services, nginx, wizard UI, Docker projects, and databases.
- Read [references/testing-publishing.md](references/testing-publishing.md) for validation matrices, installation tests, logs, review, publishing, and support.
- Read [references/dsm6-migration.md](references/dsm6-migration.md) only for DSM 6 support or DSM 6-to-7 migration.

## Create or inspect a project

For a new package, use:

```sh
scripts/new_package.py PACKAGE_ID OUTPUT_DIR \
  --display-name "Display Name" \
  --version 1.0.0-0001 \
  --arch noarch \
  --os-min-ver 7.2-64570
```

The generator refuses to overwrite an existing target. Review every generated field and replace the placeholder icon files before packing.

For an existing project:

1. Locate `AGENTS.md`, `INFO`/`INFO.sh`, `SynoBuildConf`, lifecycle scripts, `conf/privilege`, `conf/resource`, payload source, lockfiles, and build configuration.
2. Run `git status --short` before editing.
3. Run the offline validator:

```sh
scripts/validate_package.py PROJECT_DIR --target-dsm 7.2.2
```

Treat validation warnings as review prompts, not as proof of safety or correctness.

## Design the package

1. Keep immutable application payload in `target`.
2. Keep persistent configuration in `etc`, persistent mutable data in `var`, private package state in `home`, and disposable state in `tmp`.
3. Define `conf/privilege` with `"run-as": "package"` by default.
4. Request privileged integration through the narrowest resource worker. Do not grant root merely to make development easier.
5. Declare all package and service dependencies explicitly.
6. Register ports and check conflicts. Avoid hard-coded public bindings.
7. Design upgrades as reversible migrations with version gates and verified backups.
8. Design uninstall to preserve user data unless the user explicitly and separately elects deletion.
9. Never embed passwords, API tokens, private keys, cookies, production hostnames, or live credentials in INFO, resources, Compose files, scripts, examples, build logs, or SPKs.
10. Pin external dependencies and container images to reviewed versions or immutable digests where practical.

## Implement safely

- Make preflight scripts side-effect free.
- Quote shell variables, validate paths, use explicit targets, and make lifecycle operations idempotent.
- Never delete an unresolved or empty path.
- Distinguish install, upgrade, repair, replacement, start, stop, shutdown, and uninstall through `SYNOPKG_PKG_STATUS` and relevant old/new version variables.
- Preserve the previous working version and data schema until post-upgrade verification succeeds.
- Use database-native dumps or application-supported backups before migrations.
- Do not directly edit DSM-managed nginx, firewall, service, account, or share configuration when a supported worker exists.
- Do not mount `/var/run/docker.sock` into package containers without explicit need and a documented security model.
- Never use floating database major versions.
- Do not use proprietary DSM UI internals unless the target release and official examples support them.

## Build

1. Pin the `pkgscripts-ng` branch/commit and toolkit release.
2. Deploy the exact target DSM/platform environment.
3. Build from a clean source tree or recorded commit.
4. Generate INFO deterministically.
5. Assemble payload and metadata in fresh, validated temporary directories.
6. Run `PkgCreate.py` for the required platform set.
7. Record source commit, toolkit commit, DSM target, platform, build command, output checksums, and dependency versions.
8. Inspect the finished SPK without installing it:

```sh
scripts/inspect_spk.py RESULT.spk
```

## Test on DSM

Do not treat successful packing as successful packaging.

Test on a non-production DSM instance or explicitly designated test NAS:

1. clean install and optional wizard branches;
2. start, status, stop, restart, and boot behavior;
3. dependency startup and failure behavior;
4. ports, firewall registration, authentication, permissions, UI, localization, and logs;
5. upgrade from every supported predecessor and interrupted migration recovery;
6. repair and package move if supported;
7. uninstall with data-retention and any explicit data-removal choice;
8. reinstall after uninstall;
9. offline installation if claimed;
10. least privilege, AppArmor/security logs, coredumps, leftover processes/files, and unintended outbound connections.

Protect the current SSH/Codex session. Do not test network, authentication, firewall, reverse-proxy, or package uninstall behavior on this production-like NAS without an explicit safe test plan and rollback.

## Completion gate

Claim completion only when:

- source and staged/SPK validation pass;
- required platform builds succeed;
- install, lifecycle, upgrade, rollback, and uninstall tests match the declared support matrix;
- persistent user data survives normal uninstall unless deletion was explicitly chosen;
- no secret is embedded;
- no unexpected listener, privilege, process, file, database, container, volume, or network exposure remains;
- documentation states supported DSM/platform/provider versions and recovery steps;
- checksums and exact build provenance are recorded.

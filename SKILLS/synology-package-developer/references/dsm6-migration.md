# DSM 6 compatibility and DSM 7 migration

Read only when maintaining DSM 6 or migrating a DSM 6 package. Never blend DSM 6 and DSM 7 assumptions.

## DSM 7 breaking changes

The supplied guide identifies:

- required explicit lower privilege through `conf/privilege`;
- removal of `run-as: system`;
- required INFO fields and `os_min_ver >= 7.0-40000`;
- removal of DSM 6 package signing;
- package home moved from `target` to `home`;
- package icon changed from 72x72 to 64x64;
- FHS ownership follows privilege configuration;
- control-script logs moved to `/var/log/packages/PACKAGE.log`;
- prestart behavior during boot;
- removal of Package Center keyring/trust-level controls;
- changed `synopkg` dependency behavior.

## Migration workflow

1. Inventory DSM 6 package metadata, signing, scripts, users/groups, paths, permissions, services, web integration, ports, databases, shares, and upgrade data.
2. Create a separate DSM 7 build target/artifact.
3. Add lower-privilege configuration and replace root operations with resource workers.
4. Move mutable configuration/data out of `target`.
5. replace direct DSM configuration edits with supported workers.
6. update icon/UI/web integration for DSM 7.
7. revise dependency/service names.
8. implement a versioned migration that detects old storage/layout.
9. test upgrade on a clone/snapshot of real DSM 6-era data.
10. document rollback boundaries; data/schema changes may make DSM 6 rollback impossible.

## Signing

DSM 5.1–6.x used a GPG-based signing flow. DSM 7 deprecated/removed that build-stage mechanism. Maintain signing only in a dedicated DSM 6 pipeline. Never copy private keys into source, artifacts, logs, or a shared toolkit image.

## Compatibility rule

A DSM 6 package is not automatically compatible with DSM 7. Produce separate artifacts and support matrices. Refuse installation outside declared bounds rather than hoping lifecycle scripts cope.

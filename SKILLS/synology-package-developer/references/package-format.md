# DSM package format and metadata

Derived from the user-supplied DSM 7.2.2 guide and current official Synology documentation. Verify fields against the target release.

## Contents

- SPK layout
- INFO fundamentals
- Required fields
- Compatibility and dependencies
- UI and behavior fields
- Packaging rules

## SPK layout

A conventional DSM 7 SPK archive contains:

```text
INFO
package.tgz
scripts/
  preinst postinst preuninst postuninst preupgrade postupgrade
  start-stop-status
conf/
  privilege
  resource
WIZARD_UIFILES/       optional; DSM-version-specific
LICENSE               optional; under 1 MiB in the cited guide
PACKAGE_ICON.PNG      64x64 on DSM 7
PACKAGE_ICON_256.PNG  256x256
```

Names are case-sensitive. `package.tgz` contains the installed payload. DSM extracts it under the package `target` location and maintains `/var/packages/PACKAGE/target` as the stable indirection.

Do not confuse a source project, the staged SPK root, `package.tgz`, and the final SPK archive.

## INFO fundamentals

INFO uses shell-style `key="value"` properties. Prefer `INFO.sh` plus the toolkit's `pkg_dump_info` when building through `pkgscripts-ng`; inspect the resulting INFO as the actual artifact.

DSM 7 requires at least:

| Field | Purpose |
|---|---|
| `package` | Stable unique package identity |
| `version` | Package version and monotonically increasing build |
| `os_min_ver` | Earliest compatible DSM/OS build |
| `description` | Package Center description |
| `arch` | Supported package architecture/family |
| `maintainer` | Maintainer name |

Use `displayname` for the Package Center name. Localize display name and description with the documented `displayname_LANG` and `description_LANG` fields.

### Package identity

Keep `package` stable forever after release. Do not use `: / > < | =`. Changing identity creates a different package, user/group, FHS tree, dependencies, and upgrade lineage.

### Version

Use numeric segments separated only by `.`, `-`, or `_`, normally:

```text
MAJOR.MINOR.PATCH-BUILD
1.4.2-0007
```

Increase the build monotonically for every published artifact. Do not reuse a version for different bytes.

### OS compatibility

For DSM 7 packages, set `os_min_ver` to at least `7.0-40000`; use the actual minimum feature/build required. Set `os_max_ver` only when incompatibility is known and maintained. Do not claim DSM 6 and DSM 7 compatibility with one package.

### Architecture

- Use `noarch` only when payload and all invoked dependencies are architecture-independent.
- Use a compatible architecture family for ordinary native user-space binaries.
- Use a platform-specific value when kernel, ABI, or hardware dependencies require it.
- Do not place unrelated native architectures into one SPK and label it `noarch`.

Common families in the supplied guide include `x86_64`, `i686`, `armv7`, `armv5`, and `armv8`. The platform list changes; query the target toolkit and current official mapping.

## Compatibility and dependencies

Declare package relationships rather than probing and mutating dependencies ad hoc.

Legacy INFO relationship fields include:

- `install_dep_packages`
- `install_conflict_packages`
- `install_break_packages`
- `install_replace_packages`
- `install_dep_services`
- `start_dep_services`

Use colon-separated package dependencies and explicit version constraints. Avoid ambiguous or unnecessarily broad constraints.

DSM 7.2 supports `conf/PKG_DEPS` and `conf/PKG_CONX` with OS-version-qualified sections. These take precedence over the corresponding legacy INFO fields. Use:

- `pkg_min_ver`, `pkg_max_ver`
- `os_min_ver`, `os_max_ver`

Older `dsm_min_ver`/`dsm_max_ver` constraints are described as replaced for DSM 7.2.

Starting a package with `synopkg` on DSM 7 may start dependees. Stopping/uninstalling can affect dependers. Test the dependency graph, not only the package in isolation.

## UI and behavior fields

Review these only when required:

- `dsmuidir`, `dsmappname`, `dsmapppage`, `dsmapplaunchname`
- `adminprotocol`, `adminport`, `adminurl`, `checkport`
- `ctl_stop`, `ctl_uninstall`, `precheckstartstop`
- `silent_install`, `silent_upgrade`, `silent_uninstall`
- `auto_upgrade_from`, `offline_install`
- `support_move`, `exclude_arch`, `exclude_model`
- `install_on_cold_storage`
- `startstop_restart_services`, `instuninst_restart_services`

Avoid deprecated fields such as `startable` for modern targets. Treat `install_type="system"` as exceptional: root filesystem exhaustion can impair DSM. Prefer volume installation.

## Packaging rules

- Keep build-time tools out of the runtime payload.
- Normalize permissions and ownership intentionally.
- Store no live secrets.
- Include all required licenses for bundled third-party components.
- Keep icons at target DSM dimensions.
- Generate `extractsize` correctly if used; DSM 6+ interprets it as KiB according to the supplied guide.
- Produce deterministic inputs and record artifact checksums.
- Inspect final archives for absolute paths, traversal entries, setuid/setgid bits, world-writable files, unexpected binaries, and secrets.
- DSM 7 removed the legacy package signing stage. Do not copy DSM 6 signing instructions into a DSM 7 build.

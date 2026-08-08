# Build toolkit, cross-compilation, and reproducibility

## Contents

- Environment policy
- Toolkit layout
- Environment deployment
- Source configuration
- Build and pack stages
- Native compilation
- Reproducibility

## Environment policy

Use a dedicated 64-bit generic Linux environment with root capability for chroot creation. Pin its OS image. Do not install the toolkit directly on DSM; use a workstation, VM, CI runner, or isolated Linux container/VM hosted by the NAS.

Use official sources:

- `SynologyOpenSource/pkgscripts-ng`
- `SynologyOpenSource/ExamplePackages`
- Synology Archive toolchains and GPL sources
- target DSM developer guide

Pin commits and verify downloads/checksums when available. Inspect scripts before execution.

## Toolkit layout

Typical layout:

```text
/toolkit/
  pkgscripts-ng/
    EnvDeploy
    PkgCreate.py
  toolkit_tarballs/
  build_env/
    ds.PLATFORM-VERSION/
  source/
    PROJECT/
  result_spk/
```

Keep source in version control outside the disposable chroot too. Do not treat hard-linked chroot sources as backups.

## Environment deployment

Use the branch and environment matching the target DSM family:

```sh
git clone https://github.com/SynologyOpenSource/pkgscripts-ng
cd pkgscripts-ng
git checkout DSM7.2
./EnvDeploy -v 7.2 -p PLATFORM
```

Query rather than guess:

```sh
./EnvDeploy -v 7.2 --list
./EnvDeploy -v 7.2 --info PLATFORM
```

For offline deployment, place the exact base, development, and environment tarballs in `toolkit_tarballs` and use the documented no-download option.

Removal of a build environment can involve an active `/proc` mount. Resolve and unmount only the exact chroot mount before deleting the exact environment directory. Never generalize a guide's `rm -rf` example.

## Source configuration

Each toolkit project normally has:

```text
SynoBuildConf/
  depends
  build
  install
  install-dev  optional
  collect      optional
```

### `depends`

Use INI sections:

```ini
[BuildDependent]

[ReferenceOnly]

[default]
all="7.2.2"
```

`BuildDependent` controls build order. `ReferenceOnly` exposes another project without building it. Use `ProjDepends.py -x0 PROJECT` to inspect dependency resolution.

### `build`

The build script runs inside the target chroot. Use toolkit-provided `CC`, `CXX`, `LD`, `AR`, `NM`, `STRIP`, `RANLIB`, `CFLAGS`, `LDFLAGS`, `ConfigOpt`, `ARCH`, `SYNO_PLATFORM`, and sysroot variables.

Do not hard-code a host compiler. Do not leak host `/usr/include` or `/usr/lib` into the target build.

### `install-dev`

Use when a dependent project must install headers/libraries into the chroot sysroot for later projects. Keep this separate from runtime packaging.

### `collect`

Use an executable `SynoBuildConf/collect` only when artifact collection must differ from the default. Toolkit variables include SPK source/destination and package version; validate their values before file operations.

## Build and pack stages

`PkgCreate.py` separates:

- link/compile build stage;
- pack stage producing the SPK.

Common forms vary by branch. Inspect `PkgCreate.py --help` for the pinned checkout. The supplied guide describes:

```sh
./PkgCreate.py -v 7.2 -p PLATFORM -c PROJECT
./PkgCreate.py -i PROJECT
./PkgCreate.py -x0 -c PROJECT
```

Do not rely on case-sensitive option spelling from old documentation without checking the actual tool.

The install script should:

1. create fresh, narrow staging directories;
2. install payload under a staging root;
3. generate and validate INFO;
4. copy scripts, conf, icons, wizard files, and license;
5. call toolkit package/SPK creation helpers;
6. place results in the declared artifact directory.

Use `mktemp -d` or explicit validated build-only paths. Add traps that remove only owned temporary directories.

## Native compilation

For native code:

- identify package architecture and exact ABI/toolchain;
- use the toolkit compiler wrapper/sysroot;
- pass host/build/target correctly to Autoconf;
- use `pkg-config` from the target environment;
- strip only after preserving debug artifacts when needed;
- check ELF architecture, interpreter, required shared libraries, RPATH/RUNPATH, and symbol versions;
- avoid linking against undeclared DSM-private libraries unless target-specific support is intentional.

Kernel-dependent code requires platform-specific builds and much stricter DSM build matching.

For `noarch` packages, still verify invoked runtimes and tools exist through declared dependencies.

## Reproducibility

Record:

- source commit and dirty state;
- submodule commits;
- toolkit commit/branch;
- build environment image digest;
- DSM/toolchain version and platform;
- exact command and environment-variable names;
- dependency lockfiles;
- generated INFO;
- final SHA-256;
- build logs with secrets redacted.

Build twice in clean environments when reproducibility matters. Compare archive member lists, metadata, and hashes. Control timestamps, locale, ordering, umask, and generated identifiers where the toolchain permits.

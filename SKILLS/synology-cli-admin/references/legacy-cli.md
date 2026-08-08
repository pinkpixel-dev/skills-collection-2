# Legacy Synology administrative CLI reference

Source basis: *CLI Administrator Guide for Synology NAS*, copyright 2015–2021 Synology Inc. This is a concise compatibility reference derived from the user-supplied guide. Confirm every command against the installed DSM binary and current official documentation.

## Contents

- `synouser`
- `synogroup`
- `synoshare`
- `synonet`
- `synoservice`
- `synowin`
- Compatibility notes

## `synouser`

Legacy synopsis:

```text
synouser --help
synouser --add username passwd full_name expired email app_privilege
synouser --del username...
synouser --rename old_username new_username
synouser --modify username passwd full_name expired email
```

The guide also demonstrates `synouser --setpw username password`, although it omits that action from the synopsis. Never infer support from the example; inspect current help.

Legacy constraints:

- Username: 1–64 UTF-8 characters, case-insensitive; cannot start with `-` or space or end with space; numerous punctuation characters are forbidden.
- Password: case-sensitive, up to 127 displayable characters. The guide permits blank passwords; operational policy should normally forbid them.
- Full name: up to 64 displayable UTF-8 characters.
- `expired`: `0` for active, `1` for expired.
- Email may be empty.
- Legacy application privilege is a decimal bitmask: FTP `0x01`, File Station `0x02`, Audio Station `0x04`, Download Station `0x08`; the example implies Surveillance Station `0x10`.

Only the superuser may run the utility. Success is exit status `0`.

Security warning: password arguments can leak through shell history and process inspection.

## `synogroup`

Legacy synopsis:

```text
synogroup --help
synogroup --add groupname username...
synogroup --del groupname...
synogroup --rename old_groupname new_groupname
synogroup --member groupname username...
```

`--member` replaces the membership list. Capture the complete current membership before using it.

Legacy group names are case-insensitive, 1–15 UTF-8 characters, cannot start with `-` or space, cannot end with space, and exclude numerous punctuation characters. System groups cannot be deleted or renamed. Only the superuser may run the utility. Success is exit status `0`.

## `synoshare`

Legacy synopsis:

```text
synoshare --help
synoshare --add sharename description path users_na users_rw users_ro browsable advanced_privilege
synoshare --del TRUE|FALSE sharename...
synoshare --rename old_sharename new_sharename
synoshare --setuser sharename NA|RO|RW +|-|= user_list
```

Critical semantics:

- `--del TRUE` removes DSM configuration **and share data**.
- `--del FALSE` removes configuration but leaves the directory; the legacy guide says DSM may restore the share with default privileges after reboot.
- The guide states deletion applies only to normal shared folders, not Hybrid Share.
- `--setuser`: `+` appends, `-` removes, `=` replaces that access list.
- User lists are comma-separated; prefix groups with `@`.
- `browsable`: `1` displays the share in Windows network browsing, `0` hides it without changing access.
- Advanced privilege decimal bitmask: disable directory browsing `0x1`, modification of existing files `0x2`, downloading `0x4`.

Legacy share names are case-insensitive and 1–32 UTF-8 characters. Reserved names listed by the guide include `global`, `homes`, `home`, `printers`, `.`, `..`, `surveillance`, `usbbackup`, `usbshare`, and `esatashare`. Current DSM reserves additional or different names; verify current rules.

Creating a share can create a missing path automatically. That makes a typo stateful: validate the resolved path and target volume first.

Only the superuser may run the utility. Success is exit status `0`.

## `synonet`

Legacy synopsis:

```text
synonet --help
synonet --dhcp iface
synonet --manual iface ip mask [--dont_restart_service]
synonet --set_gateway gateway
synonet --set_dns dns
synonet --set_mtu iface MTU
synonet --set_hostname hostname [--dont_restart_service]
```

The old guide limits interfaces to `eth0` and `eth1`, IPv4 inputs, hostname length to 1–15 characters, and MTU to `1500` or round thousands from `2000` through `9000`. These limitations are historically useful but unreliable on current DSM and modern network topologies.

Network changes can terminate SSH and Codex. Inspect the current interface model and preserve recovery access before mutation.

Only the superuser may run the utility. Success is exit status `0`.

## `synoservice`

Legacy synopsis:

```text
synoservice --help
synoservice --list [running]
synoservice --enable|--disable service...
synoservice --start|--stop|--restart service...
synoservice --keyon|--keyoff service...
synoservice --detail service...
```

Legacy behavior:

- `--enable`/`--disable` persist setting and immediately start/stop.
- `--start`/`--stop`/`--restart` change current state without changing enablement.
- `--keyon`/`--keyoff` change persistent settings without interrupting the service.

The guide lists legacy service keys such as `web`, `photo`, `netbkp`, `download`, `media`, `audio`, `itunes`, `mysql`, `printer`, `surveillance`, `userhome`, `ftp`, `telnet`, `ssh`, `nfs`, `afp`, `samba`, `filestation`, and `https`.

Modern DSM may omit `synoservice` entirely and use `synosystemctl`, package tooling, or DSM-managed interfaces. Discover the installed mechanism; never substitute commands by guesswork.

## `synowin`

Legacy synopsis:

```text
synowin --help
synowin --joinWorkgroup workgroup
synowin --joinDomain short_or_full_domain username password [-d dns_ip] [-i kdc_ip] [-n netbios_name] [-f fqdn_name]
```

The printed guide contains a `--joinDomai` typo in its synopsis. Current binaries can use single-dash action names rather than the guide's double-dash spelling.

Legacy workgroup names contain 1–15 characters. A domain containing a period is treated as a full domain name; otherwise it is treated as short. Multiple KDC IPs may be comma-separated, with an optional final `,*` fallback described by the guide.

Domain credentials in process arguments are unsafe. Prefer DSM's supported directory-service UI/API. Verify DNS and time before joining.

## Compatibility notes observed on CLOUDWERX_NAS

Observation date: 2026-07-25.

- DSM reports `synowin` version 7.2.2.
- `/usr/syno/sbin/synouser`, `synogroup`, `synoshare`, and `synonet` exist but are root-executable on this host.
- `/usr/syno/sbin/synoservice` is absent.
- `/usr/syno/bin/synosystemctl` and `/usr/syno/bin/synopkg` exist.
- Current `synowin` help uses actions such as `-joinWorkgroup`, `-joinDomain`, `-getWorkgroup`, and `-setWGP`, demonstrating why installed help outranks the legacy guide.

These observations are not portable inventory. Re-run discovery on every target host.

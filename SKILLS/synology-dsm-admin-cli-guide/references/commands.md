# Documented command catalog

## Contents

- `synouser`
- `synogroup`
- `synoshare`
- `synonet`
- `synoservice`
- `synowin`
- Verification checklist

All syntax is historical guide syntax. Compare with the live command's `--help` before use.

## `synouser`

Guide synopsis:

```text
synouser --help
synouser --add username passwd full_name expired email app_privilege
synouser --del username...
synouser --rename old_username new_username
synouser --modify username passwd full_name expired email
```

The examples also show `--setpw`, despite its omission from the printed synopsis. This inconsistency is a reason to trust live help.

- `--add`: Create one local user.
- `--del`: Delete named local users; guide says system, admin, and guest cannot be deleted.
- `--rename`: Rename a non-system local account if the new name does not exist.
- `--modify`: Change local account details.
- Guide requires super-user privilege.

Historical constraints: username is case-insensitive, 1–64 UTF-8 characters, cannot begin with minus/space or end with space, and excludes many shell/punctuation characters. Password is case-sensitive and up to 127 displayable characters. `expired` is `0` or `1`. `app_privilege` is a decimal bitmask: FTP `0x01`, File Station `0x02`, Audio Station `0x04`, Download Station `0x08`; the guide example implies Surveillance Station `0x10`.

Before mutation, inspect UID, groups, homes, ACLs, owned files, tasks, package usage, and admin coverage. Never embed a real password in saved commands or reports.

## `synogroup`

Guide synopsis:

```text
synogroup --help
synogroup --add groupname username...
synogroup --del groupname...
synogroup --rename old_groupname new_groupname
synogroup --member groupname username...
```

- `--add`: Create a group and initial member list.
- `--del`: Delete groups; system groups are protected according to the guide.
- `--rename`: Rename a non-system group.
- `--member`: Replace/modify membership according to live behavior; treat it as full replacement until proven otherwise.

Historical group names are case-insensitive, 1–15 UTF-8 characters, exclude punctuation, cannot begin with minus/space, and cannot end with space. Guide requires super-user privilege.

Record complete membership before any `--member` operation. Verify retained administrators, share ACL principals, Docker/package service access, and inherited permissions afterward.

## `synoshare`

Guide synopsis:

```text
synoshare --help
synoshare --add sharename share_desc share_path user_list_na user_list_rw user_list_ro share_browsable adv_privilege
synoshare --del {TRUE|FALSE} sharename...
synoshare --rename old_sharename new_sharename
synoshare --setuser sharename {NA|RO|RW} {+|-|=} user_list
```

- `--add`: Create a normal share; the guide says a missing backing path may be created automatically.
- `--del TRUE`: Remove configuration and data. This is permanently destructive and requires explicit authorization.
- `--del FALSE`: Remove configuration but retain the directory; the guide warns DSM may restore the share with default privilege after restart if the directory remains.
- `--rename`: Rename a share if the new name is unused.
- `--setuser`: Change no-access/read-only/read-write lists using append `+`, remove `-`, or replace `=`.

User lists are comma-separated; prefix groups with `@`. `share_browsable=0` only hides discovery and does not revoke access. Advanced privilege decimal bits: disable directory browsing `0x1`, disable modifying existing files `0x2`, disable downloading `0x4`.

Historical reserved names include `global`, `homes`, `home`, `printers`, `.`, `..`, `surveillance`, `usbbackup`, `usbshare`, and `esatashare`. Live DSM may reserve more.

Before any change, inspect the share's exact backing path, mount state, ACL/xattrs, encryption, snapshots, backups, recycle bin, packages, Docker bind mounts, NFS/SMB clients, and capacity. Never infer that a share is disposable from its name.

## `synonet`

Guide synopsis:

```text
synonet --help
synonet --dhcp iface
synonet --manual iface ip mask [--dont_restart_service]
synonet --set_gateway gateway
synonet --set_dns dns
synonet --set_mtu iface MTU
synonet --set_hostname hostname [--dont_restart_service]
```

The printed option spelling contains spacing/format ambiguity; use live help. The historical guide only names `eth0` and `eth1`, which is inadequate for bonds, VLANs, virtual switches, newer naming, and DSM 7. Never use those names without live discovery.

Historical MTU values are 1500 through 9000 in 1000-step options. Modern interface/hardware/switch support must be verified end to end.

Network changes can immediately terminate Codex and SSH. Capture interface, address, route, gateway, DNS, firewall, bond/VLAN state, and DSM access first. Provide console/recovery and a tested rollback path.

## `synoservice`

Guide synopsis:

```text
synoservice --help
synoservice --list [running]
synoservice --enable|--disable service...
synoservice --start|--stop|--restart service...
synoservice --keyon|--keyoff service...
synoservice --detail service...
```

- `--list`: List services, optionally running only.
- `--enable/--disable`: Persist setting and immediately start/stop.
- `--start/--stop/--restart`: Change runtime state without persistence; start checks enabled state.
- `--keyon/--keyoff`: Persist setting without interrupting runtime.
- `--detail`: Show service details.

The guide's service aliases (`web`, `photo`, `netbkp`, `download`, `media`, `audio`, `itunes`, `mysql`, `printer`, `surveillance`, `userhome`, `ftp`, `telnet`, `ssh`, `nfs`, `afp`, `samba`, `filestation`, `https`) are legacy. DSM 7 package/service names and supported managers differ. Discover current Synology package/service tools before acting.

Never restart a service merely as a guess. Inspect dependencies, listeners, packages, logs, and recovery first. Protect SSH/HTTPS and any service carrying the active management path.

## `synowin`

Guide synopsis contains a typo (`--joinDomai`); description uses `--joinDomain`:

```text
synowin --help
synowin --joinWorkgroup workgroup
synowin --joinDomain short_or_full_domain username password [-d dns_ip] [-i kdc_ip] [-n netbios_name] [-f fqdn_name]
```

Domain join requires privileged directory credentials in the historical syntax. Do not place those credentials in history or process arguments without explicit acceptance of exposure and no safer supported method. Verify DNS, time synchronization, domain controller reachability, computer-object policy, rollback/local admin access, and directory-service impact.

Workgroup names are historically 1–15 characters with exclusions. Domain names containing a period are treated as FQDNs; others as short names. Multiple KDC IPs may be comma-separated, and the guide describes a trailing wildcard fallback.

## Verification checklist

- Exit status is zero.
- Object exists in the intended state through a separate read command or DSM UI/API.
- Required ACLs/memberships remain present.
- Relevant services are running and enabled as intended.
- Network route, DNS, DSM HTTPS, and SSH remain usable where relevant.
- Persistence survives only the specifically authorized restart/reload test.
- No unrelated users, groups, shares, interfaces, services, or domain settings changed.

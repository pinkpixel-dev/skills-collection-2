# Legacy Synology error codes

Source basis: the user-supplied 2021 Synology CLI Administrator Guide. Use this table to interpret a returned legacy hexadecimal code. Treat spelling quirks as documentation artifacts. A current command's own diagnostics and current Synology documentation outrank this table.

## Contents

- General and filesystem
- Backup and storage
- Device, update, and protocol
- System, quota, service, and identity

## General and filesystem

| Code | Symbol | Meaning |
|---|---|---|
| `0x0000` | `ERR_SUCCESS` | Success |
| `0x0100` | `ERR_NOT_ENOUGH_MEMORY` | Insufficient memory allocation |
| `0x0200` | `ERR_OUT_OF_MEMORY` | Operation ran out of memory |
| `0x0300` | `ERR_ACCESS_DENIED` | Access denied |
| `0x0400` | `ERR_LOCK_FAILED` | File lock failed |
| `0x0500` | `ERR_UNLOCK_FAILED` | File unlock failed |
| `0x0600` | `ERR_PATH_NOT_FOUND` | Path not found |
| `0x0700` | `ERR_FILE_NOT_FOUND` | File not found |
| `0x0800` | `ERR_FILE_EXISTS` | File exists |
| `0x0900` | `ERR_OPEN_FAILED` | Open failed |
| `0x0A00` | `ERR_READ_FAILED` | Read failed |
| `0x0B00` | `ERR_WRITE_FAILED` | Write failed |
| `0x0C00` | `ERR_CREATE_FAILED` | Create failed |
| `0x0D00` | `ERR_BAD_PARAMETERS` | Invalid parameters |
| `0x0E00` | `ERR_INVALID_SERVERNAME` | Invalid server name |
| `0x0F00` | `ERR_INVALID_DOMAINNAME` | Invalid domain name |
| `0x1000` | `ERR_INVALID_NETNAME` | Invalid IP address format |
| `0x1100` | `ERR_SERVER_UNREACHABLE` | Windows domain controller unreachable |
| `0x1200` | `ERR_INVALID_SHARENAME` | Invalid share name |
| `0x1300` | `ERR_SHARE_EXISTS` | Share exists |
| `0x1400` | `ERR_NO_SUCH_SHARE` | Share does not exist |
| `0x1500` | `ERR_TOO_MANY_SHARES` | Share limit exceeded |
| `0x1600` | `ERR_INVALID_GROUPNAME` | Invalid group name |
| `0x1700` | `ERR_GROUP_EXISTS` | Group exists |
| `0x1800` | `ERR_NO_SUCH_GROUP` | Group does not exist |
| `0x1900` | `ERR_TOO_MANY_GROUPS` | Group limit exceeded |
| `0x1A00` | `ERR_INVALID_USERNAME` | Invalid user name |
| `0x1B00` | `ERR_INVALID_PASSWORDNAME` | Invalid password format |
| `0x1C00` | `ERR_USER_EXISTS` | User exists |
| `0x1D00` | `ERR_NO_SUCH_USER` | User does not exist |
| `0x1E00` | `ERR_WRONG_PASSWORD` | Incorrect password |
| `0x1F00` | `ERR_TOO_MANY_USERS` | User limit exceeded |
| `0x2000` | `ERR_KEY_NOT_FOUND` | Keyword not found |
| `0x2100` | `ERR_KEY_EXISTS` | Keyword exists |
| `0x2200` | `ERR_SECTION_NOT_FOUND` | Section not found |
| `0x2300` | `ERR_SECTION_EXISTS` | Section exists |
| `0x2400` | `ERR_NOT_ENOUGH_QUOTA` | User quota insufficient |
| `0x2500` | `ERR_NOT_ENOUGH_VOLUME_SPACE` | Volume free space insufficient |
| `0x2600` | `ERR_SEEK_FAILED` | Seek failed |
| `0x2700` | `ERR_STAT_FAILED` | Stat failed |
| `0x2800` | `ERR_RENAME_FAILED` | Rename failed |
| `0x2900` | `ERR_NOT_ENOUGH_SPACE` | Filesystem free space insufficient |
| `0x2A00` | `ERR_OP_FAILURE` | Operation failed |
| `0x2B00` | `ERR_DEV_UNCONFIG` | Device not ready |
| `0x2C00` | `ERR_DEV_UNMOUNTED` | Device not mounted |
| `0x2D00` | `ERR_OP_UNREGISTERED` | Operation not allowed |
| `0x2E00` | `ERR_TIMER_EXPIRED` | Timer expired |
| `0x2F00` | `ERR_USER_BATCH_CONFLICT` | Duplicate names |
| `0x3900` | `ERR_REMOVE_FAILED` | Remove failed |
| `0x3A00` | `ERR_MOVE_FAILED` | Move failed |
| `0x3B00` | `ERR_COPY_FAILED` | Copy failed |
| `0x3C00` | `ERR_MKDIR_FAILED` | Directory creation failed |
| `0x3D00` | `ERR_MMAP_FAILED` | Memory mapping failed |
| `0x4000` | `ERR_FORMAT_ERROR` | Filesystem creation failed |

## Backup and storage

| Code | Symbol | Meaning |
|---|---|---|
| `0x5000` | `ERR_NO_BACKUP_SET` | Backup set missing |
| `0x5100` | `ERR_NO_DEST_ID` | Local backup destination ID missing |
| `0x5200` | `ERR_BACKUP_INFO_FAIL` | Backup shared-memory info unavailable |
| `0x5300` | `ERR_BAD_DEST_PATH` | Invalid local backup destination |
| `0x5400` | `ERR_RM_SHM_FAIL` | Shared-memory ID removal failed |
| `0x5500` | `ERR_EXPORT_APPLICATION` | Application export failed |
| `0x5600` | `ERR_IMPORT_APPLICATION` | Application import failed |
| `0x6000` | `ERR_NO_VOLUME_ID` | Volume ID missing |
| `0x6100` | `ERR_NO_DISK_ID` | Disk ID missing |
| `0x6200` | `ERR_NOT_ENOUGH_SD` | Insufficient disks |
| `0x6300` | `ERR_SD_SIZE_NOT_ALIGN` | Disk capacities do not align |
| `0x6400` | `ERR_DEVICE_BUSY` | Volume destruction blocked because device is busy |
| `0x6500` | `ERR_INVALID_SD` | Invalid disk |
| `0x6600` | `ERR_FORMAT_FAIL` | Disk reformat failed |
| `0x6700` | `ERR_CANNOT_REBUILD_DISK` | Disk rebuild failed |
| `0x6800` | `ERR_BROKEN_RAID_CONF` | Invalid RAID information |
| `0x6900` | `ERR_DISK_TOO_SMALL` | Disk too small |
| `0x6A00` | `ERR_CANNOT_GET_MNTINFO` | Mount information unavailable |
| `0x6B00` | `ERR_BROKEN_DISK_INFO` | Invalid disk information |
| `0x6C00` | `ERR_DISK_IO_FAILED` | Disk I/O failed |
| `0x6D00` | `ERR_BAD_DISKSECTOR` | Bad sectors found |
| `0x8200` | `ERR_VOLUME_SIZE_TOO_LARGE` | Volume exceeds size limit |
| `0x8300` | `ERR_VOLUME_NOT_FOUND` | Volume not found |
| `0x8400` | `ERR_VOLUME_READ_ONLY` | Volume is read-only |
| `0xC100` | `ERR_EXCEED_ISCSI_SIZE_IN_VOLUME` | Reserved iSCSI file exceeds volume limit |
| `0xC200` | `ERR_FS_NOT_FOUND` | Filesystem not found |
| `0xC300` | `ERR_NAME_TOO_LONG` | File name too long |

## Device, update, and protocol

| Code | Symbol | Meaning |
|---|---|---|
| `0x3000` | `ERR_READ_GEO` | Disk geometry read failed |
| `0x3100` | `ERR_USAGE` | Invalid parameter usage |
| `0x3200` | `ERR_UPDATE_OFFSET` | Illegal patch checksum offset |
| `0x3300` | `ERR_CHECKSUM` | Invalid patch checksum |
| `0x3400` | `ERR_OPEN_RAWDEVICE` | Raw device open failed |
| `0x3500` | `ERR_OPEN_OPTFILE` | Installation configuration open failed |
| `0x3600` | `ERR_READ_RAWDEVICE` | Raw device read failed |
| `0x3700` | `ERR_WRITE_RAWDEVICE` | Raw device write failed |
| `0x3800` | `ERR_BADPATCH` | Invalid patch file |
| `0x7100` | `ERR_UDPD_INVALID_HANDLE` | Invalid handle |
| `0x7200` | `ERR_UDPD_RUNNING_HANDLE` | Handle busy |
| `0x7300` | `ERR_UDPD_INVALID_EVENT` | Invalid event |
| `0x7400` | `ERR_UDPD_INVALID_PARAMETER` | Invalid parameters |
| `0x7500` | `ERR_UDPD_EXIT_ABNORMAL` | Daemon exited abnormally |
| `0x7600` | `ERR_UDPD_NOT_ENOUGH_SPACE` | Insufficient specified space |
| `0x7700` | `ERR_UDPD_TIMEOUT` | Packet receive timeout |
| `0x7800` | `ERR_UDPD_INIT_FAIL` | Handle initialization failed |
| `0x7900` | `ERR_UDPD_SEND_FAIL` | Send failed |
| `0x7A00` | `ERR_UDPD_RECV_FAIL` | Receive failed |
| `0x7B00` | `ERR_MANUTIL_PERM` | Invalid burn-in function |

## System, quota, service, and identity

| Code | Symbol | Meaning |
|---|---|---|
| `0x8000` | `ERR_UNKNOWN` | Unknown error |
| `0x8100` | `ERR_SYS_UNKNOWN` | Underlying system error not identified |
| `0x9000` | `ERR_YP_BIND` | NIS domain ypbind error |
| `0x9100` | `ERR_QUOTA_NOT_FOUND` | User quota not specified |
| `0x9200` | `ERR_QUOTA_PARAM_INVALID` | Corrupt quota file or invalid parameter/type |
| `0x9300` | `ERR_QUOTA_MOUNTING` | Remount for quota enablement failed |
| `0x9400` | `ERR_QUOTA_QUOTACHECK` | `quotacheck` failed |
| `0x9500` | `ERR_QUOTA_QUOTAON` | `quotaon` failed |
| `0x9501` | `ERR_QUOTA_QUOTAOFF` | `quotaoff` failed |
| `0x9600` | `ERR_FORK_FAIL` | Fork failed |
| `0x9700` | `ERR_RAID_ENUM_FAIL` | RAID enumeration failed |
| `0x9800` | `ERR_ENUM_FAIL` | Enumeration failed |
| `0x9900` | `ERR_INVALID_PATHNAME` | Invalid volume path |
| `0xA000` | `ERR_SERVICE_EXISTS` | Service exists |
| `0xA100` | `ERR_SERVICE_NOT_EXISTS` | Service does not exist |
| `0xA200` | `ERR_NOT_DIRECTORY` | Path is not a directory |
| `0xA300` | `ERR_DIRECTORY_NOT_EXISTS` | Directory does not exist |
| `0xA400` | `ERR_SERVICE_NOT_SET` | Service not configured |
| `0xA500` | `ERR_IS_DIRECTORY` | Path is a directory |
| `0xA600` | `ERR_PATH_CONFLICT` | Source and destination identify the same file |
| `0xA700` | `ERR_FAT_FILESIZE_TOO_LARGE` | File exceeds FAT 4 GB limit |
| `0xA800` | `ERR_FAT_FILENAME_ILLEGAL` | Illegal FAT filename character |
| `0xA900` | `ERR_USER_CANCEL` | User cancelled |
| `0xAA00` | `ERR_INTERRUPTED` | Interrupted by signal |
| `0xAB00` | `ERR_ENCKEY_VERIFY` | Incorrect share encryption key |
| `0xAC00` | `ERR_ENCKEY_LOST` | Local share encryption key copy lost |
| `0xB000` | `ERR_BDB_FILE_DEPRECATED` | BDB file deprecated |
| `0xB100` | `ERR_BDB_FILE_BAD_FORMAT` | Invalid BDB format |
| `0xB200` | `ERR_BDB_GET_FAILED` | BDB get failed |
| `0xB300` | `ERR_BDB_SET_FAILED` | BDB set failed |
| `0xB400` | `ERR_BDB_DELETE_FAILED` | BDB delete failed |
| `0xB500` | `ERR_BDB_CURSOR_FINISH` | BDB cursor finished |
| `0xB600` | `ERR_NO_SUCH_FTYPE` | Unknown file type value |
| `0xB700` | `ERR_RESERVED_GROUP` | GID below `GID_MIN` |
| `0xB800` | `ERR_RESERVED_USER` | UID below `UID_MIN` |
| `0xB900` | `ERR_LOOKUP_DOMAIN_GROUP` | `wbinfo -g` timed out |
| `0xBA00` | `ERR_LOOKUP_DOMAIN_USER` | `wbinfo -u` timed out |
| `0xBB00` | `ERR_INTERFACE_EXISTS` | Interface exists |
| `0xBC00` | `ERR_NO_SUCH_INTERFACE` | Interface does not exist |
| `0xBD00` | `ERR_TOO_MANY_INTERFACE` | Interface limit exceeded |
| `0xBE00` | `ERR_INVALID_PATH` | Invalid path |
| `0xBF00` | `ERR_SIZE_TOO_SMALL` | Capacity too small |
| `0xC000` | `ERR_NAME_EXISTS` | Name exists |

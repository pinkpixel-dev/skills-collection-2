# DSM Login WebAPI protocol

## Contents

- Discovery
- Request construction
- Response envelopes
- Authentication methods and fields
- SynoToken
- OTP and device trust
- Logout
- Secure example flow

## Discovery

Fixed entry point from the April 2023 guide:

```http
POST /webapi/entry.cgi
api=SYNO.API.Info&version=1&method=query&query=all
```

`SYNO.API.Info.query` accepts comma-separated API names or `all`. Returned API descriptors contain:

| Field | Meaning |
|---|---|
| `path` | CGI path relative to `/webapi/` |
| `minVersion` | Minimum supported version |
| `maxVersion` | Maximum supported version |
| `requestFormat` | If `JSON`, JSON-encode other parameter values |

Negotiate rather than copying example versions.

## Request construction

Every API call carries `api`, `version`, and `method`; include method-specific parameters. Authenticate with a retained cookie or `_sid`. When login returns a CSRF token, add it as `SynoToken`.

Although the guide illustrates GET URLs, production clients should POST encoded form bodies so secrets and tokens do not enter URLs. Ensure redirects do not forward credentials across origin.

For a target whose discovery descriptor says `requestFormat: JSON`, JSON-serialize parameter values rather than applying legacy comma escaping.

## Response envelopes

Successful JSON:

```json
{"success":true,"data":{}}
```

Failure:

```json
{"success":false,"error":{"code":101,"errors":[]}}
```

`errors` is optional and can contain per-object detail such as a file path. HTTP 200 does not imply `success:true`. Download-style APIs may return non-JSON content.

## `SYNO.API.Auth`

The guide documents DSM 6.0+ Auth versions 3–7 and recommends version 6.

### `login`

| Parameter | Availability | Purpose |
|---|---:|---|
| `account` | 3+ | DSM account |
| `passwd` | 3+ | Account password |
| `session` | 3+ | Optional DSM application session name |
| `format` | 3+ | `cookie` or `sid` |
| `otp_code` | 3+ | Two-factor code |
| `enable_syno_token` | 6+ | Request CSRF token; guide uses yes/no |
| `enable_device_token` | 6+ | Request trusted-device identity |
| `device_name` | 6+ | Trusted-device label |
| `device_id` | 6+ | Previously issued device ID |

Response data:

| Field | Purpose |
|---|---|
| `sid` | Authorized session ID |
| `did` | Device ID for trusted-device flow |
| `synotoken` | CSRF token sent as `SynoToken` |
| `is_portal_port` | Guide calls this irrelevant |

### `token`

Auth version 6+ can query the current SynoToken with `method=token`. The guide says JavaScript applications should query it again after a page reload rather than relying on a stale variable.

### `logout`

Call `method=logout`, using retained cookie or `_sid`. A successful response has an empty success envelope. Always clear local state in a `finally` block.

## OTP and device trust

Standard OTP login sends `otp_code`. To establish omission on later logins, the guide uses `enable_device_token=yes` and `device_name`; response `did` becomes the later `device_id` with the same `device_name`.

Security requirements:

- Obtain explicit user intent before trusting a device.
- Encrypt `did` at rest and scope it to origin/account.
- Provide server-side revocation guidance.
- Do not expose whether an account exists through differentiated UI messages.
- Rate-limit login and OTP failures.

## Secure example flow

```text
discover Auth -> negotiate version 6 if supported
POST login(account, passwd, session, format=sid, enable_syno_token=yes)
retain sid + synotoken in memory
POST harmless target API with _sid + SynoToken
POST Auth.logout with _sid + SynoToken if required
zero/clear local state
```

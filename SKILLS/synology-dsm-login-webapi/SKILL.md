---
name: synology-dsm-login-webapi
description: Build, audit, test, and troubleshoot secure authentication clients for the Synology DSM WebAPI using SYNO.API.Info and SYNO.API.Auth. Use for API discovery, version negotiation, login/logout, SID or cookie sessions, SynoToken CSRF protection, OTP and trusted-device flows, requestFormat JSON encoding, DSM WebAPI envelopes, authentication errors, session expiry, and migrating insecure DSM login examples to production-safe code.
---

# Synology DSM Login WebAPI

Implement DSM WebAPI authentication from the bundled April 19, 2023 guide while negotiating against live `SYNO.API.Info` metadata.

## Security boundary

- Use verified HTTPS. Never send DSM credentials over HTTP outside a deliberately isolated disposable lab.
- Never place account passwords, OTPs, SIDs, device IDs, SynoTokens, or cookies in URLs, command lines, logs, screenshots, commits, or exception messages.
- Use a dedicated least-privilege DSM account and a narrowly scoped session name.
- Treat `did`/`device_id` as an authentication secret because it can help omit future OTP challenges.
- Do not automate bypass of two-factor authentication unless explicitly required and secured as a long-lived device credential.
- Do not weaken DSM CSRF protection. When returned, send `SynoToken` on subsequent API requests.
- Log out in cleanup/finally paths and expire client-side material.

## Read references selectively

- Read [references/protocol.md](references/protocol.md) for discovery, request formats, envelopes, login, OTP, SynoToken, token refresh, and logout.
- Read [references/errors-and-security.md](references/errors-and-security.md) for error mapping, CSRF/session handling, secure storage, and retry policy.
- Read [references/source-notes.md](references/source-notes.md) for provenance and document scope.
- Consult [assets/DSM_Login_Web_API_Guide_enu.pdf](assets/DSM_Login_Web_API_Guide_enu.pdf) for exact version availability and official examples.
- Use [scripts/dsm_auth_client.py](scripts/dsm_auth_client.py) as a dependency-free SID/SynoToken reference client. It deliberately has no credential-bearing CLI.

## Required workflow

1. Discover requested APIs through fixed `/webapi/entry.cgi` using `SYNO.API.Info` version 1.
2. Read each API's `path`, `minVersion`, `maxVersion`, and optional `requestFormat`.
3. Select the highest version implemented by the client within the server range; the guide recommends Auth version 6 while documenting 3–7.
4. POST credentials as encoded form data to the discovered Auth path with `method=login`.
5. Request `enable_syno_token=yes` when supported and retain returned `sid`, `synotoken`, and optionally `did` only in protected memory/storage.
6. Send the session by cookie or `_sid`, and send `SynoToken` whenever returned/required.
7. Encode other parameters according to the target API's `requestFormat`; JSON-marked APIs require JSON-encoded parameter values.
8. Validate HTTP status, content type, JSON envelope, `success`, and contextual error codes.
9. Log out using the same session identity; clear all local authentication state even if logout fails.

## Version and endpoint rules

- Treat `/webapi/entry.cgi` as the fixed discovery endpoint described by this guide.
- Do not hard-code other CGI paths.
- Never assume the guide's Auth maximum version is the live maximum.
- Do not request a newer Auth version unless the client handles its fields/semantics.
- Interpret error codes in context; Auth codes 400–410 differ from other DSM APIs.

## OTP and trusted-device gate

- Pass `otp_code` only for an active user challenge.
- Use `enable_device_token=yes` with `device_name` only when the user explicitly wants a trusted device.
- Store returned `did` like a password, bind it to the correct DSM origin/account, and provide revocation/rotation instructions.
- For later omitted-OTP login, send the corresponding `device_name` and `device_id`; never silently downgrade when rejected.
- Errors 403 and 406 mean further two-factor authentication is required; prompt through a secure interaction rather than looping.

## Code-generation standard

- Separate discovery, transport, credential acquisition, session storage, CSRF handling, and API calls.
- Use POST for secrets and tokens; avoid query-string leakage.
- Configure connect/read timeouts and bounded response sizes.
- Retry discovery and harmless reads for transient failures with jitter; do not blindly replay login/OTP attempts because that can trigger lockout.
- Pin the DSM origin and prevent redirects from forwarding credentials to another host.
- Redact sensitive form fields and headers in observability tooling.
- Test against a fake server, not a production DSM account.

## Completion standard

Report the discovered Auth path/version, session mechanism, SynoToken handling, OTP/device-token behavior, logout result, and end-to-end harmless API verification. Redact all credential and token values.

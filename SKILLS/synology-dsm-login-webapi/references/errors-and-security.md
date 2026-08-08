# Errors and security

## Common WebAPI codes

| Code | Meaning |
|---:|---|
| 100 | Unknown error |
| 101 | Missing API, method, or version |
| 102 | API does not exist |
| 103 | Method does not exist |
| 104 | Version does not support function |
| 105 | Session lacks permission |
| 106 | Session timeout |
| 107 | Session interrupted by duplicate login |
| 108 | File upload failed |
| 109–111 | Network unstable or system busy |
| 112–113 | Reserved |
| 114 | Required API parameters lost |
| 115 | Upload not allowed |
| 116 | Operation not allowed on demo site |
| 117–118 | Network unstable or system busy |
| 119 | Invalid session |
| 120–149 | Reserved |
| 150 | Request source IP differs from login IP |

For 102–104, rediscover. For 106/107/119, reauthenticate at most once after confirming origin and account. For 109–111/117–118, retry only idempotent requests with bounded backoff. For 150, investigate proxy/source-address behavior rather than disabling protection.

## Auth-specific codes

| Code | Meaning |
|---:|---|
| 400 | Account missing or password incorrect |
| 401 | Account disabled |
| 402 | Permission denied |
| 403 | Two-factor code required |
| 404 | Two-factor code failed |
| 406 | Two-factor authentication enforced |
| 407 | Source IP blocked |
| 408 | Expired password cannot be changed in this flow |
| 409 | Password expired |
| 410 | Password must be changed |

Avoid account enumeration: present a generic login failure externally while preserving exact codes only in protected diagnostics. Do not repeatedly retry 400/403/404/406/407.

## Token handling

- `passwd` and `otp_code`: ephemeral secrets; never persist.
- `sid`/cookie: bearer session secret; protect from logs, browser storage leakage, and cross-origin transmission.
- `synotoken`: CSRF secret paired with the session; send on subsequent calls when present.
- `did`: long-lived trusted-device credential; encrypt at rest and support revocation.

Do not put any of these in URL query strings. Disable HTTP client debug dumps or configure field-level redaction.

## TLS and origin

Use a hostname matching a trusted DSM certificate. For a private CA, configure the trust store explicitly. Do not set `verify=False` in production examples. Reject redirects to a different scheme, host, or port before sending credentials.

## Retry and lockout

Retry discovery for transient network errors. Do not automatically replay passwords/OTP after an ambiguous response: the server may have accepted it, and repeated attempts can trigger lockout or duplicate sessions. Reconcile with a harmless authenticated call or restart the user-driven login flow.

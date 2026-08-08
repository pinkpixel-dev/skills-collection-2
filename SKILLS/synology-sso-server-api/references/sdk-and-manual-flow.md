# SDK and manual flow

## JavaScript SDK

Guide script location:

```text
https://DSM_HOST:PORT/webman/sso/synoSSO-1.0.0.js
```

Use the actual HTTPS origin and verify the live package serves the script.

### `SYNOSSO.init`

| Key | Type | Meaning |
|---|---|---|
| `oauthserver_url` | string | DSM origin running SSO Server |
| `app_id` | string | Registered application ID |
| `redirect_uri` | string | Exact registered callback URI |
| `callback` | function | Receives login status/result |
| `domain_name` | optional string | Windows AD domain for directory-service validation |
| `ldap_baseDN` | optional string | LDAP base DN for validation |

If a directory option is supplied, the guide says SSO Server validates that it matches the DSM's directory service.

### `SYNOSSO.login`

Takes no arguments and opens a popup. Callback response:

- `{status: "login", access_token: "..."}` on success.
- `{status: "not_login"}` when not signed in.
- `{status: "ERR_STRING"}` on error.

Do not render the token or raw response in the DOM. Send the token to a same-origin backend in a protected request body, then clear frontend references.

### `SYNOSSO.logout`

Call with a callback after `init`. The callback has no arguments. The guide states logout signs the user out of SSO Server but does not alter login status in other applications; validate desired product behavior to avoid surprising global logout.

## Manual authorization flow

Endpoint:

```text
/webman/sso/SSOOauth.cgi
```

Parameters:

| Parameter | Requirement |
|---|---|
| `app_id` | Registered SSO application ID |
| `redirect_uri` | Exact registered URI |
| `synossoJSSDK` | `false` for manual flow |
| `scope` | Guide supports only `user_id` |
| `state` | Optional in guide, mandatory for secure implementations |

After authentication, SSO redirects to:

```text
https://app.example/callback#access_token=...&state=...
```

Callback requirements:

1. Parse the fragment with `URLSearchParams`.
2. Require one non-empty access token and one state.
3. Compare state with constant-time semantics where practical and consume it once.
4. Replace browser history to remove the fragment.
5. Transmit token only to the same-origin backend over HTTPS.

## User-information exchange

Endpoint:

```text
/webman/sso/SSOAccessToken.cgi
```

Documented parameters: `action=exchange`, `access_token`, and `app_id`.

Success shape:

```json
{"success":true,"data":{"user_id":1024,"user_name":"john"}}
```

Failure shape:

```json
{"success":false,"error":"invalid_token"}
```

Perform exchange on the application backend. The guide illustrates query strings; if the live endpoint only supports GET, ensure token-bearing URLs are excluded from proxy/application/access logs and sent only over verified HTTPS. Prefer POST if the endpoint supports it and verify behavior against the installed version.

Validate that `success` is Boolean, `data` is an object, `user_id` has the expected scalar type, and `user_name` is a string. Map the external identity to an application account using an explicit policy; do not grant admin rights based only on a username string.

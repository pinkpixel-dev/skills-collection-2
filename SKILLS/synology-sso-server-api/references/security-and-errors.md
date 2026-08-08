# Security and errors

## Documented error strings

| Error | Meaning |
|---|---|
| `server_error` | SSO server error |
| `parameter_error` | Invalid `SYNOSSO.init` parameters |
| `invalid_app_id` | Application ID rejected |
| `invalid_redirect_uri` | Redirect URI rejected |
| `invalid_directory_service` | Client and SSO DSM directory services differ |
| `invalid_token` | Access token invalid |
| `unknown_error` | Unexpected error |

Do not reveal detailed application-registration failures to untrusted clients beyond what is needed. Preserve exact errors in protected diagnostics.

## Threat controls

### CSRF/login injection

Generate at least 32 random bytes for `state`, bind it to the initiating browser session and redirect target, expire it within minutes, compare exactly, and consume once. Reject missing, repeated, or mismatched state before processing the token.

### Token leakage

- Remove URL fragments immediately.
- Exclude callback routes from analytics/session replay.
- Apply a strict Content Security Policy and avoid third-party scripts on the callback page.
- Never place access tokens in your backend URL query string.
- Redact SSO endpoints and authorization headers/form fields in logs.
- Exchange once and create an application-owned secure session cookie.

### Redirect abuse

Register exact HTTPS redirect URIs. Do not accept caller-supplied redirect URIs or forward parameters without an allowlist. Prevent open redirects after login.

### SDK supply chain

Load the SDK only from the verified DSM SSO origin. Restrict `script-src` and do not proxy/cache it through an untrusted public service. Version/package updates can change behavior; perform end-to-end tests after upgrades.

### TLS

The guide's PHP example disables host and peer verification for testing. Never carry that into production. Configure a trusted certificate/private CA and verify hostname. Keep DSM SSO LAN/VPN/access-proxy scoped unless public exposure is explicitly designed.

## Legacy OAuth limitations

The guide identifies OAuth 2 but documents an access token delivered through the fragment. It does not document authorization codes, PKCE, standard OIDC discovery, ID tokens, refresh tokens, nonce, token introspection, revocation, audience, or scopes beyond `user_id`. Do not invent these features. If they are required, verify newer live documentation or select a modern IdP.

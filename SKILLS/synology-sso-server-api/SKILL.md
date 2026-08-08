---
name: synology-sso-server-api
description: Design, implement, audit, and troubleshoot application integrations with Synology DSM SSO Server and its OAuth-2-based JavaScript SDK or manual flow. Use for SYNOSSO.init/login/logout, app IDs, exact redirect URIs, state/CSRF validation, access-token fragments, server-side SSOAccessToken.cgi exchange, user_id/user_name retrieval, directory-service validation, SSO error strings, and modernizing insecure examples from the 2023 Synology SSO Server guide.
---

# Synology SSO Server API

Use the bundled 2023 guide as the protocol reference while applying modern OAuth and browser security controls absent from its minimal examples.

## Security boundary

- Use HTTPS for the SSO server, application, SDK script, redirects, and token exchange.
- Never copy the guide's HTTP examples or disabled certificate verification into production.
- Register and compare redirect URIs exactly. Do not allow wildcards, prefix matches, open redirects, or user-controlled redirect destinations.
- Generate a cryptographically random, single-use `state`, bind it to the initiating browser session, compare exactly, and expire it quickly.
- Access tokens arrive in the URL fragment in the documented manual flow. Remove the fragment from browser history immediately after parsing and never send tokens to logs, analytics, referrers, DOM text, query strings, or third-party scripts.
- Exchange access tokens server-side. Authenticate the browser-to-backend request and avoid sending the token in your own query string.
- Treat the bundled flow as a legacy OAuth-style implicit flow. Do not assume OIDC, PKCE, refresh tokens, ID tokens, or standard discovery endpoints; verify live capabilities.
- Do not expose SSO Server publicly without explicit design for TLS, firewall, application registration, access policy, and monitoring.

## Read references selectively

- Read [references/sdk-and-manual-flow.md](references/sdk-and-manual-flow.md) for SDK initialization, login/logout, manual authorization, fragment handling, and user exchange.
- Read [references/security-and-errors.md](references/security-and-errors.md) for threat controls, token lifecycle, directory-service options, and all documented error strings.
- Read [references/source-notes.md](references/source-notes.md) for provenance and scope.
- Consult [assets/Synology_SSO_API_Guide.pdf](assets/Synology_SSO_API_Guide.pdf) for exact official examples.
- Use [scripts/sso_flow_helpers.py](scripts/sso_flow_helpers.py) for strict authorization-URL construction, state generation, and callback-fragment validation. It performs no network calls and stores no tokens.

## Choose the flow

- Use the JavaScript SDK only when the app can safely load the SDK from the exact trusted DSM origin and the live SSO Server package supports it.
- Use manual flow when explicit control is needed over redirect construction and fragment processing.
- Consider a modern external identity provider instead when the application requires standards-based OIDC discovery, PKCE, refresh-token management, federation, or public Internet exposure.

## Required implementation workflow

1. Verify the live SSO Server package/version, DSM origin, TLS certificate, and registered application configuration.
2. Record exact `app_id` and `redirect_uri`; keep application registration changes scoped and reversible.
3. Generate and session-bind a one-time `state` before authorization.
4. Initialize the SDK before SDK methods, or construct the manual authorization URL using a real URL encoder.
5. On callback, verify origin/redirect context and `state` before accepting `access_token`.
6. Remove fragment data from history immediately.
7. Send the access token to the application's backend in a protected request body or secure channel.
8. Exchange it with the SSO server and validate HTTPS, response envelope, expected app binding, `user_id`, and `user_name` types.
9. Establish the application's own short-lived secure session; do not continue exposing the Synology access token to frontend code.
10. Log out and clear state/token material according to desired SSO behavior.

## SDK contract

- Load `/webman/sso/synoSSO-1.0.0.js` from the trusted SSO DSM origin documented by the live server.
- Call `SYNOSSO.init(...)` before `login` or `logout`.
- Configure `oauthserver_url`, `app_id`, exact `redirect_uri`, and callback.
- Optional `domain_name` or `ldap_baseDN` requests directory-service validation.
- `SYNOSSO.login()` opens the SSO dialog and returns callback status `login`, `not_login`, or an error string; successful login includes `access_token`.
- `SYNOSSO.logout(callback)` signs out the user from SSO Server according to the guide but does not affect login state in other applications.

## Manual contract

Authorization endpoint: `/webman/sso/SSOOauth.cgi` with `app_id`, `redirect_uri`, `synossoJSSDK=false`, `scope=user_id`, and `state`.

Successful redirect fragment contains `access_token` and returned `state`. User exchange endpoint: `/webman/sso/SSOAccessToken.cgi` with `action=exchange`, `access_token`, and `app_id`; successful data contains `user_id` and `user_name`.

## Completion standard

Report SSO package/version, exact origins and redirect URI (without secrets), selected flow, state validation, token containment, TLS verification, exchange validation, application-session result, logout semantics, and unresolved legacy-flow risks.

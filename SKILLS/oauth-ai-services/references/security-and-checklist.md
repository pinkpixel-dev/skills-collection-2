# Security Best Practices & Integration Checklist

## Security Rules (Non-Negotiable)

- **Always use PKCE** with S256 — protects public clients from auth code interception
- **Always use `state` parameter** — cryptographically random, verify on callback to prevent CSRF
- **HTTPS only** — all redirect URIs and token endpoints require HTTPS, no exceptions
- **Never log tokens** — not in console, not in error logs, not anywhere
- **Minimal scopes** — only request what you actually use
- **Store tokens encrypted** — server-side sessions or encrypted DB fields
- **Rotate refresh tokens** — store new refresh_token on each refresh response
- **Validate ID tokens** if using OIDC (OpenAI/Google): verify signature, audience, expiry

## Token Storage by Platform

| Platform | Server-side Web | Mobile | CLI/Desktop |
|---|---|---|---|
| Secure HTTP-only cookies | ✅ Best | ❌ N/A | ❌ N/A |
| Encrypted DB field | ✅ | ✅ | ✅ |
| OS Keychain | ❌ | ✅ (iOS/Android) | ✅ |
| Memory only | ✅ (short-lived) | ❌ | ❌ |
| localStorage/sessionStorage | ❌ Never | ❌ | ❌ |

## Token Refresh Strategy

```typescript
// Proactive refresh — don't wait for 401
async function getToken(stored: { access_token: string; refresh_token: string; expires_at: number }) {
  const BUFFER_MS = 2 * 60 * 1000; // Refresh 2 minutes before expiry
  if (Date.now() > stored.expires_at - BUFFER_MS) {
    return await refreshToken(stored.refresh_token);
  }
  return stored.access_token;
}
```

## Error Handling Guide

| HTTP Status | Meaning | Action |
|---|---|---|
| 401 Unauthorized | Token expired or invalid | Refresh token; if refresh fails, re-auth |
| 403 Forbidden | Token valid but insufficient scope | Re-auth requesting correct scopes |
| 429 Too Many Requests | Rate limited | Exponential backoff; respect `Retry-After` header |
| 400 on token endpoint | Bad request (wrong params) | Check grant_type, client_id, code_verifier |

## Comparison Table

| Attribute | OpenAI | Anthropic | Google Gemini | GitHub Copilot |
|---|---|---|---|---|
| **Auth URL** | `auth.openai.com/oauth/authorize` | `claude.ai/oauth/authorize` | `accounts.google.com/o/oauth2/v2/auth` | `github.com/login/oauth/authorize` |
| **Token URL** | `auth.openai.com/oauth/token` | `platform.claude.com/v1/oauth/token` | `oauth2.googleapis.com/token` | `github.com/login/oauth/access_token` |
| **Body Format** | JSON | JSON | Form-encoded | JSON |
| **Token Format** | JWT | Opaque | Opaque (`ya29.`) | Opaque (`gho_`) |
| **id_token** | ✅ (OIDC) | ❌ | ✅ (OIDC) | ❌ |
| **Device Flow** | ✅ | ❌ | ✅ | ✅ |
| **PKCE Required** | ✅ | ✅ | ✅ (recommended) | Optional (server apps) |
| **Scopes** | `model.request` + OIDC | `user:inference` etc | `generative-language.*` | None/minimal |
| **Token Lifetime** | ~1 hour | ~1 hour | ~1 hour | ~1 hour |
| **Billing** | Per user | Per user | Per GCP project | Per user (Copilot subscription) |
| **SDK** | None (manual) | `@anthropic-ai/sdk` | `google-auth-library`, `googleapis` | `@github/copilot-sdk` |

## Integration Checklist

### All Providers
- [ ] PKCE enabled (verifier + S256 challenge)
- [ ] State parameter generated (random) and verified on callback
- [ ] Tokens stored encrypted server-side
- [ ] Refresh flow implemented
- [ ] 401 error handling triggers refresh or re-auth
- [ ] 429 handling with exponential backoff
- [ ] HTTPS-only redirect URIs

### OpenAI Specific
- [ ] `model.request` scope included
- [ ] Token exchange uses JSON body (not form-encoded)
- [ ] ID token validated if using user identity

### Anthropic Specific
- [ ] Using `platform.claude.com` for token endpoint (not `claude.ai`)
- [ ] `user:inference` scope included for API calls
- [ ] `user:mcp_servers` scope included if building MCP integrations

### Google Gemini Specific
- [ ] OAuth app created in Google Cloud Console
- [ ] Generative Language API enabled on project
- [ ] Redirect URI added to authorized URIs
- [ ] OAuth consent screen configured
- [ ] Scope verification submitted (for external/production apps)
- [ ] `access_type=offline` in auth URL for refresh tokens
- [ ] Token exchange uses form-encoded body (not JSON)
- [ ] Billing enabled on GCP project

### GitHub Copilot Specific
- [ ] OAuth App registered in GitHub Developer Settings
- [ ] Expiring tokens enabled in OAuth App settings
- [ ] Users confirmed to have active Copilot subscriptions
- [ ] `@github/copilot-sdk` properly initialized with `githubToken`

## Known Gotchas Summary

1. **OpenAI vs Google body format**: OpenAI/Anthropic want JSON; Google wants `application/x-www-form-urlencoded`. Getting this wrong → 400 error.

2. **Anthropic endpoint domains**: Auth is `claude.ai`, tokens are `platform.claude.com`. Using wrong domain → connection error.

3. **Google refresh tokens**: Only issued on first consent with `access_type=offline`. If you don't get one, revoke access and re-auth with `prompt=consent`.

4. **OpenAI `model.request` scope**: Missing this → 401 on actual API calls even though OAuth succeeded.

5. **GitHub Copilot subscription**: Your OAuth succeeds but Copilot API fails → user doesn't have Copilot subscription. Your app can't fix this.

6. **Anthropic rate limits**: Some community workarounds (specific system prompts) unlock higher rate pools — don't rely on undocumented behavior in production.

7. **State parameter**: Verify that `state` in the callback matches what you stored. Skipping this → CSRF vulnerability.

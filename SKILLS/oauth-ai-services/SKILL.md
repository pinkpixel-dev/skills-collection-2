---
name: oauth-ai-services
description: >
  Complete reference for implementing OAuth 2.0 login flows with major AI service providers:
  OpenAI/ChatGPT, Anthropic Claude/Claude Code, Google Gemini, and GitHub Copilot.
  USE THIS SKILL whenever working on authentication, login, OAuth, tokens, or API access for
  any of these AI services — even if the user just says "how do I log in to X API", "I need to
  auth with Claude/OpenAI/Gemini/Copilot", "implement OAuth for AI service", "refresh tokens",
  "PKCE flow", "authorization code grant", "device code flow", or anything relating to
  integrating user authentication into an app that uses these AI APIs. Also trigger when
  comparing auth patterns across AI providers, troubleshooting 401/403 errors on AI APIs,
  or building MCP servers/clients that need user-scoped AI tokens.
---

# OAuth for AI Services

Four major AI providers, four different auth strategies. This skill covers endpoints, grant
types, scopes, token formats, code examples, and security best practices for each.

## Quick Provider Summary

| Provider | Auth Endpoint | Token Endpoint | Token Format | Device Flow |
|---|---|---|---|---|
| **OpenAI** | `https://auth.openai.com/oauth/authorize` | `https://auth.openai.com/oauth/token` | JWT | ✅ |
| **Anthropic** | `https://claude.ai/oauth/authorize` | `https://platform.claude.com/v1/oauth/token` | Opaque string | ❌ |
| **Google Gemini** | `https://accounts.google.com/o/oauth2/v2/auth` | `https://oauth2.googleapis.com/token` | Opaque (+ JWT id_token) | ✅ |
| **GitHub Copilot** | `https://github.com/login/oauth/authorize` | `https://github.com/login/oauth/access_token` | Opaque (`gho_` prefix) | ✅ |

All four support **Authorization Code + PKCE** and **Refresh Tokens**. All tokens expire ~1 hour.

---

## Critical Gotchas (Read First!)

- **OpenAI**: Token endpoint expects **JSON body**, NOT form-encoded. Must include `model.request` scope or you'll get 401 on API calls.
- **Anthropic**: Token endpoint at `platform.claude.com` (not `claude.ai`). Uses custom scopes, no OIDC (`openid` not used).
- **Google**: Token endpoint expects **form-encoded body** (opposite of OpenAI). Must add `access_type=offline` for refresh tokens. App needs verification for production.
- **GitHub Copilot**: No special scopes needed. Token is a standard GitHub OAuth token (`gho_` prefix) that Copilot SDK accepts directly.

---

## Per-Provider Details

See `references/` for deep-dive implementation details, full code examples, and flow diagrams.

- `references/openai.md` — OpenAI/ChatGPT/Codex OAuth
- `references/anthropic.md` — Anthropic Claude / Claude Code OAuth
- `references/google-gemini.md` — Google Gemini / generative-language OAuth
- `references/github-copilot.md` — GitHub Copilot OAuth
- `references/security-and-checklist.md` — Security best practices, integration checklist, comparison table

---

## Universal Auth Code + PKCE Flow

All four providers follow this same general pattern:

```
1. Generate code_verifier (random 43-128 char string)
2. code_challenge = BASE64URL(SHA256(code_verifier))
3. Redirect user to provider's authorize URL with:
   ?response_type=code
   &client_id=YOUR_CLIENT_ID
   &redirect_uri=YOUR_CALLBACK
   &scope=REQUIRED_SCOPES
   &code_challenge=<challenge>
   &code_challenge_method=S256
   &state=RANDOM_CSRF_TOKEN
4. User logs in + consents
5. Provider redirects to YOUR_CALLBACK?code=AUTH_CODE&state=...
6. Verify state matches
7. POST to provider's token endpoint with grant_type=authorization_code + code + code_verifier
8. Receive access_token + refresh_token
9. Use access_token as "Authorization: Bearer <token>" on API calls
10. When token expires (~1hr), POST to token endpoint with grant_type=refresh_token
```

---

## Scope Cheat Sheet

```
OpenAI:    openid profile email offline_access model.request
Anthropic: user:profile user:inference user:sessions:claude_code user:mcp_servers
Google:    https://www.googleapis.com/auth/generative-language openid email profile
Copilot:   (none required beyond default user scopes)
```

---

## TypeScript PKCE Helper (Works Everywhere)

```typescript
import { createHash, randomBytes } from 'crypto';

export function generatePKCE() {
  const verifier = randomBytes(32).toString('base64url');
  const challenge = createHash('sha256').update(verifier).digest('base64url');
  return { verifier, challenge };
}

export function buildAuthUrl(
  baseUrl: string,
  params: {
    clientId: string;
    redirectUri: string;
    scope: string;
    challenge: string;
    state: string;
    extra?: Record<string, string>;
  }
): string {
  const url = new URL(baseUrl);
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('client_id', params.clientId);
  url.searchParams.set('redirect_uri', params.redirectUri);
  url.searchParams.set('scope', params.scope);
  url.searchParams.set('code_challenge', params.challenge);
  url.searchParams.set('code_challenge_method', 'S256');
  url.searchParams.set('state', params.state);
  if (params.extra) {
    for (const [k, v] of Object.entries(params.extra)) {
      url.searchParams.set(k, v);
    }
  }
  return url.toString();
}
```

For detailed per-provider examples, token refresh flows, device code flows, and SDK usage → read the relevant `references/` file.

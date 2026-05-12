# Anthropic Claude / Claude Code OAuth

## Endpoints

| Purpose | URL |
|---|---|
| Authorization | `https://claude.ai/oauth/authorize` |
| Token | `https://platform.claude.com/v1/oauth/token` |

> ⚠️ Auth is on `claude.ai` but token exchange is on `platform.claude.com`. Don't mix these up!

## Grant Types
- **Authorization Code + PKCE** (primary flow)
- **Refresh Token**
- No device code, no implicit, no client credentials

## Scopes

```
user:profile user:inference user:sessions:claude_code user:mcp_servers
```

| Scope | Purpose |
|---|---|
| `user:profile` | Basic identity |
| `user:inference` | Make API calls (model requests) |
| `user:sessions:claude_code` | Claude Code session management |
| `user:mcp_servers` | MCP server access |

> Note: Anthropic does NOT use OIDC. No `openid` scope. Pure OAuth2 with custom scopes.

## Token Details

- **Format**: Opaque string (not JWT — don't try to decode it)
- **Lifetime**: 3600 seconds (1 hour)
- **Refresh Token**: Long-lived; CLI supports up to 1-year tokens via `setup-token`
- **No id_token** (no OIDC)

## Authorization Code Flow (TypeScript/Node)

```typescript
import { createHash, randomBytes } from 'crypto';

const CLIENT_ID = 'YOUR_ANTHROPIC_CLIENT_ID'; // From Anthropic (no public portal yet)
const REDIRECT_URI = 'https://yourapp.com/callback';

// Step 1: Build auth URL
const verifier = randomBytes(32).toString('base64url');
const challenge = createHash('sha256').update(verifier).digest('base64url');
const state = randomBytes(16).toString('hex');

const authUrl = new URL('https://claude.ai/oauth/authorize');
authUrl.searchParams.set('response_type', 'code');
authUrl.searchParams.set('client_id', CLIENT_ID);
authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
authUrl.searchParams.set('scope', 'user:profile user:inference user:sessions:claude_code user:mcp_servers');
authUrl.searchParams.set('code_challenge', challenge);
authUrl.searchParams.set('code_challenge_method', 'S256');
authUrl.searchParams.set('state', state);
// Store verifier + state in session, redirect user to authUrl.toString()

// Step 2: Exchange code (JSON body, same pattern as OpenAI)
async function exchangeCode(code: string, codeVerifier: string) {
  const res = await fetch('https://platform.claude.com/v1/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'authorization_code',
      code,
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      code_verifier: codeVerifier
    })
  });
  const data = await res.json();
  // data: { access_token, refresh_token, expires_in, scope }
  return data;
}

// Step 3: Refresh
async function refreshToken(refreshToken: string) {
  const res = await fetch('https://platform.claude.com/v1/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: CLIENT_ID
    })
  });
  return res.json();
}
```

## Using the Token

```typescript
import Anthropic from '@anthropic-ai/sdk';

// Option 1: SDK with token
const client = new Anthropic({ apiKey: accessToken });
// Or set env: CLAUDE_CODE_OAUTH_TOKEN=<access_token>

// Option 2: Raw fetch
const response = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
    'anthropic-version': '2023-06-01'
  },
  body: JSON.stringify({
    model: 'claude-opus-4-6',
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello!' }]
  })
});
```

## Notes

- Tokens are **per-user** — tied to a specific Anthropic account's billing/subscription
- No "app-level" tokens — every call bills against a user's plan
- For enterprise/team accounts: SAML/SSO is handled by Anthropic's side; your app flow is unchanged
- No public app registration portal as of May 2026; treat client ID/secret as private
- Rate limits: per-user quotas apply; a community workaround exists (specific system prompt) but don't rely on it
- Anthropic ToS likely forbids using tokens outside the official CLI/app context at scale
- `user:mcp_servers` scope is what you need for MCP-based integrations

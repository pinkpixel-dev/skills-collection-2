# GitHub Copilot OAuth

## Endpoints

| Purpose | URL |
|---|---|
| Authorization | `https://github.com/login/oauth/authorize` |
| Token | `https://github.com/login/oauth/access_token` |
| Device Code | `https://github.com/login/device/code` |

These are standard GitHub OAuth endpoints — Copilot SDK uses standard GitHub tokens.

## Grant Types
- **Authorization Code** (no PKCE required for server apps with a secret)
- **Device Code** (for CLI/headless)
- **Refresh Token** (newer GitHub behavior — token + refresh with offline_access)
- No implicit flow

## Scopes

> ⚠️ No special Copilot scopes! Just standard GitHub user scopes.

Minimal: `user:email` or no scopes. GitHub issues a `gho_` token that the Copilot SDK accepts directly. Copilot subscription is checked server-side by GitHub.

## Token Details

- **Format**: Opaque string with `gho_` prefix (OAuth App user token)
- **Lifetime**: ~1 hour (with refresh tokens enabled) or non-expiring (old behavior)
- **Refresh Token**: Supported (GitHub moved to expiring tokens + refresh)
- `ghu_` prefix = GitHub App installation token (different, also accepted by Copilot SDK)

## Authorization Code Flow (TypeScript/Node)

```typescript
const GITHUB_CLIENT_ID = 'YOUR_GITHUB_CLIENT_ID';
const GITHUB_CLIENT_SECRET = 'YOUR_GITHUB_CLIENT_SECRET';
const REDIRECT_URI = 'https://yourapp.com/callback';

// Step 1: Build auth URL (no PKCE needed for server apps)
import { randomBytes } from 'crypto';
const state = randomBytes(16).toString('hex');

const authUrl = new URL('https://github.com/login/oauth/authorize');
authUrl.searchParams.set('client_id', GITHUB_CLIENT_ID);
authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
authUrl.searchParams.set('state', state);
// scope is optional for Copilot — omit or use 'user:email'
// authUrl.searchParams.set('scope', 'user:email');

// Redirect user to authUrl.toString()

// Step 2: Exchange code
async function exchangeCode(code: string) {
  const res = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      client_secret: GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: REDIRECT_URI
    })
  });
  const data = await res.json();
  // data: { access_token: "gho_...", token_type: "bearer", scope, refresh_token? }
  return data;
}

// Step 3: Refresh token
async function refreshGitHubToken(refreshToken: string) {
  const res = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      client_secret: GITHUB_CLIENT_SECRET,
      grant_type: 'refresh_token',
      refresh_token: refreshToken
    })
  });
  const newTokens = await res.json();
  // Store newTokens.access_token and newTokens.refresh_token
  return newTokens;
}
```

## Token Lifecycle Management

```typescript
interface StoredToken {
  access_token: string;
  refresh_token?: string;
  expires_at?: number; // Unix ms timestamp
}

async function getValidToken(stored: StoredToken): Promise<string> {
  const now = Date.now();
  const isExpired = stored.expires_at && now >= stored.expires_at - 60_000; // 60s buffer
  
  if (isExpired && stored.refresh_token) {
    const newTokens = await refreshGitHubToken(stored.refresh_token);
    // Update stored tokens in your DB
    return newTokens.access_token;
  }
  return stored.access_token;
}
```

## Device Code Flow (CLI/Headless)

```typescript
// Step 1: Request codes
const deviceRes = await fetch('https://github.com/login/device/code', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    client_id: GITHUB_CLIENT_ID,
    scope: 'user:email'
  })
});
const { device_code, user_code, verification_uri, expires_in, interval } = await deviceRes.json();
// Show user: `Visit ${verification_uri} and enter: ${user_code}`

// Step 2: Poll
async function pollDeviceCode(deviceCode: string): Promise<any> {
  while (true) {
    await new Promise(r => setTimeout(r, interval * 1000));
    const res = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        client_id: GITHUB_CLIENT_ID,
        device_code: deviceCode,
        grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
      })
    });
    const data = await res.json();
    if (data.access_token) return data;
    if (data.error === 'authorization_pending') continue;
    if (data.error === 'slow_down') {
      await new Promise(r => setTimeout(r, 5000));
      continue;
    }
    throw new Error(data.error);
  }
}
```

## Using the Token with Copilot SDK

```typescript
import { CopilotClient } from '@github/copilot-sdk';

const copilotClient = new CopilotClient({
  githubToken: accessToken, // your gho_... token
  useLoggedInUser: false
});

const session = await copilotClient.createSession({
  sessionId: crypto.randomUUID(),
  model: 'gpt-4o'
});

const result = await session.sendAndWait({
  prompt: 'Explain OAuth flows'
});
console.log(result);
```

## Setup Requirements

1. Go to GitHub account Settings → Developer settings → OAuth Apps → New OAuth App
2. Enter app name, homepage URL, and callback URL
3. Save Client ID and generate Client Secret
4. Optional: Enable "Expiring user access tokens" (recommended — enables refresh tokens)

## Notes

- Copilot usage is **per-user billed** — each user MUST have an active Copilot subscription
- Your app doesn't add/remove Copilot access; it just fronts for each user's own license
- `gho_` tokens are standard GitHub OAuth App user tokens
- No special "Copilot scope" to request — subscription verified server-side by GitHub
- Rate limits are per user's Copilot plan; 429 if exceeded
- Multi-tenant/org: works with GitHub orgs/enterprises — users from orgs can authorize normally
- GitHub is phasing out non-expiring tokens; enable expiring tokens + refresh in your OAuth App settings

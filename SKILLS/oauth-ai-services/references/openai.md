# OpenAI / ChatGPT / Codex OAuth

## Endpoints

| Purpose | URL |
|---|---|
| Authorization | `https://auth.openai.com/oauth/authorize` |
| Token | `https://auth.openai.com/oauth/token` |
| Device Code | `https://auth.openai.com/oauth/device/code` |
| User Profile | `https://api.openai.com/oauth/profile` |

## Grant Types
- **Authorization Code + PKCE** (primary flow)
- **Device Code** (for headless/IoT)
- **Refresh Token** (requires `offline_access` scope)
- No implicit flow, no client credentials for public use

## Scopes

```
openid profile email offline_access model.request
```

> ⚠️ **CRITICAL**: You MUST include `model.request` or API calls will 401.  
> Optional: `api.connectors.invoke` for ChatGPT plugins/MCP integrations.

## Token Details

- **Format**: JWT (both access token and ID token)
- **Lifetime**: ~3600 seconds (1 hour)
- **Refresh Token**: Long-lived (up to ~1 year for device-auth flow)
- **ID Token**: Contains `chatgpt_account_id` and standard OIDC claims

## Authorization Code Flow (TypeScript/Node)

```typescript
import { createHash, randomBytes } from 'crypto';

const CLIENT_ID = 'app_EMoamEEZ73f0CkXaXp7hrann'; // OpenAI's known client ID
const REDIRECT_URI = 'https://yourapp.com/callback';

// Step 1: Build auth URL
const verifier = randomBytes(32).toString('base64url');
const challenge = createHash('sha256').update(verifier).digest('base64url');
const state = randomBytes(16).toString('hex');

const authUrl = new URL('https://auth.openai.com/oauth/authorize');
authUrl.searchParams.set('response_type', 'code');
authUrl.searchParams.set('client_id', CLIENT_ID);
authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
authUrl.searchParams.set('scope', 'openid profile email offline_access model.request');
authUrl.searchParams.set('code_challenge', challenge);
authUrl.searchParams.set('code_challenge_method', 'S256');
authUrl.searchParams.set('state', state);
// Store verifier + state in session, redirect user to authUrl.toString()

// Step 2: After callback with ?code=AUTH_CODE&state=...
async function exchangeCode(code: string, codeVerifier: string) {
  // NOTE: OpenAI expects JSON body, not form-encoded!
  const res = await fetch('https://auth.openai.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'authorization_code',
      code,
      redirect_uri: REDIRECT_URI,
      client_id: CLIENT_ID,
      code_verifier: codeVerifier
    })
  });
  const data = await res.json();
  // data: { access_token, refresh_token, id_token, token_type, expires_in }
  return data;
}

// Step 3: Refresh when expired
async function refreshToken(refreshToken: string) {
  const res = await fetch('https://auth.openai.com/oauth/token', {
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

## Device Code Flow

```typescript
// Step 1: Request device + user codes
const deviceRes = await fetch('https://auth.openai.com/oauth/device/code', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    client_id: CLIENT_ID,
    scope: 'openid profile email offline_access model.request'
  })
});
const { device_code, user_code, verification_url, expires_in, interval } = await deviceRes.json();

// Show user: `Go to ${verification_url} and enter code: ${user_code}`

// Step 2: Poll for token
async function pollForToken(deviceCode: string): Promise<any> {
  while (true) {
    await new Promise(r => setTimeout(r, interval * 1000));
    const res = await fetch('https://auth.openai.com/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
        device_code: deviceCode,
        client_id: CLIENT_ID
      })
    });
    const data = await res.json();
    if (data.access_token) return data;
    if (data.error === 'authorization_pending') continue;
    throw new Error(data.error);
  }
}
```

## Using the Token

```typescript
// Call Codex / ChatGPT API
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Hello!' }]
  })
});
```

## Notes

- No official public OAuth app registration portal — use the known `client_id` above
- Token exchange MUST be JSON (`Content-Type: application/json`), not form-encoded
- Enterprise SSO is separate (SAML via OpenAI's side)
- Rate limits on OAuth endpoints are unpublished but generous for normal use
- Device verification screen at: `https://auth.openai.com/codex/device`

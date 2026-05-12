# Google Gemini OAuth

## Endpoints

| Purpose | URL |
|---|---|
| Authorization | `https://accounts.google.com/o/oauth2/v2/auth` |
| Token | `https://oauth2.googleapis.com/token` |
| Device Code | `https://oauth2.googleapis.com/device/code` |
| User Info | `https://openidconnect.googleapis.com/v1/userinfo` |

## Grant Types
- **Authorization Code + PKCE**
- **Refresh Token** (requires `access_type=offline`)
- **Device Code** (for TVs/IoT/CLI)
- **Service Account / JWT** (server-to-server, no user login required)
- Implicit is deprecated

## Scopes

```
https://www.googleapis.com/auth/generative-language
https://www.googleapis.com/auth/cloud-platform
openid email profile
```

| Scope | Use |
|---|---|
| `generative-language` | Core Gemini API access |
| `generative-language.retriever` | Retrieval/RAG features |
| `generative-language.tuning` | Fine-tuning features |
| `cloud-platform` | Broad GCP access (only if needed) |

> Prefer specific `generative-language.*` scopes over `cloud-platform` when possible.

## Token Details

- **Format**: Opaque bearer string (e.g., `ya29.a0Af...`) — NOT a JWT
- **id_token**: Is a JWT (if you requested `openid`), contains user info
- **Lifetime**: ~3600 seconds (1 hour)
- **Refresh Token**: Long-lived; expires after ~6 months inactivity or revocation

## Authorization Code Flow (TypeScript/Node)

> ⚠️ **Google token exchange uses form-encoded body, not JSON!** (Opposite of OpenAI/Anthropic)

```typescript
import { createHash, randomBytes } from 'crypto';
import { OAuth2Client } from 'google-auth-library';

const CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID';
const CLIENT_SECRET = 'YOUR_GOOGLE_CLIENT_SECRET';
const REDIRECT_URI = 'https://yourapp.com/callback';

// Option A: Using google-auth-library (recommended)
const oAuth2Client = new OAuth2Client(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

const authUrl = oAuth2Client.generateAuthUrl({
  access_type: 'offline',   // Required for refresh token!
  prompt: 'consent',         // Force consent screen to get refresh token every time
  scope: [
    'https://www.googleapis.com/auth/generative-language',
    'openid', 'email', 'profile'
  ]
});
// Redirect user to authUrl

// After callback:
async function exchangeCode(code: string) {
  const { tokens } = await oAuth2Client.getToken(code);
  oAuth2Client.setCredentials(tokens);
  // tokens: { access_token, refresh_token, expiry_date, id_token }
  return tokens;
}

// Refresh is automatic when using setCredentials + making API calls


// Option B: Raw fetch (form-encoded!)
async function exchangeCodeRaw(code: string) {
  const params = new URLSearchParams({
    code,
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    redirect_uri: REDIRECT_URI,
    grant_type: 'authorization_code'
  });
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });
  return res.json();
}

// Refresh token (raw)
async function refreshTokenRaw(refreshToken: string) {
  const params = new URLSearchParams({
    refresh_token: refreshToken,
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    grant_type: 'refresh_token'
  });
  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });
  return res.json();
}
```

## Device Code Flow

```typescript
// Step 1: Request codes
const deviceRes = await fetch('https://oauth2.googleapis.com/device/code', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    client_id: CLIENT_ID,
    scope: 'https://www.googleapis.com/auth/generative-language'
  }).toString()
});
const { device_code, user_code, verification_url, expires_in, interval } = await deviceRes.json();
// Show user: `Visit ${verification_url} and enter: ${user_code}`

// Step 2: Poll
async function pollDeviceCode(deviceCode: string): Promise<any> {
  while (true) {
    await new Promise(r => setTimeout(r, interval * 1000));
    const res = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        device_code: deviceCode,
        grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
      }).toString()
    });
    const data = await res.json();
    if (data.access_token) return data;
    if (data.error === 'authorization_pending') continue;
    if (data.error === 'slow_down') {
      await new Promise(r => setTimeout(r, 5000)); // Back off extra
      continue;
    }
    throw new Error(data.error);
  }
}
```

## Service Account Flow (Server-to-Server, No User Consent)

```typescript
import { GoogleAuth } from 'google-auth-library';

const auth = new GoogleAuth({
  keyFile: 'path/to/service-account-key.json',
  scopes: ['https://www.googleapis.com/auth/generative-language']
});
const client = await auth.getClient();
const token = await client.getAccessToken();
// Use token.token as Bearer
```

## Using the Token with Gemini

```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

// With API key (simplest for development):
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

// With OAuth token (for user-scoped access):
const response = await fetch(
  'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contents: [{ parts: [{ text: 'Hello!' }] }]
    })
  }
);
```

## Python SDK Example

```python
from google_auth_oauthlib.flow import InstalledAppFlow
import google.generativeai as genai

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['https://www.googleapis.com/auth/generative-language']
)
creds = flow.run_local_server(port=0)
# Use creds.token as Bearer, or configure genai with it
```

## Setup Requirements

1. Enable "Generative Language API" in Google Cloud Console
2. Create OAuth 2.0 credentials (Web Application type for redirect flow)
3. Add your redirect URI to "Authorized redirect URIs"
4. Configure OAuth consent screen with app name, privacy URL
5. Add required scopes and submit for verification (for external/production apps)

## Notes

- Billing is **per Google Cloud project** (not per user like OpenAI/Anthropic/Copilot)
- Rate limits are per model per project (RPM/TPM — check Gemini rate limits page)
- `access_type=offline` required at auth time to receive refresh token
- The `googleapis` and `google-auth-library` npm packages handle refresh automatically
- API tokens are `ya29.xxx` opaque strings; id_token is JWT if openid scope requested

# BYOP — Bring Your Own Pollen

Let your users authorize your app to spend their own Pollen. Your app never pays — users
control their own balance, budgets, and revocation.

**Your App Key (`pk_`)** identifies your app on the consent screen and attributes traffic to your account.

---

## App Key Setup

Create at [enter.pollinations.ai](https://enter.pollinations.ai) → **Create New App Key**

Required fields:
- **Name** — shown on the consent screen
- **Redirect URIs** — exact callback URL(s) for web apps
- **Earnings** — opt-in, charges users 25% over base rate, credits you 25%

```bash
# Create via API
curl -X POST https://gen.pollinations.ai/account/keys \
  -H 'Authorization: Bearer sk_yoursecretkey' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "my-app",
    "type": "publishable",
    "redirectUris": ["https://myapp.com/callback"],
    "earningsEnabled": true
  }'
```

---

## Web Apps — Redirect Flow

### Step 1: Build the Auth URL

```
https://enter.pollinations.ai/authorize?redirect_uri=https://myapp.com&client_id=pk_yourkey
```

| Param | Description | Example |
|-------|-------------|---------|
| `client_id` | Your `pk_` key — shows app name on consent screen | `pk_abc123` |
| `redirect_uri` | Where user returns after auth | `https://myapp.com/callback` |
| `state` | CSRF protection — echoed back on redirect | `random-string` |
| `scope` | Account access (space/comma separated) | `usage keys` |
| `models` | Restrict to specific models | `flux,openai,gptimage` |
| `budget` | Pollen cap (default: 5; user can clear for unlimited) | `10` |
| `expiry` | Key lifetime in days (default: 7) | `30` |

Legacy aliases still accepted: `app_key`, `redirect_url`, `permissions`

### Step 2: Handle the Redirect

User returns to:
```
https://myapp.com/callback#api_key=sk_abc123xyz&state=yourstate
```

Key is in the URL **fragment** (never hits server logs). On denial: `#error=access_denied&state=...`

### Full TypeScript Example

```typescript
// Step 1: Send user to auth
function initiateAuth() {
  const params = new URLSearchParams({
    redirect_uri: window.location.href,
    client_id: 'pk_yourkey',
    budget: '20',
    expiry: '30',
    state: crypto.randomUUID(),
  });
  window.location.href = `https://enter.pollinations.ai/authorize?${params}`;
}

// Step 2: Grab key from URL fragment after redirect
function handleCallback(): string | null {
  const hash = new URLSearchParams(window.location.hash.slice(1));
  const apiKey = hash.get('api_key');
  const error = hash.get('error');
  
  if (error) {
    console.error('Auth denied:', error);
    return null;
  }
  
  if (apiKey) {
    localStorage.setItem('pollinations_key', apiKey);
    // Clear fragment from URL
    window.history.replaceState({}, '', window.location.pathname);
  }
  return apiKey;
}

// Step 3: Use their pollen
async function generate(prompt: string, apiKey: string) {
  const res = await fetch('https://gen.pollinations.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'openai',
      messages: [{ role: 'user', content: prompt }],
    }),
  });
  return res.json();
}
```

---

## CLIs & Headless Apps — Device Flow

For bots, CLIs, MCP servers, IoT, VS Code extensions — anything without a browser.

```
User sees a short code → opens browser separately → approves → your app gets the key
```

### Step 1: Request Device Code

```bash
curl -X POST https://enter.pollinations.ai/api/device/code \
  -H 'Content-Type: application/json' \
  -d '{"client_id": "pk_yourkey", "scope": "generate"}'
```

Response:
```json
{
  "device_code": "...",
  "user_code": "ABCD-1234",
  "verification_uri": "/device"
}
```

### Step 2: Show User the Code

Tell the user: *"Go to enter.pollinations.ai/device and enter ABCD-1234"*

### Step 3: Poll for the Key (every 5s)

```bash
curl -X POST https://enter.pollinations.ai/api/device/token \
  -H 'Content-Type: application/json' \
  -d '{"device_code": "..."}'
```

Responses:
- Pending: `{ "error": "authorization_pending" }`
- Done: `{ "access_token": "sk_...", "token_type": "bearer", "scope": "generate" }`

### Step 4: (Optional) Identify the User

```bash
curl https://enter.pollinations.ai/api/device/userinfo \
  -H 'Authorization: Bearer sk_...'
# → { "sub": "user-id", "name": "Thomas", "preferred_username": "...", "email": "...", "picture": "..." }
```

Standard OIDC userinfo shape.

### TypeScript Device Flow Example

```typescript
interface DeviceCodeResponse {
  device_code: string;
  user_code: string;
  verification_uri: string;
}

async function deviceFlowAuth(clientId: string): Promise<string> {
  // Step 1: Get device code
  const codeRes = await fetch('https://enter.pollinations.ai/api/device/code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ client_id: clientId, scope: 'generate' }),
  });
  const { device_code, user_code }: DeviceCodeResponse = await codeRes.json();

  console.log(`Go to https://enter.pollinations.ai/device and enter: ${user_code}`);

  // Step 2: Poll every 5s
  while (true) {
    await new Promise(r => setTimeout(r, 5000));
    
    const tokenRes = await fetch('https://enter.pollinations.ai/api/device/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_code }),
    });
    const data = await tokenRes.json();

    if (data.access_token) {
      console.log('Authorized!');
      return data.access_token;
    }
    if (data.error !== 'authorization_pending') {
      throw new Error(`Auth failed: ${data.error}`);
    }
  }
}
```

---

## Developer Earnings

When enabled on your App Key, users pay 25% above base rates — that markup credits your balance.

```
Base cost: 1.00 pollen  →  User pays: 1.25  →  You receive: 0.25
```

Credits land in the same balance type the user paid from (tier or paid).

---

## Notes

- User-authorized keys expire after 7 days by default
- Users can revoke anytime from their dashboard
- Keys are scoped — if you restrict models, those restrictions are enforced

---
name: pollinations-api
description: >
  Complete reference for building apps with the Pollinations API — a multi-modal AI generation
  platform supporting text, image, video, audio, and embeddings. Use this skill whenever working
  with Pollinations, gen.pollinations.ai, pollinations.ai, or any of their models. ALWAYS trigger
  on: text generation with Pollinations models, image generation via URL or API, video generation,
  TTS/audio generation, embeddings, BYOP (Bring Your Own Pollen) OAuth flows, MCP server setup,
  CLI usage, account/balance/usage APIs, or safety filtering. Also trigger when the user mentions
  "pollen", "flux model", "pollinations image", "polli CLI", device flow for Pollinations, or wants
  to integrate Pollinations into any TypeScript/Node/Python/React app. If the user wants to generate
  any media with AI without paying OpenAI directly, this is a strong candidate — check this skill.
---

# Pollinations API

**Base URL:** `https://gen.pollinations.ai`  
**Media Storage:** `https://media.pollinations.ai`  
**Dashboard / Keys:** `https://enter.pollinations.ai`  
**Full API Docs:** `https://gen.pollinations.ai/docs`

Pollinations is a multi-modal AI generation API — OpenAI-compatible, covering text, image, video,
audio, and embeddings. One base URL, many modalities.

---

## Quick Start (No Code)

```
# Image via URL — zero code, zero auth
https://gen.pollinations.ai/image/a%20cat%20in%20space?model=flux

# Text via URL
https://gen.pollinations.ai/text/explain%20quantum%20tunneling

# Audio via URL (auth required)
curl "https://gen.pollinations.ai/audio/Hello%20world?voice=nova" \
  -H "Authorization: Bearer YOUR_API_KEY" -o speech.mp3
```

---

## Authentication

Get a key at [enter.pollinations.ai](https://enter.pollinations.ai).

| Key type | Prefix | Use case | Rate limits |
|----------|--------|----------|-------------|
| Secret | `sk_` | Server-side / backend | None |
| Publishable | `pk_` | Client-side / frontend (beta) | 1 pollen/IP/hour |

Two auth methods:
```
Authorization: Bearer YOUR_API_KEY    # header
?key=YOUR_API_KEY                     # query param
```

> ⚠️ Never expose `sk_` keys in frontend/client-side code. Use `pk_` there.

---

## Modalities Overview

| Modality | Simple GET | POST (OpenAI-compat) |
|----------|-----------|----------------------|
| Text | `GET /text/{prompt}` | `POST /v1/chat/completions` |
| Image | `GET /image/{prompt}` | — |
| Video | `GET /video/{prompt}` | — |
| Audio (TTS) | `GET /audio/{text}` | `POST /v1/audio/speech` |
| Audio (STT) | — | `POST /v1/audio/transcriptions` |
| Embeddings | — | `POST /v1/embeddings` |

---

## Text Generation

Fully OpenAI-compatible. Swap the base URL in any OpenAI SDK.

```typescript
// TypeScript / Node.js
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://gen.pollinations.ai",
  apiKey: process.env.POLLINATIONS_API_KEY,
});

const response = await client.chat.completions.create({
  model: "openai",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(response.choices[0].message.content);
```

### Key Text Models
See `references/models.md` for the full list. Highlights:
- `openai`, `openai-fast`, `openai-large` — GPT wrappers
- `claude-fast`, `claude`, `claude-large`, `claude-opus-4.7` — Claude wrappers
- `gemini`, `gemini-3.5-flash`, `gemini-large` — Gemini wrappers  
- `deepseek`, `deepseek-pro` — DeepSeek
- `grok`, `grok-large`, `grok-4.3` — Grok
- `gemini-search`, `gemini-search-fast` — web-grounded answers
- `perplexity-fast`, `perplexity-reasoning` — Perplexity
- `qwen-coder`, `qwen-coder-large` — coding-focused
- `llama`, `llama-maverick`, `llama-scout` — Llama variants

---

## Image Generation

```
GET /image/{prompt}?model=flux&width=1024&height=1024&seed=42
```

Returns JPEG or PNG.

```typescript
const imageUrl = `https://gen.pollinations.ai/image/${encodeURIComponent(prompt)}?model=flux&width=1024`;
```

### Key Image Models
- `flux` — general purpose, high quality
- `kontext` — context-aware
- `gptimage`, `gptimage-large`, `gpt-image-2` — GPT image models
- `seedream`, `seedream-pro`, `seedream5` — Seedream variants
- `nanobanana`, `nanobanana-2`, `nanobanana-pro`
- `grok-imagine`, `grok-imagine-pro`
- `wan-image`, `wan-image-pro`
- `p-image`, `p-image-edit` — editing support

Image params: `model`, `width`, `height`, `seed`, `enhance`, `negative_prompt`, `quality`, `image` (for img2img), `transparent`

---

## Video Generation

```
GET /video/{prompt}?model=veo&duration=4
```

Returns MP4.

### Video Models
- `veo`, `seedance-pro`, `seedance-2.0`
- `wan`, `wan-fast`, `wan-pro`
- `grok-video-pro`
- `ltx-2`, `p-video`, `nova-reel`

Video params: `model`, `duration`, `aspectRatio`, `audio`

---

## Audio Generation (TTS)

```bash
# Simple GET
GET /audio/{text}?voice=nova&model=elevenlabs

# OpenAI-compatible POST
POST /v1/audio/speech
{ "model": "elevenlabs", "input": "Hello world", "voice": "nova" }

# Transcription
POST /v1/audio/transcriptions
```

### Audio Models
`elevenlabs`, `elevenflash`, `elevenmusic`, `whisper`, `scribe`, `universal-2`, `universal-3-pro`, `acestep`, `qwen-tts`, `qwen-tts-instruct`

### Available Voices
`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`, `ash`, `ballad`, `coral`, `sage`, `verse`, `rachel`, `domi`, `bella`, `elli`, `charlotte`, `dorothy`, `sarah`, `emily`, `lily`, `matilda`, `adam`, `antoni`, `arnold`, `josh`, `sam`, `daniel`, `charlie`, `james`, `fin`, `callum`, `liam`, `george`, `brian`, `bill`

---

## Embeddings

```typescript
const response = await fetch("https://gen.pollinations.ai/v1/embeddings", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "openai-3-small",
    input: "Hello world",
    dimensions: 512,
  }),
});
```

### Embedding Models & Dimensions
| Model | Max Dimensions | Modalities |
|-------|---------------|------------|
| `openai-3-small` | 1536 | text |
| `openai-3-large` | 3072 | text |
| `gemini-2` | 3072 | text, image, audio, video |
| `cohere-embed-v4` | — | text |
| `qwen3-embedding-8b` | 4096 | text |

String batch input supports up to 32 items. `task_type` is Gemini-only.

---

## Model Discovery Endpoints

No auth required for these:

```
GET /models              # all models, full metadata
GET /v1/models           # OpenAI-compatible format
GET /text/models         # text models with context window + tool support
GET /image/models        # image/video models
GET /audio/models        # audio models with voices
GET /embeddings/models   # embedding models with modalities
```

---

## Media Storage

Upload and retrieve files by content hash:

```bash
# Upload
curl -X POST "https://media.pollinations.ai/upload" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file=@image.png
# → { "url": "https://media.pollinations.ai/{hash}" }

# Retrieve (public, no auth)
GET https://media.pollinations.ai/{hash}
GET https://media.pollinations.ai/{hash}/metadata
```

---

## Account API

All require auth (`/account` base path):

```
GET /account/profile    # username, tier, nextResetAt
GET /account/balance    # pollen balance
GET /account/usage      # per-request history
GET /account/usage/daily # daily aggregated
GET /account/key        # key validity, type, permissions
```

---

## Safety Filtering

Optional. Apply via query param, body field, or header:

```bash
?safe=privacy          # redact PII
?safe=secrets          # redact keys/passwords
?safe=sexual           # block sexual content (returns 400)
?safe=violence         # block violent content
?safe=shield           # block all harmful content
?safe=true             # = privacy,secrets
?safe=nsfw             # = sexual,violence

# Via header
-H "Pollinations-Safe: privacy"
```

Blocked → `400` with `error.type: "safety_error"`.  
Response headers: `X-Safety-Applied`, `X-Safety-Redacted`, `X-Safety-Status`

---

## Error Responses

```json
{
  "status": 400,
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Description of what went wrong"
  }
}
```

| Status | Meaning |
|--------|---------|
| 400 | Invalid params / malformed request |
| 401 | Missing or invalid API key |
| 402 | Insufficient pollen balance |
| 403 | Key lacks required permission |
| 500 | Internal server error |

---

## Reference Files

For deep-dive details, see:
- `references/models.md` — Full model lists for all modalities
- `references/byop.md` — BYOP OAuth flows (web redirect + device flow)
- `references/mcp-server.md` — MCP server setup and all available tools
- `references/cli.md` — `polli` CLI commands and agent-friendly usage

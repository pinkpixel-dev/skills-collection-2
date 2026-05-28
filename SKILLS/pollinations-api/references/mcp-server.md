# Pollinations MCP Server

The official Pollinations MCP server lets MCP-capable hosts (Claude Desktop, Cursor, Windsurf, etc.)
generate images, videos, text, and audio — plus check balance and usage.

Package: `@pollinations_ai/mcp`  
All requests go to `https://gen.pollinations.ai`.  
Models, voices, and pricing are read **live** from the registry — no hardcoded enums.

---

## Installation & Auth

```bash
# Run directly (no install)
npx @pollinations_ai/mcp

# Or install globally
npm install -g @pollinations_ai/mcp
pollinations-mcp
```

Get your API key at [enter.pollinations.ai](https://enter.pollinations.ai).

```bash
export POLLINATIONS_API_KEY=sk_your_key_here
npx @pollinations_ai/mcp
```

Or use the `setApiKey` tool at runtime.

---

## Claude Desktop Integration

```bash
npx @pollinations_ai/mcp install-claude-mcp
```

Or manually add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "pollinations": {
      "command": "npx",
      "args": ["@pollinations_ai/mcp"],
      "env": {
        "POLLINATIONS_API_KEY": "sk_your_key_here"
      }
    }
  }
}
```

---

## Available Tools

### Image & Video

| Tool | Description |
|------|-------------|
| `generateImageUrl` | Generate a shareable image URL from a text prompt |
| `generateImage` | Generate an image, returns base64 data |
| `generateImageBatch` | Generate multiple images in parallel (best with `sk_` keys) |
| `generateVideo` | Generate a video, returns base64 data |
| `generateVideoUrl` | Generate a shareable video URL from a text prompt |
| `describeImage` | Vision analysis of an image URL |
| `analyzeVideo` | Analyze YouTube videos or video URLs |
| `listImageModels` | List available image & video models (live) |

Common image params: `prompt`, `model`, `width`, `height`, `seed`, `enhance`, `negative_prompt`, `quality`, `image` (img2img), `transparent`  
Common video params: `model`, `duration`, `aspectRatio`, `audio`

### Text

| Tool | Description |
|------|-------------|
| `generateText` | Simple text generation from a prompt |
| `chatCompletion` | OpenAI-compatible chat completions + tool calling |
| `webSearch` | Web-grounded answers (perplexity, gemini-search) |
| `listTextModels` | List available text models (live) |
| `getPricing` | Per-model pricing for text / image / audio |

### Audio

| Tool | Description |
|------|-------------|
| `respondAudio` | AI responds to a prompt with speech |
| `sayText` | Text-to-speech (verbatim) |
| `transcribeAudio` | Transcribe audio (uses gemini-large) |
| `listAudioVoices` | List available voices (live) |

Output formats: `mp3`, `wav`, `flac`, `opus`, `pcm16`

### Auth Tools

| Tool | Description |
|------|-------------|
| `setApiKey` | Set API key for this session |
| `getKeyInfo` | Check stored key type/prefix (local) |
| `clearApiKey` | Remove stored key |

### Account

| Tool | Description |
|------|-------------|
| `getBalance` | Remaining Pollen (requires `account:usage` permission) |
| `getUsage` | Per-request history; pass `daily: true` for daily aggregate |

---

## System Requirements

- Node.js 18.0.0 or higher

---

## Key Types in MCP Context

- `pk_` (publishable) — client-safe, rate-limited (1 pollen/IP/hour)
- `sk_` (secret) — server-side only, no rate limits, full spend capability

Use `sk_` keys when running the MCP server server-side.

---

## Testing

```bash
POLLINATIONS_API_KEY=sk_… npm run test
```

Spawns the server over stdio, lists tools, and exercises auth, text, image URL, and balance.
Skips authenticated calls when env var is unset.

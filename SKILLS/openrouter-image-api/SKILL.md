---
name: openrouter-image-api
description: >
  Complete reference for generating images with OpenRouter's dedicated Image API. ALWAYS use
  this skill when the user mentions: "openrouter image", "openrouter image generation",
  "generate images with openrouter", "openrouter /api/v1/images", "image models on openrouter",
  "openrouter flux", "openrouter dalle", "openrouter gpt-image", "openrouter stable diffusion",
  "openrouter seedream", "openrouter recraft", "text-to-image via openrouter", or any request
  to list, discover, or use image-generating models through OpenRouter. Also trigger when the
  user asks about image-to-image (img2img) via OpenRouter, streaming image generation, aspect
  ratio or resolution options, or provider-specific image params on OpenRouter. If they're
  building an app that generates images and OpenRouter is in the mix at all — use this skill.
---

# OpenRouter Image Generation API

OpenRouter provides a **dedicated Image API** at `/api/v1/images` (separate from the chat
completions endpoint) for text-to-image and image-to-image generation.

Base URL: `https://openrouter.ai`
Image endpoint: `POST /api/v1/images`
Image models list: `GET /api/v1/images/models`

---

## Quick Start

```typescript
const response = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "black-forest-labs/flux-1.1-pro",
    prompt: "a red panda astronaut floating in space, studio lighting",
  }),
});

const result = await response.json();
// result.data[0].b64_json — base64-encoded PNG image
```

Response images are returned as **base64-encoded bytes** in `data[0].b64_json`.

---

## Model Discovery

### Dedicated Image Models Endpoint (preferred)
```bash
GET https://openrouter.ai/api/v1/images/models
```
Returns all image-capable models with full capability descriptors, per-endpoint pricing, and
supported parameters. **Always use this to check what a model supports before using it.**

### General Models API (filtered)
```bash
GET https://openrouter.ai/api/v1/models?output_modalities=image
```

### Per-Endpoint Details
```bash
GET https://openrouter.ai/api/v1/images/models/{model-id}/endpoints
```
Returns provider-by-provider breakdown with definitive supported params, pricing, and
passthrough options. Use this when you need to know exact cost or provider-specific params.

→ See `references/models.md` for the current model list with capabilities and pricing.

---

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | ✅ | Model slug (e.g. `black-forest-labs/flux-1.1-pro`) |
| `prompt` | string | ✅ | Text description of the desired image |
| `n` | integer | — | Number of images (1–10, not all models support >1) |
| `resolution` | string | — | Tier: `512`, `1K`, `2K`, `4K` |
| `aspect_ratio` | string | — | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `4:5`, `5:4`, `1:2`, `2:1`, `9:21`, `21:9`, etc. |
| `size` | string | — | Convenience shorthand — tier (`"2K"`) or explicit (`"2048x2048"`) |
| `quality` | string | — | `auto`, `low`, `medium`, `high` |
| `output_format` | string | — | `png`, `jpeg`, `webp` |
| `background` | string | — | `auto`, `transparent`, `opaque` (`transparent` requires png/webp) |
| `output_compression` | integer | — | 0–100 for webp/jpeg only |
| `seed` | integer | — | Deterministic generation (where supported) |
| `stream` | boolean | — | SSE streaming for progressive renders |
| `input_references` | array | — | Reference images for img2img |
| `provider.options` | object | — | Provider-specific passthrough params |

> **Always check `supported_parameters` from the models endpoint** — not every model supports
> every field. Unsupported params are silently ignored or may error.

---

## Response Format

### Standard (buffered)
```json
{
  "created": 1748372400,
  "data": [
    { "b64_json": "<base64-encoded-image>" }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 4175,
    "total_tokens": 4175,
    "cost": 0.04
  }
}
```

For **vector outputs** (e.g. Recraft SVG models), `media_type` is included:
```json
{ "b64_json": "...", "media_type": "image/svg+xml" }
```

### Decoding in TypeScript
```typescript
const imgData = result.data[0].b64_json;
// In Node.js:
const buffer = Buffer.from(imgData, "base64");
await fs.writeFile("output.png", buffer);

// In browser:
const img = document.createElement("img");
img.src = `data:image/png;base64,${imgData}`;
```

---

## Image Configuration

### Resolution & Aspect Ratio
```typescript
{
  model: "bytedance-seed/seedream-4.5",
  prompt: "a landscape photo",
  resolution: "2K",
  aspect_ratio: "16:9"
}
```
- `resolution` and `aspect_ratio` can be combined
- `size` is a convenience alias — pass `"2K"` or `"2048x2048"`. **Don't mix `size` with
  `resolution`/`aspect_ratio`** — conflicting values are rejected.

### Quality & Format
```typescript
{
  model: "openai/gpt-image-1",
  prompt: "a product photo on white background",
  quality: "high",
  output_format: "png",
  background: "transparent"
}
```

### Multiple Images
```typescript
{ model: "openai/gpt-image-1", prompt: "a cute cat", n: 4 }
// result.data is an array of n images
```

---

## Image-to-Image (Reference Images)

Pass reference images via `input_references`:
```typescript
{
  model: "openai/gpt-image-1",
  prompt: "make this scene look like a watercolor painting",
  input_references: [
    {
      type: "image_url",
      image_url: {
        url: "https://example.com/photo.jpg"
        // OR base64: "data:image/png;base64,..."
      }
    }
  ]
}
```
Number of accepted references varies by provider — check `supported_parameters`.

---

## Streaming Image Generation

Models with `supports_streaming: true` return partial renders via SSE:
```typescript
const response = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: { "Authorization": `Bearer ${KEY}`, "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "openai/gpt-image-1",
    prompt: "a detailed landscape painting",
    stream: true,
  }),
});

for await (const chunk of response.body!) {
  const text = new TextDecoder().decode(chunk);
  for (const line of text.split("\n")) {
    if (!line.startsWith("data: ") || line === "data: [DONE]") continue;
    const event = JSON.parse(line.slice(6));
    if (event.type === "image_generation.partial_image") {
      // event.b64_json — partial render, update preview
    } else if (event.type === "image_generation.completed") {
      // event.b64_json — final image, event.usage.cost
    } else if (event.type === "error") {
      // event.error.message
    }
  }
}
```

SSE event types:
- `image_generation.partial_image` — progressive render chunk
- `image_generation.completed` — final image + usage/cost
- `error` — generation failed
- `data: [DONE]` — stream end sentinel

---

## Provider-Specific Options

Pass provider-specific params using the `provider_slug` from the endpoints API:
```typescript
{
  model: "black-forest-labs/flux.2-pro",
  prompt: "a dramatic portrait",
  provider: {
    options: {
      "black-forest-labs": {
        steps: 40,
        guidance: 3
      }
    }
  }
}
```
Check `allowed_passthrough_parameters` in the endpoint record for accepted keys.

---

## Capability Descriptor Types

When reading `supported_parameters` from the API:

| Type | Shape | Meaning |
|------|-------|---------|
| `enum` | `{ type: "enum", values: ["1K","2K","4K"] }` | Only these values accepted |
| `range` | `{ type: "range", min: 0, max: 100 }` | Any integer in range |
| `boolean` | `{ type: "boolean" }` | Supported (present = yes, absent = no) |

An **absent key** means that parameter is unsupported by that endpoint.

---

## Pricing Notes

- Pricing is per-endpoint (provider), not per model
- `billable` types: `output_image`, `input_image`, `input_reference`
- `unit` types: `image`, `megapixel`, `token`
- Resolution-tiered models have variant tiers (e.g. `2k`, `4k`) in the pricing array
- `usage.cost` in the response is the actual USD charged

---

## Gotchas & Common Issues

- ❌ **Wrong endpoint** — image generation uses `/api/v1/images`, NOT `/api/v1/chat/completions`
- ❌ **Unsupported params silently vary** — always check `supported_parameters` first
- ❌ **Conflicting size params** — don't use `size` together with `resolution`/`aspect_ratio`
- ❌ **Transparent background** — only works with `output_format: "png"` or `"webp"`
- ❌ **n > 1** — not universally supported; check model caps
- ✅ **Model IDs change** — always fetch `/api/v1/images/models` at runtime for current list

---

## Reference Files

- `references/models.md` — Current image models, providers, key capabilities, and pricing tiers
- `references/examples.md` — Full TypeScript/Node.js code examples for common patterns

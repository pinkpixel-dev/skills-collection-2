---
name: openai-image-generation
description: Complete reference for generating and editing images with the OpenAI API using GPT Image models (gpt-image-2, gpt-image-1.5, gpt-image-1, gpt-image-1-mini). ALWAYS trigger this skill when the user wants to generate images with OpenAI, mentions "gpt-image", "GPT Image", DALL-E replacement, image generation via the OpenAI Images API or Responses API `image_generation` tool, editing/inpainting images with a mask, multi-turn/iterative image editing, streaming partial images, or asks about OpenAI image generation pricing, sizes, quality settings, or moderation. Also trigger for building any image-generation feature in a Node/TypeScript/Python/Go app that should use OpenAI rather than another provider, or when comparing OpenAI image generation to other providers (Pollinations, Gemini, etc). If the user just says "generate an image with OpenAI" or "add AI image generation to my app" without naming a provider, this skill is a strong candidate to check.
---

# OpenAI Image Generation (GPT Image)

Reference for generating and editing images with OpenAI's GPT Image models via the **Image API** (`images.generate` / `images.edit`) or the **Responses API** (`image_generation` built-in tool).

## Which API to use

| Need | Use |
|---|---|
| Single image from one prompt, no conversation | **Image API** (`client.images.generate` / `client.images.edit`) |
| Conversational, iterative editing across turns; flexible image inputs (URL, base64, File ID) | **Responses API** (`tools: [{ type: "image_generation" }]`) |

With the Image API you pick the GPT Image model directly. With the Responses API you pick a mainline model (e.g. `gpt-5.6`) that supports the `image_generation` tool — the tool internally handles GPT Image model selection, and the mainline model's token usage is billed in addition to image generation cost.

`gpt-5` and newer mainline models support the `image_generation` tool in the Responses API. GPT Image models require **API Organization Verification** before use (`gpt-image-2`, `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`) — check the developer console if requests fail with a verification error.

## Quick start

### Generate an image — Image API (Node/TS)
```javascript
import OpenAI from "openai";
import fs from "fs";
const openai = new OpenAI();

const result = await openai.images.generate({
  model: "gpt-image-2",
  prompt: "A children's book drawing of a veterinarian using a stethoscope to listen to the heartbeat of a baby otter.",
});

const image_bytes = Buffer.from(result.data[0].b64_json, "base64");
fs.writeFileSync("otter.png", image_bytes);
```

### Generate an image — Image API (Python)
```python
from openai import OpenAI
import base64

client = OpenAI()
result = client.images.generate(
    model="gpt-image-2",
    prompt="A children's book drawing of a veterinarian using a stethoscope to listen to the heartbeat of a baby otter.",
)
with open("otter.png", "wb") as f:
    f.write(base64.b64decode(result.data[0].b64_json))
```

### Generate an image — Responses API tool (Node/TS)
```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
  model: "gpt-5.6",
  input: "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

const imageData = response.output
  .filter((o) => o.type === "image_generation_call")
  .map((o) => o.result);

if (imageData.length > 0) {
  const fs = await import("fs");
  fs.writeFileSync("otter.png", Buffer.from(imageData[0], "base64"));
}
```

The Image API returns base64-encoded PNG by default (`data[0].b64_json`). Set `n` to generate multiple images in one request (default is 1).

For full multi-language examples (JS/Python/Go/curl/CLI), editing, masking, streaming, multi-turn conversations, and error handling, see `references/api-reference.md`.

## Models

| Model | Notes |
|---|---|
| `gpt-image-2` | Latest. Accepts near-arbitrary resolutions (not just fixed presets). Always processes image inputs at **high fidelity** — `input_fidelity` param is not accepted/needed. Does **not** support transparent backgrounds. |
| `gpt-image-1.5` | Prior generation. Fixed size presets. Token-based output pricing. |
| `gpt-image-1` | Prior generation. Fixed size presets. Token-based output pricing. |
| `gpt-image-1-mini` | Smaller/cheaper prior-generation model. Fixed size presets. |

All four require **API Organization Verification**.

## Pricing

Cost = input text tokens + input image tokens (edits only) + image output tokens. `gpt-image-2` always processes input images at high fidelity, so edit requests with reference images can cost more in input tokens.

### Per-image pricing by model, quality, and size (USD)

| Model | Quality | 1024×1024 | 1024×1536 | 1536×1024 |
|---|---|---|---|---|
| **GPT Image 2** | Low | $0.006 | $0.005 | $0.005 |
| | Medium | $0.053 | $0.041 | $0.041 |
| | High | $0.211 | $0.165 | $0.165 |
| **GPT Image 1.5** | Low | $0.009 | $0.013 | $0.013 |
| | Medium | $0.034 | $0.05 | $0.05 |
| | High | $0.133 | $0.2 | $0.2 |
| **GPT Image 1** | Low | $0.011 | $0.016 | $0.016 |
| | Medium | $0.042 | $0.063 | $0.063 |
| | High | $0.167 | $0.25 | $0.25 |
| **GPT Image 1 Mini** | Low | $0.005 | $0.006 | $0.006 |
| | Medium | $0.011 | $0.015 | $0.015 |
| | High | $0.036 | $0.052 | $0.052 |

`gpt-image-2` supports thousands of valid resolutions beyond this table — a larger non-square resolution can sometimes produce *fewer* output tokens (and cost less) than a smaller square one at the same quality. Use OpenAI's pricing calculator for exact non-standard sizes.

### Output tokens for models prior to gpt-image-2

Latency and cost for `gpt-image-1.5`/`gpt-image-1`/`gpt-image-1-mini` scale with output tokens, which depend on size/quality:

| Quality | Square (1024×1024) | Portrait (1024×1536) | Landscape (1536×1024) |
|---|---|---|---|
| Low | 272 tokens | 408 tokens | 400 tokens |
| Medium | 1056 tokens | 1584 tokens | 1568 tokens |
| High | 4160 tokens | 6240 tokens | 6208 tokens |

### Streaming cost
Each partial image (via `partial_images`) incurs an **extra 100 image output tokens** on top of the final image cost.

## Customizing output

- **`size`**: e.g. `1024x1024`, `1536x1024` (landscape), `1024x1536` (portrait), or `auto` (default, model picks). `gpt-image-2` also accepts 2K sizes (`2048x2048`, `2048x1152`) and 4K sizes (`3840x2160`, `2160x3840`) — anything over 2560×1440 total pixels (~3.7MP) is experimental. Constraints for `gpt-image-2` custom sizes: max edge ≤3840px, both edges multiples of 16px, long:short ratio ≤3:1, total pixels between 655,360 and 8,294,400.
- **`quality`**: `low` | `medium` | `high` | `auto` (default). Use `low` for fast drafts/thumbnails/iteration, move to `medium`/`high` for final assets.
- **`background`**: `opaque` or `auto`. `gpt-image-2` does **not** support `transparent`.
- **`output_format`**: `png` (default) | `jpeg` | `webp`. `jpeg` is fastest — prefer it if latency matters.
- **`output_compression`**: 0–100, only for `jpeg`/`webp`.
- **`moderation`**: `auto` (default, standard filtering) | `low` (less restrictive).

## Editing images

The edits endpoint (Image API `images.edit`) or the `image_generation` tool with input images (Responses API) can:
- Edit an existing image with a new prompt
- Generate a new image using one or more reference images (e.g. combine items from 4 reference photos into one new image)
- Edit only part of an image using a **mask** (inpainting) — masking is prompt-guided, not pixel-precise. Mask must match the source image's format/size, be under 50MB, and have an alpha channel. If multiple input images are given, the mask applies to the first one only.

Responses API accepts input images as a fully-qualified URL, a base64 data URL, or a File ID (via the Files API, `purpose: "vision"`). See `references/api-reference.md` for full generate/edit/mask code in JS, Python, Go, and curl.

## Multi-turn editing (Responses API only)

Iterate on an image across turns by either passing `previous_response_id`, or carrying the prior `image_generation_call` output (or just its `id`) in the next `input`. The optional `action` param on the tool controls behavior: `"auto"` (default, model decides), `"generate"` (always new image), `"edit"` (force edit — errors if no image is in context). Mainline models also auto-revise your prompt for better results; read it back via `revised_prompt` on the image generation call.

## Streaming

Both APIs support streaming partial images via `partial_images: 0-3` (`stream: true`). 0 = only the final image. You may get fewer partials than requested if generation finishes fast. Responses API emits `response.image_generation_call.partial_image` events; Image API emits `image_generation.partial_image` events.

## Limitations

- Complex prompts can take up to **2 minutes**.
- Text rendering is improved but still imperfect for precise placement/clarity.
- Recurring characters/brand elements may drift across generations.
- Precise layout-sensitive composition can be hit-or-miss.

## Errors & moderation

All prompts and outputs are filtered per OpenAI's content policy. Moderation-blocked requests return `error.code = "moderation_blocked"` with an optional `error.moderation_details` object containing `moderation_stage` (`input` | `output` | `unknown`) and `categories` (e.g. `harassment`, `self-harm`, `sexual`, `violence`). Branch on `error.code` first; treat `moderation_details` as extra context for logs/support, not the user-facing message. Retry `429`/`5xx` errors; don't blindly retry `image_generation_user_error` codes — the prompt or inputs need to change. Full error-handling code in `references/api-reference.md`.

## Reference files

- `references/api-reference.md` — complete code examples (JS/Python/Go/curl/CLI) for: generation, Responses API multi-turn (previous_response_id and image ID variants), streaming both APIs, creating reference-image edits, mask-based inpainting (including adding an alpha channel to a B&W mask), and full moderation error-handling.

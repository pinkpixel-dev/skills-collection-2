# Images & Vision

## Which API for which image task

| Task | API |
|---|---|
| Analyze images + generate images as output (multimodal) | Responses API |
| Generate images only, optionally using image input | Images API |
| Analyze images as input → text/audio output | Chat Completions API |

## Generating/editing images

Flagship image model: `gpt-image-2` — understands text + images, uses world knowledge for realistic, instruction-following generation (e.g. it knows which gemstones look like what, without a reference image).

```typescript
const response = await openai.responses.create({
  model: "gpt-5.6",
  input: "Generate an image of a gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

const imageData = response.output
  .filter((o) => o.type === "image_generation_call")
  .map((o) => o.result); // base64 string(s)

if (imageData.length > 0) {
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageData[0], "base64"));
}
```

Same pattern in Python: iterate `response.output`, filter `type == "image_generation_call"`, base64-decode `.result` and write to file.

## Analyzing images (vision)

Give a model image input via **URL**, **base64 data URL**, or a **file ID** (from the Files API). Multiple images can go in one `content` array — each one counts toward token billing.

```typescript
const response = await openai.responses.create({
  model: "gpt-5.6",
  input: [{
    role: "user",
    content: [
      { type: "input_text", text: "what's in this image?" },
      { type: "input_image", image_url: "https://example.com/photo.jpg" },
    ],
  }],
});
console.log(response.output_text);
```

Base64 variant: swap `image_url` for a data URL, e.g. `` `data:image/jpeg;base64,${base64Image}` ``.

File-ID variant: upload via `openai.files.create({ file, purpose: "vision" })`, then pass `{ type: "input_image", file_id }`.

### Input requirements

- File types: PNG, JPEG/JPG, WEBP, non-animated GIF
- Up to 512 MB total payload per request, up to 1,500 images per request
- No watermarks/logos, no NSFW, must be clear enough for a human to parse

### Detail levels

`detail` controls resolution/cost tradeoff: `low`, `high`, `original`, or `auto` (default if omitted).

| Detail | Best for |
|---|---|
| `low` | Fast/cheap, fine detail unimportant — resized to 512×512 |
| `high` | Standard high-fidelity understanding |
| `original` | Large/dense/spatially-sensitive images, computer-use — available on `gpt-5.4`+ |
| `auto` | On `gpt-5.5`/GPT-5.6-family models, behaves identically to `original` |

For computer-use, localization, or click-accuracy work on `gpt-5.4`+, explicitly use `"detail": "original"`.

### Model sizing/resizing behavior (matters for cost + fidelity)

- **GPT-5.6 family**: `low`/`high` resize to finite limits; `original`/`auto` preserve input dimensions with **no** patch-budget or pixel-limit resizing — large images can cost noticeably more tokens than on older models. Resize client-side or use `low`/`high` if you want to control cost/latency.
- **`gpt-5.5` / `gpt-5.4`**: `high` caps at 2,500 patches or 2048px max dimension; `original` caps at 10,000 patches or 6000px max dimension (aspect-ratio-preserving resize if exceeded). `gpt-5.5`'s `auto`/omitted behaves like `original`; `gpt-5.4`'s `auto`/omitted behaves like `high` — note this difference between the two snapshots.
- **Mini/nano/o4-mini/older 4.1-mini,nano snapshots**: only `low`/`high`/`auto` supported (no `original`); `high` caps at 1,536 patches or 2048px.
- **GPT-4o, GPT-4.1, GPT-4o-mini, computer-use-preview, o-series except o4-mini**: use older tile-based resizing (see cost formulas below), not patch-based.

### Cost calculation — patch-based models

For patch-based models, cost is computed in 32×32px patches:

1. `original_patch_count = ceil(width/32) × ceil(height/32)`
2. If that exceeds the model's patch budget, compute a shrink factor to fit within budget (`shrink_factor = sqrt((32² × patch_budget) / (width × height))`), then adjust it so the resized integer-pixel image still fits the patch budget after rounding.
3. Recompute patch count on the resized image — this is the pre-multiplier token count.
4. Multiply by the model's multiplier:

| Model | Multiplier |
|---|---|
| `gpt-5.4-mini` | 1.62 |
| `gpt-5.4-nano` | 2.46 |
| `gpt-5-mini` | 1.62 |
| `gpt-5-nano` | 2.46 |
| `gpt-4.1-mini` (2025-04-14 snapshot) | 1.62 |
| `gpt-4.1-nano` (2025-04-14 snapshot) | 2.46 |
| `o4-mini` | 1.72 |

Worked example (1,536-patch budget model): a 1024×1024 image needs 1,024 patches (under budget, no resize) → multiply by the model's multiplier for billed tokens. A 1800×2400 image needs 4,275 raw patches (over budget) → gets shrunk to ~1056×1408 → 1,452 patches → multiply by the model's multiplier.

### Cost calculation — tile-based models (GPT-4o, GPT-4.1, GPT-4o-mini, CUA, o-series except o4-mini)

`low` detail = flat base-token cost. `high` detail: scale to fit 2048×2048, then scale so shortest side = 768px, count 512px tiles, each tile costs a fixed amount, plus a base amount:

| Model | Base tokens | Tile tokens |
|---|---|---|
| `gpt-5`, `gpt-5-chat-latest` | 70 | 140 |
| `gpt-4o`, `gpt-4.1`, `gpt-4.5` | 85 | 170 |
| `gpt-4o-mini` | 2833 | 5667 |
| `o1`, `o1-pro`, `o3` | 75 | 150 |
| `computer-use-preview` | 65 | 129 |

GPT Image 1 input pricing uses the same tile logic but scales to a 512px shortest side instead of 768px. Low fidelity: base 65 + 129/tile. High fidelity: adds 4,160 extra tokens for square images, or 6,240 extra tokens for portrait/landscape, on top of the tile tokens.

For exact current numbers, point the user to OpenAI's pricing-page image calculator rather than hand-computing for anything cost-sensitive.

## Known vision limitations

- Not suitable for medical images (no medical advice use)
- Weaker on non-Latin-alphabet text (Japanese, Korean, etc.)
- Struggles with small text — enlarge it, or use `"detail": "original"` where available
- Can misread rotated/upside-down content
- Struggles with graphs/charts using subtle line-style distinctions (dashed vs dotted)
- Weak at precise spatial localization (e.g. reading chess positions)
- Can hallucinate captions/descriptions
- Struggles with panoramic/fisheye images
- Ignores original filenames/metadata
- Gives approximate, not exact, counts of objects
- CAPTCHAs are blocked from submission for safety reasons

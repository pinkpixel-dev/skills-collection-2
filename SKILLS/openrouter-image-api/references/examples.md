# OpenRouter Image API — Code Examples

## TypeScript / Node.js Examples

### Basic text-to-image
```typescript
import fs from "fs/promises";

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY!;

async function generateImage(prompt: string, model = "black-forest-labs/flux-1.1-pro") {
  const response = await fetch("https://openrouter.ai/api/v1/images", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model, prompt }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`OpenRouter image API error ${response.status}: ${err}`);
  }

  const result = await response.json();
  const b64 = result.data[0].b64_json;
  const buffer = Buffer.from(b64, "base64");
  await fs.writeFile("output.png", buffer);
  console.log(`Cost: $${result.usage?.cost ?? "unknown"}`);
  return buffer;
}
```

---

### Discover models at runtime
```typescript
async function getImageModels() {
  const res = await fetch("https://openrouter.ai/api/v1/images/models", {
    headers: { "Authorization": `Bearer ${OPENROUTER_API_KEY}` },
  });
  const { data } = await res.json();
  return data; // Array of model objects with id, name, supported_parameters, etc.
}

async function getModelEndpoints(modelId: string) {
  const res = await fetch(
    `https://openrouter.ai/api/v1/images/models/${modelId}/endpoints`,
    { headers: { "Authorization": `Bearer ${OPENROUTER_API_KEY}` } }
  );
  const { endpoints } = await res.json();
  return endpoints; // Per-provider pricing + supported params
}
```

---

### With resolution and aspect ratio
```typescript
const result = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "bytedance-seed/seedream-4.5",
    prompt: "epic landscape with mountains and golden hour light",
    resolution: "2K",
    aspect_ratio: "16:9",
  }),
}).then(r => r.json());
```

---

### Transparent background (product shots, icons)
```typescript
const result = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "openai/gpt-image-1",
    prompt: "a sleek coffee mug product photo, studio lighting, clean",
    quality: "high",
    output_format: "png",   // required for transparent
    background: "transparent",
  }),
}).then(r => r.json());
```

---

### Image-to-image
```typescript
import fs from "fs/promises";

async function img2img(imagePath: string, prompt: string) {
  const imageData = await fs.readFile(imagePath);
  const b64Input = imageData.toString("base64");
  const mimeType = imagePath.endsWith(".png") ? "image/png" : "image/jpeg";

  const result = await fetch("https://openrouter.ai/api/v1/images", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "openai/gpt-image-1",
      prompt,
      input_references: [
        {
          type: "image_url",
          image_url: { url: `data:${mimeType};base64,${b64Input}` },
        },
      ],
    }),
  }).then(r => r.json());

  const out = Buffer.from(result.data[0].b64_json, "base64");
  await fs.writeFile("output.png", out);
}
```

---

### Streaming (progressive renders)
```typescript
async function streamImage(prompt: string) {
  const response = await fetch("https://openrouter.ai/api/v1/images", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "openai/gpt-image-1",
      prompt,
      stream: true,
    }),
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop()!;

    for (const line of lines) {
      if (!line.startsWith("data: ") || line === "data: [DONE]") continue;
      const event = JSON.parse(line.slice(6));

      if (event.type === "image_generation.partial_image") {
        console.log(`Partial render ${event.partial_image_index}`);
        // Use event.b64_json for live preview
      } else if (event.type === "image_generation.completed") {
        console.log(`Done! Cost: $${event.usage.cost}`);
        const out = Buffer.from(event.b64_json, "base64");
        await fs.writeFile("output.png", out);
      } else if (event.type === "error") {
        throw new Error(event.error.message);
      }
    }
  }
}
```

---

### Multiple images
```typescript
const result = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "openai/gpt-image-1",
    prompt: "a cute cartoon robot",
    n: 4,
    quality: "medium",
  }),
}).then(r => r.json());

// result.data is an array of 4 images
for (let i = 0; i < result.data.length; i++) {
  const buf = Buffer.from(result.data[i].b64_json, "base64");
  await fs.writeFile(`output_${i}.png`, buf);
}
```

---

### Provider-specific passthrough (FLUX)
```typescript
const result = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "black-forest-labs/flux.2-pro",
    prompt: "dramatic cinematic portrait, moody lighting",
    provider: {
      options: {
        "black-forest-labs": {
          steps: 40,
          guidance: 3,
        },
      },
    },
  }),
}).then(r => r.json());
```

---

### Vector output (SVG from Recraft)
```typescript
const result = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "recraft-ai/recraft-v3-svg",
    prompt: "minimalist coffee cup logo, clean lines, modern",
  }),
}).then(r => r.json());

// Check media_type for vector outputs
const { b64_json, media_type } = result.data[0];
if (media_type === "image/svg+xml") {
  const svgContent = Buffer.from(b64_json, "base64").toString("utf-8");
  await fs.writeFile("logo.svg", svgContent);
}
```

---

### React component (browser)
```tsx
import { useState } from "react";

export function ImageGenerator() {
  const [prompt, setPrompt] = useState("");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    try {
      const res = await fetch("/api/generate-image", {  // proxy through your backend
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, model: "black-forest-labs/flux-1.1-pro" }),
      });
      const { b64_json } = await res.json();
      setImageUrl(`data:image/png;base64,${b64_json}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <textarea value={prompt} onChange={e => setPrompt(e.target.value)} />
      <button onClick={generate} disabled={loading}>
        {loading ? "Generating..." : "Generate"}
      </button>
      {imageUrl && <img src={imageUrl} alt="Generated" />}
    </div>
  );
}
```

> ⚠️ Never expose your `OPENROUTER_API_KEY` in frontend code. Always proxy through a backend.

---

### Error handling
```typescript
async function safeGenerate(prompt: string, model: string) {
  const res = await fetch("https://openrouter.ai/api/v1/images", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model, prompt }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: { message: res.statusText } }));
    const msg = body?.error?.message ?? `HTTP ${res.status}`;
    // Common errors:
    // 400 — bad params (unsupported resolution, conflicting size params, etc.)
    // 401 — invalid API key
    // 402 — insufficient credits
    // 429 — rate limited
    // 503 — model/provider unavailable
    throw new Error(`Image generation failed: ${msg}`);
  }

  return res.json();
}
```

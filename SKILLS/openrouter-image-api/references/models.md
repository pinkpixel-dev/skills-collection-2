# OpenRouter Image Models Reference

> Last updated: June 2026. Always verify current models and pricing at:
> `GET https://openrouter.ai/api/v1/images/models`
> or browse: https://openrouter.ai/models?output_modalities=image

---

## Model List

### OpenAI
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `openai/gpt-image-1` | GPT Image 1 | High quality, transparent bg, img2img, multiple images (n), streaming |
| `openai/dall-e-3` | DALL-E 3 | Prompt rewriting, high fidelity, quality tiers |
| `openai/dall-e-2` | DALL-E 2 | Budget option, img2img, inpainting |

### Black Forest Labs (FLUX)
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `black-forest-labs/flux-1.1-pro` | FLUX 1.1 Pro | Fast, high quality, excellent prompt adherence |
| `black-forest-labs/flux-1.1-pro-ultra` | FLUX 1.1 Pro Ultra | Ultra-high resolution, up to 4K |
| `black-forest-labs/flux-pro` | FLUX Pro | Production quality |
| `black-forest-labs/flux-dev` | FLUX Dev | Development/research, lower cost |
| `black-forest-labs/flux-schnell` | FLUX Schnell | Fastest FLUX, good for iteration |
| `black-forest-labs/flux.2-pro` | FLUX 2 Pro | Latest generation, provider passthrough (steps, guidance) |

### Bytedance
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `bytedance-seed/seedream-4.5` | Seedream 4.5 | Text-to-image + img2img, 1K/2K/4K resolution tiers |

### Google
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `google/imagen-3` | Imagen 3 | High fidelity, photorealistic, safety filters |
| `google/imagen-3-fast` | Imagen 3 Fast | Faster, lower cost variant |
| `google/imagen-4` | Imagen 4 | Latest Imagen, top quality |
| `google/imagen-4-ultra` | Imagen 4 Ultra | Highest quality, slower |

### Stability AI
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `stability/stable-diffusion-3.5-large` | SD 3.5 Large | Latest Stable Diffusion, high quality |
| `stability/stable-diffusion-3.5-large-turbo` | SD 3.5 Large Turbo | Fast SD3.5 |
| `stability/stable-diffusion-3.5-medium` | SD 3.5 Medium | Balanced quality/speed |
| `stability/stable-image-ultra` | Stable Image Ultra | Premium Stability offering |
| `stability/stable-image-core` | Stable Image Core | Core quality tier |
| `stability/stable-diffusion-xl-1024-v1-0` | SDXL 1.0 | Classic SDXL |

### Recraft
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `recraft-ai/recraft-v3` | Recraft V3 | Design-focused, style control |
| `recraft-ai/recraft-v3-svg` | Recraft V3 SVG | **Vector output** (media_type: image/svg+xml), logos/icons |

### Ideogram
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `ideogram-ai/ideogram-v2` | Ideogram V2 | Excellent text rendering in images |
| `ideogram-ai/ideogram-v2-turbo` | Ideogram V2 Turbo | Faster Ideogram |

### Midjourney / MJ
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `midjourney/midjourney` | Midjourney | Highly aesthetic, artistic quality |

### Other Notable Models
| Model ID | Name | Key Capabilities |
|----------|------|-----------------|
| `fal-ai/aura-flow` | AuraFlow | Open source, artistic |
| `fal-ai/hyper-sdxl` | HyperSDXL | Very fast SDXL variant |
| `playground-ai/playground-v2.5-1024px-aesthetic` | Playground v2.5 | Aesthetic quality |

---

## Capability Matrix (Common Parameters)

| Model | n>1 | streaming | img2img | transparent bg | vector out | seed |
|-------|-----|-----------|---------|----------------|------------|------|
| gpt-image-1 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| dall-e-3 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| flux-1.1-pro | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| flux-1.1-pro-ultra | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| flux.2-pro | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| seedream-4.5 | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| imagen-3 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| imagen-4 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| recraft-v3-svg | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| ideogram-v2 | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| sd-3.5-large | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

> ⚠️ This matrix is approximate. Always verify via the API:
> `GET https://openrouter.ai/api/v1/images/models/{model-id}/endpoints`

---

## Resolution Support by Model

### Tiered Resolution (1K/2K/4K)
- `bytedance-seed/seedream-4.5` — 1K, 2K, 4K
- `black-forest-labs/flux-1.1-pro-ultra` — up to 4K

### Quality-based (low/medium/high/auto)
- `openai/gpt-image-1` — low, medium, high
- `openai/dall-e-3` — standard, hd

### Fixed sizes (DALL-E 2 style)
- `openai/dall-e-2` — 256x256, 512x512, 1024x1024

---

## Pricing Tiers (approximate, verify via API)

| Model | Cost per image | Notes |
|-------|---------------|-------|
| `openai/gpt-image-1` | ~$0.04–0.17 | Quality-dependent |
| `openai/dall-e-3` | ~$0.04–0.12 | Size/quality-dependent |
| `black-forest-labs/flux-1.1-pro` | ~$0.04 | Flat per image |
| `black-forest-labs/flux-1.1-pro-ultra` | ~$0.06 | Higher res |
| `black-forest-labs/flux-schnell` | ~$0.003 | Cheapest FLUX |
| `google/imagen-3` | ~$0.03–0.04 | |
| `google/imagen-4-ultra` | ~$0.06 | |
| `stability/stable-image-ultra` | ~$0.08 | |
| `recraft-ai/recraft-v3` | ~$0.04 | |
| `ideogram-ai/ideogram-v2` | ~$0.08 | |

> Pricing changes frequently. Always check `pricing` in the endpoints API response for
> current costs before building billing logic.

---

## Model Selection Guide

**Best quality / most capable:** `openai/gpt-image-1`, `google/imagen-4-ultra`

**Best for photorealism:** `black-forest-labs/flux-1.1-pro-ultra`, `stability/stable-image-ultra`

**Best for text in images:** `ideogram-ai/ideogram-v2`

**Best for logos/icons (vector):** `recraft-ai/recraft-v3-svg`

**Best for artistic/aesthetic:** `midjourney/midjourney`, `black-forest-labs/flux.2-pro`

**Fastest / cheapest iteration:** `black-forest-labs/flux-schnell`

**Transparent backgrounds:** `openai/gpt-image-1`, `recraft-ai/recraft-v3-svg`

**Image-to-image:** `openai/gpt-image-1`, `bytedance-seed/seedream-4.5`

**Streaming progressive renders:** `openai/gpt-image-1`

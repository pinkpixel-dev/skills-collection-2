# Pollinations Models Reference

> Dynamic — always check `GET /models` or type-specific endpoints for latest list.
> No auth required for model listing.

---

## Text Models

`GET /text/models` — includes context window, tool support, pricing

| Model ID | Notes |
|----------|-------|
| `openai` | GPT default |
| `openai-fast` | Faster GPT |
| `openai-large` | Larger GPT |
| `gpt-5.4-mini` | |
| `gpt-5.5` | |
| `claude-fast` | Claude (fast) |
| `claude` | Claude default |
| `claude-large` | Claude large |
| `claude-opus-4.7` | Claude Opus |
| `gemini` | Gemini default |
| `gemini-3.5-flash` | |
| `gemini-flash-lite-3.1` | |
| `gemini-fast` | |
| `gemini-large` | |
| `gemini-search` | Web-grounded |
| `gemini-search-fast` | Web-grounded fast |
| `gemini-search-large` | Web-grounded large |
| `deepseek` | |
| `deepseek-pro` | |
| `grok` | |
| `grok-large` | |
| `grok-4.3` | |
| `llama` | |
| `llama-maverick` | |
| `llama-scout` | |
| `mistral` | |
| `mistral-4` | |
| `mistral-large` | |
| `qwen-coder` | Code-focused |
| `qwen-coder-large` | Code-focused large |
| `qwen-large` | |
| `qwen-vision` | Vision input |
| `qwen-vision-pro` | Vision pro |
| `qwen-safety` | Safety-focused |
| `perplexity-fast` | Perplexity |
| `perplexity-reasoning` | Reasoning |
| `kimi` | |
| `kimi-k2.6` | |
| `nova-fast` | |
| `nova` | |
| `glm` | |
| `minimax` | |
| `polly` | |
| `midijourney` | Creative |
| `midijourney-large` | |
| `gemma` | |

---

## Image Models

`GET /image/models` — includes capabilities and pricing

| Model ID | Notes |
|----------|-------|
| `flux` | General purpose, recommended default |
| `kontext` | Context-aware generation |
| `gptimage` | GPT image |
| `gptimage-large` | |
| `gpt-image-2` | |
| `seedream` | |
| `seedream-pro` | |
| `seedream5` | |
| `nanobanana` | |
| `nanobanana-2` | |
| `nanobanana-pro` | |
| `zimage` | |
| `wan-image` | |
| `wan-image-pro` | |
| `qwen-image` | |
| `grok-imagine` | |
| `grok-imagine-pro` | |
| `klein` | |
| `p-image` | |
| `p-image-edit` | Editing/img2img |
| `nova-canvas` | |

### Image Generation Parameters

| Param | Type | Description |
|-------|------|-------------|
| `model` | string | Model ID |
| `width` | int | Output width (px) |
| `height` | int | Output height (px) |
| `seed` | int | For reproducibility |
| `enhance` | bool | Auto-enhance prompt |
| `negative_prompt` | string | What to avoid |
| `quality` | string | Quality level |
| `image` | string | URL for img2img (with `p-image-edit`) |
| `transparent` | bool | Transparent background |

---

## Video Models

`GET /image/models` also covers video

| Model ID | Notes |
|----------|-------|
| `veo` | Google Veo |
| `seedance-pro` | |
| `seedance-2.0` | |
| `wan` | |
| `wan-fast` | |
| `wan-pro` | |
| `grok-video-pro` | |
| `ltx-2` | |
| `p-video` | |
| `nova-reel` | |

### Video Parameters

| Param | Type | Description |
|-------|------|-------------|
| `model` | string | Model ID |
| `duration` | int | Duration in seconds |
| `aspectRatio` | string | e.g. `16:9`, `9:16` |
| `audio` | bool | Include audio |

---

## Audio Models

`GET /audio/models` — includes voices

| Model ID | Notes |
|----------|-------|
| `elevenlabs` | High quality TTS |
| `elevenflash` | Fast TTS |
| `elevenmusic` | Music generation |
| `whisper` | OpenAI Whisper (STT) |
| `scribe` | STT |
| `universal-2` | |
| `universal-3-pro` | |
| `acestep` | |
| `qwen-tts` | |
| `qwen-tts-instruct` | Instruction-following TTS |

### All Available Voices

**OpenAI-style:** alloy, echo, fable, onyx, nova, shimmer, ash, ballad, coral, sage, verse

**ElevenLabs female:** rachel, domi, bella, elli, charlotte, dorothy, sarah, emily, lily, matilda

**ElevenLabs male:** adam, antoni, arnold, josh, sam, daniel, charlie, james, fin, callum, liam, george, brian, bill

Output formats: `mp3`, `wav`, `flac`, `opus`, `pcm16`

---

## Embedding Models

`GET /embeddings/models`

| Model ID | Max Dimensions | Input Types |
|----------|---------------|-------------|
| `openai-3-small` | 1536 | text |
| `openai-3-large` | 3072 | text |
| `gemini-2` | 3072 | text, image, audio, video |
| `cohere-embed-v4` | — | text |
| `qwen3-embedding-8b` | 4096 | text |

- Batch: up to 32 strings
- `task_type` param: Gemini models only

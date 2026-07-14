---
name: openai-api
description: Complete reference for building with the OpenAI API — Responses API (the recommended primitive), Chat Completions, text generation/prompting, vision/image understanding, GPT Image generation, audio/speech (realtime + request-based), Structured Outputs (JSON schema), tools (web search, file search, function calling, remote MCP, tool search, computer use), and current model pricing tiers. ALWAYS trigger on "OpenAI API", the `openai` npm/pip package, GPT model names (gpt-5.x, gpt-4.x, o-series), Responses API, Chat Completions, migrating Chat Completions to Responses, function/tool calling with OpenAI, Structured Outputs, JSON schema responses, vision/image input, GPT Image, realtime voice agents, TTS/STT via OpenAI, or OpenAI pricing/cost questions. Also trigger for OpenAI-vs-other-provider comparisons or building agent/tool loops with OpenAI's built-in tools. Trigger even if the user just describes calling GPT models in TypeScript/Node/Python/curl without saying "OpenAI" explicitly.
---

# OpenAI API

Badass reference for wiring up the OpenAI API — built from the latest OpenAI docs (Responses API generation, migrated from Chat Completions and its being deprecated on a timeline; images/vision; audio; structured outputs; tools; pricing).

## Golden rule: use the Responses API for anything new

**Responses API (`/v1/responses`) is the recommended primitive for all new projects.** Chat Completions (`/v1/chat/completions`) still works and is still supported, but Responses is the future-facing API: better performance with reasoning models, native multi-tool agentic loop in a single request, better prompt caching (lower cost), stateful conversation management, and it's what all new built-in tools (web search, file search, remote MCP, computer use, image generation, tool search) are designed around.

Only reach for Chat Completions when:
- You're maintaining/extending an existing Chat Completions integration and a full migration isn't worth it right now
- You need the audio-in-chat pattern (`modalities: ["text","audio"]`) — Responses docs currently describe text/image in, text out only; use Chat Completions with an audio-capable model (`gpt-audio-1.5`) for that specific case, or Realtime for live voice.

If the user has existing Chat Completions code and wants to modernize it, see `references/migrating-to-responses.md`.

## Routing table — which reference file to read

| User is asking about... | Read this file |
|---|---|
| Basic text generation, prompting, `instructions` vs `input`, message roles (developer/user/assistant), model selection, prompt versioning | `references/text-generation.md` |
| Migrating existing Chat Completions code to Responses, mapping messages→Items, streaming event differences, multi-turn state (`previous_response_id` vs manual replay vs Conversations API) | `references/migrating-to-responses.md` |
| Image input/vision (analyzing images, detail levels, tokenization/cost of image inputs), or image generation (GPT Image, `gpt-image-2`, editing images) | `references/images-vision.md` |
| Audio: speech-to-text, text-to-speech, realtime voice agents, speech-to-speech, adding audio to an existing chat app | `references/audio-speech.md` |
| Structured Outputs, JSON schema responses, `text.format`, JSON mode, refusals field, function calling with strict schemas | `references/structured-outputs.md` |
| Tools: web search, file search, function calling, remote MCP servers, tool search (deferred tool loading), computer use, Agents SDK tool wiring | `references/tools.md` |
| Pricing, cost per token, batch vs priority vs flex pricing tiers, which model is cheapest, cost calculators | `references/pricing.md` |

Read only what's relevant — don't load every reference file for a simple question.

## Quick-start pattern (Responses API, TypeScript)

```typescript
import OpenAI from "openai";
const client = new OpenAI(); // reads OPENAI_API_KEY from env

const response = await client.responses.create({
  model: "gpt-5.6",           // pick current flagship unless user specifies otherwise
  instructions: "You are a helpful assistant.", // system-level guidance, highest priority
  input: "Hello!",            // string, or array of {role, content} items
});

console.log(response.output_text); // convenience aggregator of all text output
```

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5.6",
    instructions="You are a helpful assistant.",
    input="Hello!",
)
print(response.output_text)
```

**Gotcha:** `response.output` is an array of typed **Items** (message, reasoning, function_call, function_call_output, etc.) — never assume the text lives at `output[0].content[0].text`. Use `output_text` for the common case, or iterate `output` by `.type` when you need reasoning/tool items too.

## Gotchas & non-obvious constraints

- **`instructions` doesn't carry across `previous_response_id` chains.** Resend it every request if you're chaining responses instead of manually replaying `input`.
- **Billing on chained responses**: even with `previous_response_id`, all prior input tokens in the chain are billed as input tokens again — it's not free just because OpenAI is holding state for you.
- **Structured Outputs schema location moved**: `response_format` (Chat Completions) → `text.format` (Responses). Don't mix them up when porting code.
- **Function/tool definitions are tagged differently**: externally tagged in Chat Completions, internally tagged in Responses. Also, Responses attempts `strict: true` by default and silently falls back to non-strict if the schema can't be made strict-compatible (returns `strict: false` on the resolved tool) — check for this if you expected strict mode.
- **Reasoning models (`gpt-5.6`, o-series) perform meaningfully better on Responses than Chat Completions** — if the user is using a reasoning model, steer them to Responses even if they didn't ask about migrating.
- **Starting with GPT-5.4, tool calling is not supported in Chat Completions with `reasoning: none`.**
- **Stateful by default**: Responses (and Chat Completions for new accounts) store data by default. Set `store: false` to disable. For Zero Data Retention orgs, pair `store: false` with `include: ["reasoning.encrypted_content"]` to keep reasoning continuity without persistence — OpenAI enforces `store: false` automatically for ZDR orgs.
- **Assistants API is deprecated** (sunset Aug 26, 2026) — steer any Assistants API question toward Responses instead.
- **`n` (multiple parallel generations) doesn't exist in Responses** — one generation per request; fire multiple requests if you need candidates.
- Only `gpt-5.4` and later support the `tool_search` deferred-tool-loading tool.
- Model names in these docs (e.g. `gpt-5.6`, `gpt-5.6-sol/terra/luna`, `o4-mini`) reflect the source docs' snapshot — always sanity-check current model availability against live docs if the user's request is cost- or capability-sensitive, since OpenAI ships new snapshots frequently.

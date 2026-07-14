# Migrating: Chat Completions → Responses API

Chat Completions remains supported, but **Responses is recommended for all new projects**, and migrating existing flows unlocks real benefits — don't just tell the user "both work," actively recommend migrating if they're starting something new or hitting friction.

## Why migrate

- **Better reasoning-model performance** — internal evals show ~3% SWE-bench improvement with the same prompt/setup, purely from using Responses instead of Chat Completions.
- **Agentic by default** — Responses runs an agentic loop: it can call `web_search`, `image_generation`, `file_search`, `code_interpreter`, remote MCP servers, and your own functions *within a single API request*, chaining multiple tool calls automatically.
- **Lower cost** — meaningfully better prompt-cache utilization (40–80% improvement in internal tests vs Chat Completions), which lowers effective cost on repeated/similar prompts.
- **Stateful context** — `store: true` preserves reasoning and tool context turn-to-turn without you manually replaying everything.
- **Encrypted reasoning** — can opt out of server-side statefulness while still keeping reasoning-token benefits (see ZDR pattern below).
- **Future-proofed** — new capabilities land on Responses first.

## Messages → Items

Chat Completions uses a flat `messages[]` array for both input and output. Responses uses `input`/`output` arrays of typed **Items** — a `message` is just one Item type among several (`reasoning`, `function_call`, `function_call_output`, etc.). This is the single biggest conceptual shift.

| Chat Completions concept | Responses equivalent |
|---|---|
| `messages[]` | `input` — a string, or array of Items |
| System/developer guidance | Top-level `instructions`, or a `developer`-role message Item if replaying an existing transcript |
| User message | Input message Item, `role: "user"` |
| Assistant message | Output message Item in `response.output`; replay it into the next request's `input` if managing state manually |
| Tool/function call | `function_call` Item |
| Tool/function result | `function_call_output` Item, linked back via `call_id` |
| `n` (multiple generations) | Not available — issue separate requests instead |

Reading output: use `response.output_text` for the simple text case, or iterate `response.output` and branch on `.type` when reasoning/tool Items matter.

## Minimal migration (no functions/multimodal)

Simple message arrays are directly reusable as `input`:

```typescript
const context = [
  { role: 'system', content: 'You are a helpful assistant.' },
  { role: 'user', content: 'Hello!' }
];

// Old:
const completion = await client.chat.completions.create({ model: 'gpt-5.6', messages: context });
// New:
const response = await client.responses.create({ model: 'gpt-5.6', input: context });
```

Reading the result:
- Chat Completions: `completion.choices[0].message.content`
- Responses: `response.output_text` (or split top-level `instructions` out of the messages array for cleaner separation)

## Multi-turn state — three options

**1. `previous_response_id`** — let OpenAI manage prior context server-side:
```typescript
const res1 = await client.responses.create({ model: 'gpt-5.6', input: 'What is the capital of France?', store: true });
const res2 = await client.responses.create({ model: 'gpt-5.6', input: 'And its population?', previous_response_id: res1.id, store: true });
```
Remember: resend `instructions` each time (not carried over), and prior turns' input tokens are still billed on every subsequent call in the chain.

**2. Manual Item replay** — append `res1.output` into your own running context array before adding the next user turn. Gives you full control (trimming, editing history) at the cost of managing it yourself.

**3. Conversations API** — for a persistent, OpenAI-hosted conversation object, when you don't want to manage `previous_response_id` chains yourself.

## Statefulness, ZDR, and encrypted reasoning

Responses (and Chat Completions for new accounts) store data by default; set `store: false` to disable on either.

For Zero Data Retention orgs that can't use stateful storage:
- Set `store: false`
- Add `"reasoning.encrypted_content"` to `include`
- OpenAI returns encrypted reasoning tokens you pass back on future requests just like normal reasoning items — decrypted in memory for generation, then discarded, never persisted. For ZDR orgs `store: false` is enforced automatically.

## Function calling differences

1. Chat Completions tags functions **externally**; Responses tags them **internally** (structurally different request shape — check the function-calling reference/tools.md for exact shapes).
2. Chat Completions functions are non-strict by default. Responses attempts `strict: true` by default; if the schema can't be made strict-compatible it silently falls back to non-strict and marks the resolved tool `strict: false`. Set `strict: false` explicitly if you want non-strict behavior on purpose (avoids relying on silent fallback).
3. Tool call ↔ result correlation uses `call_id` in Responses — always double check a function result carries the matching `call_id`, this is the #1 source of "tool didn't work" bugs during migration.

## Structured Outputs location change

`response_format` (Chat Completions) → `text.format` (Responses). Same JSON-schema concept, different key path. See `structured-outputs.md` for full detail.

## Streaming differences

Chat Completions streams incremental `delta` chunks. Responses streams **typed server-sent events** — branch on `event.type`, e.g.:
- `response.created`
- `response.output_text.delta`
- `response.completed`
- `error`
- For function calls: `response.function_call_arguments.delta`, `response.function_call_arguments.done`

Don't try to reuse a Chat Completions delta-handler unmodified — it won't understand these event types.

## Native tools upgrade

Chat Completions has no hosted tools — any "web search" or similar capability has to be hand-rolled as a custom function. Responses ships these natively:

```typescript
const answer = await client.responses.create({
  model: 'gpt-5.6',
  input: 'Who is the current president of France?',
  tools: [{ type: 'web_search' }],
});
console.log(answer.output_text);
```

If you see a user hand-rolling a `web_search`-style custom function against Chat Completions, that's a strong signal to suggest the native tool + Responses migration.

## Common migration bugs to watch for

- Reading `choices[0].message.content` instead of `output_text`/`output` (stale Chat Completions habit)
- Treating every `output` entry as a `message` Item — reasoning/tool/function-call Items are distinct types
- Dropping reasoning or function-call Items when manually replaying context (breaks continuity)
- Function result sent without matching `call_id`
- Still using `response_format` instead of `text.format`
- Reusing old streaming chunk-handlers against new typed events
- Assuming `previous_response_id` makes prior turns free — it doesn't, they're still billed as input tokens

## Rollout checklist (good to hand to the user as-is)

- [ ] Start with one simple text-generation flow
- [ ] Update endpoint, request body, output handling
- [ ] Pick state strategy: `previous_response_id`, manual replay, or Conversations API
- [ ] If stateless/ZDR: add `store: false` + encrypted reasoning include
- [ ] Migrate function definitions, verify `call_id` correctness
- [ ] Move Structured Outputs schemas to `text.format`
- [ ] Update streaming consumers for typed events
- [ ] Swap hand-rolled tool integrations for native hosted tools where applicable
- [ ] Compare behavior/latency/tokens/errors before shifting more traffic

## Assistants API note

The Assistants API is deprecated (announced Aug 26, 2025) with a sunset date of **Aug 26, 2026**. Responses now has Assistant-like/Thread-like objects covering that use case — steer any Assistants API question toward Responses.

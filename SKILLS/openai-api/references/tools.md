# Tools (Responses API)

Responses runs an agentic loop — the model can call built-in tools, your own functions, or remote MCP servers, and chain multiple tool calls within a single request. Only `gpt-5.4`+ supports `tool_search`.

## Available tools at a glance

| Tool | Purpose |
|---|---|
| Function calling | Call your own custom code for data/capabilities the model doesn't have |
| Web search | Pull in current internet data during generation |
| Remote MCP | Give the model capabilities exposed via Model Context Protocol servers |
| Skills | Upload/reuse versioned skill bundles in hosted shell environments |
| Shell | Run shell commands in a hosted container or your own local runtime |
| Computer use | Agentic control of a computer interface |
| Image generation | Generate/edit images with GPT Image, inline in the agentic loop |
| File search | Search uploaded file contents for context |
| Tool search | Dynamically load tool definitions at runtime to save context/tokens (gpt-5.4+ only) |
| Programmatic tool calling | Let the model compose/run JavaScript that orchestrates other tool calls |

You typically enable a tool by adding a config object to the `tools` array on `responses.create`. The model decides on its own whether to invoke a tool based on the prompt (e.g. it'll reach for `web_search` if you ask about something past its knowledge and that tool is enabled). Use `tool_choice` to force/guide this explicitly if needed.

## File search

```python
response = client.responses.create(
    model="gpt-5.6",
    input="What is deep research by OpenAI?",
    tools=[{"type": "file_search", "vector_store_ids": ["<vector_store_id>"]}],
)
```
Same shape in JS (`tools: [{ type: "file_search", vector_store_ids: [...] }]`).

## Tool search (deferred tool loading)

Use when you have many function tools and don't want to pay context/token cost for all of them up front. Mark tools you want deferred with `defer_loading: true` inside a `namespace`-typed tool group, and add `{"type": "tool_search"}` to `tools`. The model loads the relevant deferred tool definitions at runtime instead of having them all resident in context.

```python
crm_namespace = {
    "type": "namespace",
    "name": "crm",
    "description": "CRM tools for customer lookup and order management.",
    "tools": [
        {
            "type": "function",
            "name": "get_customer_profile",
            "description": "Fetch a customer profile by customer ID.",
            "parameters": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"], "additionalProperties": False},
        },
        {
            "type": "function",
            "name": "list_open_orders",
            "description": "List open orders for a customer ID.",
            "defer_loading": True,
            "parameters": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"], "additionalProperties": False},
        },
    ],
}

response = client.responses.create(
    model="gpt-5.6",
    input="List open orders for customer CUST-12345.",
    tools=[crm_namespace, {"type": "tool_search"}],
    parallel_tool_calls=False,
)
```

Only available on `gpt-5.4` and later — check the target model before suggesting this pattern.

## Remote MCP

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.6",
    "tools": [{
      "type": "mcp",
      "server_label": "dmcp",
      "server_description": "A Dungeons and Dragons MCP server to assist with dice rolling.",
      "server_url": "https://dmcp-server.deno.dev/sse",
      "require_approval": "never"
    }],
    "input": "Roll 2d4+1"
  }'
```
Same object shape in JS/Python `tools` arrays. `require_approval` controls whether tool calls need human sign-off before executing — set to `"never"` only when you trust the server and the action space is safe.

## Function calling — best practices

- Prefer strict-schema functions where possible (Responses attempts `strict: true` by default and falls back silently to `strict: false` if the schema can't be made strict-compatible — check the resolved tool if you need to confirm which mode you actually got).
- Tool calls and their results are two separate Item types, correlated by `call_id` — always make sure a `function_call_output` carries the matching `call_id` from its `function_call`.
- In Chat Completions, function defs are non-strict by default and externally tagged; in Responses they're internally tagged and strict-by-default-with-fallback. Don't port one shape directly into the other API.

## Agents SDK wiring (higher-level than raw Responses calls)

Wrap local logic as a function tool:
```typescript
import { tool } from "@openai/agents";
import { z } from "zod";

const getWeatherTool = tool({
  name: "get_weather",
  description: "Get the weather for a given city.",
  parameters: z.object({ city: z.string() }),
  async execute({ city }) { return `The weather in ${city} is sunny.`; },
});
```

Expose a whole specialist agent as a tool for a manager agent to call:
```typescript
const summarizer = new Agent({ name: "Summarizer", instructions: "Generate a concise summary of the supplied text." });
const mainAgent = new Agent({
  name: "Research assistant",
  tools: [summarizer.asTool({ toolName: "summarize_text", toolDescription: "Generate a concise summary of the supplied text." })],
});
```

Decision guide: attach tools directly on an agent when one specialist should own them; expose a specialist *as* a tool when a manager agent should stay in control of the user-facing reply; keep shell/apply-patch/computer-use harnesses in your own runtime even when the SDK models the tool decision.

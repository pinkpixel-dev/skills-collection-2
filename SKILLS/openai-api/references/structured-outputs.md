# Structured Outputs

Guarantees model output matches a JSON Schema you supply — no missing required keys, no hallucinated enum values.

Benefits: reliable type-safety (no validate/retry loop needed), programmatically detectable safety refusals (`refusal` field), simpler prompting (no need to beg the model to format things correctly).

SDK helpers: Python via Pydantic, JavaScript via Zod — both let you define the schema as native types instead of hand-writing raw JSON Schema.

## Two forms

1. **Via function calling** — when connecting the model to tools/functions/data in your system.
2. **Via `text.format` (Responses) / `response_format` (Chat Completions)** — when you want the model's *reply to the user* to follow a schema (e.g. so your UI can render distinct fields).

Simple rule: tools/functions/system integration → function calling. Structuring the user-facing response → `text.format`.

## `text.format` shape (Responses API)

```typescript
const response = await client.responses.create({
  model: "gpt-5.6",
  input: "Jane, 54 years old",
  text: {
    format: {
      type: "json_schema",
      name: "person",
      strict: true,
      schema: {
        type: "object",
        properties: {
          name: { type: "string", minLength: 1 },
          age: { type: "number", minimum: 0, maximum: 130 },
        },
        required: ["name", "age"],
        additionalProperties: false,
      },
    },
  },
});
```

```python
response = client.responses.create(
    model="gpt-5.6",
    input="Jane, 54 years old",
    text={"format": {
        "type": "json_schema",
        "name": "person",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "number", "minimum": 0, "maximum": 130},
            },
            "required": ["name", "age"],
            "additionalProperties": False,
        },
    }},
)
```

**Migration note**: Chat Completions uses `response_format: { type: "json_schema", json_schema: { name, strict, schema } }` — same concept, nested one level differently, and the key is `response_format` not `text.format`. Don't paste Chat Completions shape into a Responses call or vice versa.

## Model support

Available starting with GPT-4o-class models. For new projects, just default to the current flagship (e.g. `gpt-5.6`). Older models (`gpt-4-turbo` and earlier) can't do Structured Outputs — fall back to JSON mode for those.

## Structured Outputs vs JSON mode

| | Structured Outputs | JSON mode |
|---|---|---|
| Valid JSON | Yes | Yes |
| Schema adherence | Yes | No |
| Enabling | `text: { format: { type: "json_schema", strict: true, schema: ... } }` | `text: { format: { type: "json_object" } }` |

Always prefer Structured Outputs over JSON mode when the model supports it — JSON mode only guarantees parseable JSON, not that it matches your shape.

**JSON mode gotchas**: you must explicitly instruct the model to produce JSON somewhere in the conversation — literally the string "JSON" needs to appear in context, or the API throws an error (this exists specifically to stop the model from streaming endless whitespace trying to hit a JSON object it was never told to produce). Also: no schema guarantee, so still validate + consider retry logic, and handle incomplete/malformed JSON as an application-level edge case.

## Handling refusals

Safety-based refusals can happen even with Structured Outputs in play. A refusal won't necessarily match your schema — the API instead populates a `refusal` field on the output object. Check for `refusal` before assuming your schema fields are populated, and branch your UI/logic accordingly.

## Handling user-generated input

If input is user-generated, explicitly instruct the model (in your prompt) how to handle input that can't map cleanly to the schema — e.g. "return empty fields if the input doesn't fit," otherwise the model may hallucinate values just to satisfy the schema when given unrelated input.

## Best practices

- Use native Pydantic (Python)/Zod (JS) support rather than hand-writing JSON Schema, to avoid schema/type drift. If schemas must be hand-written, add CI checks that flag edits to one without the other (or auto-generate one from the other).
- If output quality is off even with a valid schema, iterate on instructions/examples or split the task into simpler subtasks — Structured Outputs guarantees *shape*, not *correctness*.

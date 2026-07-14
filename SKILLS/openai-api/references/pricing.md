# Pricing

**Always caveat pricing answers**: OpenAI ships new model snapshots and price changes frequently. Use the numbers below as of this skill's source docs to reason about *relative* cost (cheap vs flagship vs reasoning-heavy), but tell the user to confirm exact current numbers at OpenAI's pricing page before finalizing budget-sensitive decisions.

## Pricing tiers

| Tier | What it means |
|---|---|
| **Standard** | Normal synchronous API pricing |
| **Batch** | ~50% cheaper than Standard; submit jobs for async processing, get results within a completion window — great for non-latency-sensitive bulk work |
| **Flex** | Discounted, best-effort processing — slower/less guaranteed than Standard, cheaper for latency-tolerant workloads |
| **Priority** | Premium pricing for guaranteed low-latency/high-throughput processing |

All are priced per 1M tokens, split into input / cached-input / output (some rows also show a batch-equivalent output number).

## Relative cost shape (flagship family, standard tier)

Using the source doc's flagship-family numbers as a *relative* reference (input / cached-input / output, $ per 1M tokens):

| Model | Input | Cached input | Output |
|---|---|---|---|
| `gpt-5.6-sol` (top-tier flagship) | 5.00 | 0.50 | 30.00 |
| `gpt-5.6-terra` (mid) | 2.50 | 0.25 | 15.00 |
| `gpt-5.6-luna` (small/cheap) | 1.00 | 0.10 | 6.00 |

Pattern to remember: within a model family, the smaller/cheaper variant is typically **~2–5x cheaper** on input and output than the flagship, and cached input is consistently a small fraction (often ~10%) of fresh input cost — so prompt caching matters a lot for repeated-context workloads (this is also one of the concrete benefits of moving to the Responses API, which gets meaningfully better cache utilization than Chat Completions).

Reasoning/pro variants (e.g. `-pro` suffixed models) cost substantially more per token than their non-reasoning counterparts — expect several multiples of the base model's price, reflecting heavier compute per response.

Batch tier is consistently ~50% off Standard input/output pricing for the same model, across the whole lineup.

## Other billed components

- **Web search tool calls**: billed per call (roughly $10–25 per 1,000 calls depending on model class), *plus* search-result content tokens billed at the underlying model's normal token rates.
- **Hosted Shell / Code Interpreter containers**: billed per session (typically a 5-minute minimum), scaling with container memory size (small containers are fractions of a cent per session; large ones scale up from there).
- **File search**: storage billed per GB-day (first GB usually free), plus a per-call charge for each tool invocation.
- **Embeddings**: input-token priced, no output cost — meaningfully cheaper than generative calls, `-large` embedding models cost more per token than `-small`.
- **Moderation endpoint**: typically free.
- **Deep research models**: priced at a premium over standard equivalents, reflecting heavier multi-step tool use per request.
- **Regional data-residency endpoints**: expect a flat uplift (around 10%) over standard regional pricing for eligible newer models.

## Fine-tuning note

OpenAI has been winding down its self-serve fine-tuning platform — check current docs before assuming a model is fine-tunable via the API; existing fine-tuned models typically remain available for inference until their base model is deprecated, but new fine-tuning jobs may not be available for all models going forward.

## When the user asks "which model should I use"

Ask (or infer from context): latency sensitivity, cost sensitivity, whether reasoning depth matters, whether it's bulk/async (→ Batch tier) or interactive (→ Standard/Priority). Default recommendation for a new project needing a good cost/capability balance: the mid-tier flagship variant on Standard tier, moving to Batch tier if the workload is bulk and not latency-sensitive.

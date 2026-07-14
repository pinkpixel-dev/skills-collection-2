# Audio & Speech

## Vocabulary

| Modality | Meaning | Common uses |
|---|---|---|
| Audio input | Model receives sound | Voice agents, transcription, translation |
| Audio output | Model/API returns spoken audio | Voice agents, TTS, spoken responses |
| Text transcript | Speech → text | Captions, call analysis, search, records |
| Text prompt | Text controls speech output | Speech generation, scripted voice flows |

## Task types

- **Speech to text**: captions, notes, transcripts, search, accessibility. File-based or streaming.
- **Text to speech**: narration, assistants, accessibility, generated voice. Can stream audio as it's produced.
- **Speech to speech**: one low-latency session that listens, reasons, and speaks — for conversational voice agents that need to respond/call tools/hold session state.
- **Speech translation**: listens in one language, returns translated speech/transcript in another — use a realtime translation session for continuous translation as audio arrives.

## Architecture choice

| Architecture | Use when | Examples |
|---|---|---|
| Request-based audio APIs | You have a file, text input, or bounded request | speech-to-text, text-to-speech |
| Realtime sessions | Audio is live, need low-latency events | voice agents, realtime translation, realtime transcription |
| Multimodal chat completions | Extending an existing chat flow with audio | audio in/out bolted onto Chat Completions |

Streaming = client/service exchange partial input/output while still active — needed for live captions, calls, voice agents, translation. Request-based APIs are simpler for files/non-interactive work but can't do live back-and-forth the same way.

## Realtime voice agent (browser, WebRTC)

Natively multimodal models like `gpt-realtime-2.1` handle audio+text in and out directly. For browser speech-to-speech, use the JS Agents SDK realtime session (WebRTC connects from the client):

```javascript
import { RealtimeAgent, RealtimeSession } from "@openai/agents/realtime";

const agent = new RealtimeAgent({
  name: "Assistant",
  instructions: "You are a helpful voice assistant.",
});

const session = new RealtimeSession(agent, { model: "gpt-realtime-2.1" });
await session.connect({ apiKey: "ek_...(ephemeral key from your server)" });
```

For Python-based chained voice pipelines (not browser-direct), that's a separate voice-agents pattern — direct the user to the voice agents guide rather than trying to force WebRTC-style code into Python.

## Adding audio to an existing Chat Completions app

The Responses API docs currently describe text/image input with text output only — **for the audio-in-chat pattern, use Chat Completions** with an audio-capable model like `gpt-audio-1.5`, setting `modalities: ["text", "audio"]`.

**Audio output from model:**
```typescript
const response = await openai.chat.completions.create({
  model: "gpt-audio-1.5",
  modalities: ["text", "audio"],
  audio: { voice: "alloy", format: "wav" },
  messages: [{ role: "user", content: "Is a golden retriever a good family dog?" }],
  store: true,
});

fs.writeFileSync("dog.wav", Buffer.from(response.choices[0].message.audio.data, "base64"));
```

**Audio input to model:**
```typescript
const response = await openai.chat.completions.create({
  model: "gpt-audio-1.5",
  modalities: ["text", "audio"],
  audio: { voice: "alloy", format: "wav" },
  messages: [{
    role: "user",
    content: [
      { type: "text", text: "What is in this recording?" },
      { type: "input_audio", input_audio: { data: base64str, format: "wav" } },
    ],
  }],
  store: true,
});
```

Fetch/base64-encode the audio file first (`arrayBuffer()` → `Buffer.from(...).toString("base64")` in JS, `base64.b64encode(...)` in Python).

## Gotchas

- Don't try to force the audio-in-chat pattern onto the Responses API — it's not documented there; use Chat Completions for this specific case.
- Browser voice agents are WebRTC and inherently client-side JS — don't try to replicate that flow in a Python backend; use the chained voice pipeline pattern instead for Python.
- Realtime sessions need an **ephemeral key** from your server (not your raw API key) for client-side connection — never ship a raw `OPENAI_API_KEY` to the browser.

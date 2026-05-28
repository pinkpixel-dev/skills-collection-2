# Pollinations CLI — `polli`

Package: `@pollinations_ai/cli`  
The `polli` CLI is for humans, AI agents, and everything in between.

---

## Installation & Auth

```bash
# One-time run (no install)
npx @pollinations_ai/cli gen image "a cat in space" --output cat.png

# Install globally
npm install -g @pollinations_ai/cli

# Login (device flow via enter.pollinations.ai)
polli auth login

# Or pipe in a key
printf '%s' "$POLLINATIONS_API_KEY" | polli auth login --with-token
```

Credentials stored at `~/.pollinations/credentials.json`.

For one-off runs: `--key sk_...` or `POLLINATIONS_API_KEY` env var.

---

## Agent-Friendly Design

Every command is designed for AI agent use:
- `--json` flag → structured stdout, human messages to stderr, safe to parse
- Exit code `0` on success, non-zero on error
- When out of pollen, first line of error is the top-up link
- `polli auth status --json` exposes full session info

**For AI coding agents** (Claude Code, Cursor, Windsurf, Codex):
```
Read https://raw.githubusercontent.com/pollinations/pollinations/main/packages/polli-cli/SKILL.md
and follow the instructions to generate media with the `polli` CLI.
```

Skill also available at: `node_modules/@pollinations_ai/cli/SKILL.md`

---

## Generate Commands

### Text

```bash
# Basic generation
polli gen text "Explain quantum tunneling in one sentence"

# Stdin as context
polli gen text "Summarize this" < notes.md
echo "context" | polli gen text "question"

# Interactive multi-turn chat
polli gen chat --model openai
```

### Image

```bash
# Basic
polli gen image "cyberpunk city at night" --model flux --output city.png

# Image-to-image
polli gen image "enhance this" --image https://media.pollinations.ai/abc --model gptimage

# Without --output: picks a sensible default filename
polli gen image "a forest"
```

### Audio

```bash
# TTS
polli gen audio "Hello world" --voice nova --output speech.mp3

# Play back immediately (blocks until done)
polli gen audio "read it to me" --play

# Transcription
polli gen transcribe speech.mp3
```

### Video

```bash
polli gen video "a waterfall in slow motion" --duration 5 --output clip.mp4
```

---

## Discover Commands

```bash
# All models
polli models

# Filter by type
polli models --type image
polli models --type text
polli models --type audio

# Health + performance stats (last 60m)
polli models --stats

# Full API reference in terminal
polli docs

# One endpoint
polli docs /image

# Open in browser
polli docs --open
```

---

## Account & Key Management

```bash
# Balance
polli usage

# Recent requests
polli usage --history

# Daily spend
polli usage --daily

# List keys
polli keys list

# Create secret key (default)
polli keys create --name mybot --budget 100

# Create publishable key (frontend-safe)
polli keys create --name myapp --type publishable

# Create publishable app key with BYOP + earnings
polli keys create --name myapp --type publishable \
  --redirect-uri https://myapp.com/callback --earnings

# Revoke a key
polli keys revoke <id>
```

> Keys can't be edited — to change name, budget, or model list: revoke and recreate.  
> Publishable app keys default earnings off; add `--earnings` to enable.

---

## Auth Commands

```bash
polli auth login
polli auth status
polli auth status --json    # full session details
polli auth logout
```

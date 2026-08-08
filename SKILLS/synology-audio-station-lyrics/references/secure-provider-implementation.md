# Secure provider implementation

## Provider due diligence

- Confirm a current supported API endpoint; the guide's LyricWiki example is historical.
- Review terms, lyrics licensing, attribution, geographic restrictions, quotas, and authentication.
- Do not scrape a site whose terms or technical controls prohibit it.
- Keep API credentials outside the `.aum` where possible; the historical format does not define secret storage.

## HTTP controls

- Allowlist HTTPS scheme and exact host.
- Verify certificates and hostnames.
- Set connect and total timeouts.
- Limit redirects and revalidate each destination host.
- Cap response body size before parsing.
- Require expected status and content type.
- Encode artist/title with URL/query functions, never string concatenation.
- Apply bounded retry/backoff only to safe requests.

## Parsing controls

- Treat missing, null, reordered, or type-invalid fields as provider failure.
- Limit result count, field length, and total lyric length.
- Normalize UTF-8 and line endings; reject invalid encoding/control sequences.
- Convert allowed markup to plain text with a parser, not regex-only tag stripping.
- Do not execute provider content, templates, PHP, or shell snippets.

## Identifier design

Prefer a compact provider-owned ID. If more context is needed, encode a small signed/validated structure without secrets. Do not accept a raw arbitrary URL from the UI callback. Reconstruct URLs from a validated ID and fixed provider origin.

## Tests

- Exact artist/title and Unicode/diacritics.
- No result.
- Multiple results and previews.
- Malformed JSON/HTML.
- Wrong content type, oversized body, timeout, TLS failure, redirect.
- Rate limit and 5xx response.
- Invalid/malicious ID.
- HTML/script/control characters in lyrics.
- Provider schema evolution.
- Audio Station callback throwing/rejecting data.

Use fixtures and a local mock HTTP server. Do not depend on a live commercial provider for deterministic tests.

## Installation verification

1. Inspect archive members and source.
2. Record SHA-256.
3. Install via Audio Station Settings > Lyrics Plugin > Add only when authorized.
4. Confirm plugin identity/version in UI.
5. Test a known licensed query and no-result case.
6. Review NAS/application logs for PHP errors without exposing content/secrets.
7. Remove only the test plugin through supported UI if cleanup is authorized; do not delete Audio Station data.

---
name: synology-audio-station-lyrics
description: Design, scaffold, validate, package, audit, and troubleshoot third-party Synology Audio Station lyrics modules in .aum format. Use for INFO JSON manifests, lyric.php classes, getLyricsList/getLyrics contracts, addTrackInfoToList/addLyrics calls, external lyrics-provider HTTP parsing, secure PHP runtime constraints, tar.gz packaging, installation testing, and migration of legacy Audio Station 5.0 lyrics plugins.
---

# Audio Station lyrics modules

Build `.aum` lyrics modules from the bundled 2013 guide while recognizing that Audio Station/package/PHP/provider compatibility may have changed substantially.

## Safety and compatibility boundary

- Verify Audio Station is installed, its live version supports third-party lyrics modules, and the UI still offers Lyrics Plugin installation before building for deployment.
- Treat every `.aum` and remote lyrics response as untrusted input.
- Never install a module on the live NAS before inspecting its archive members and PHP source.
- Do not include credentials, cookies, API keys, personal listening data, or copyrighted bulk lyrics in the module archive.
- Confirm the lyrics provider's current API, terms, licensing, attribution, rate limits, and robots/access rules before implementation.
- Use HTTPS with certificate verification and strict timeouts. The 2013 skeleton omits real transport logic and is not production code.
- Expect runtime as low-privilege `nobody` with shared-folder and system-configuration access restricted, as documented.
- Avoid shell execution, dynamic includes, unsafe deserialization, arbitrary file writes, and redirects to untrusted hosts.

## Read references selectively

- Read [references/module-format.md](references/module-format.md) for `.aum`, INFO keys, mandatory PHP class methods, Audio Station callback methods, and packaging.
- Read [references/secure-provider-implementation.md](references/secure-provider-implementation.md) for HTTP, parsing, identifiers, lyrics handling, rate limits, testing, and compatibility.
- Read [references/source-notes.md](references/source-notes.md) for provenance and guide age.
- Consult [assets/AS_Guide.pdf](assets/AS_Guide.pdf) for exact historical examples.
- Use [scripts/aum_tool.py](scripts/aum_tool.py) to scaffold, statically validate, and reproducibly build a minimal module. Review generated PHP before use.

## Required workflow

1. Verify live Audio Station `.aum` support and installed PHP/runtime constraints.
2. Define provider API, authorization, licensing, attribution, timeout, rate-limit, and expected response schema.
3. Choose globally unique manifest `name` and PHP `class`; avoid collisions with installed modules.
4. Create UTF-8 `INFO` JSON with required fields and a PHP module containing the two mandatory methods.
5. Implement strict URL construction, HTTPS allowlisting, timeouts, bounded body size, status/content-type checks, and defensive parsing.
6. Add search candidates through `addTrackInfoToList`; use a stable opaque ID or allowlisted provider URL.
7. Resolve the selected ID in `getLyrics`, normalize human-readable text safely, and call `addLyrics` once.
8. Validate manifest/source/archive structure and inspect archive member paths before installation.
9. Test against fixtures and a mock provider, including no-result, malformed data, timeouts, rate limits, Unicode, and provider errors.
10. Build `.aum`, record checksum, install manually through Audio Station only after review, and verify search/retrieval without exposing NAS data.

## Module contract

An `.aum` is a gzip-compressed tar archive containing at least:

```text
INFO
lyric.php
```

`INFO` is UTF-8 JSON. Required historical keys: `name`, `displayname`, `version`, `module`, `type`, and `class`; `description` is recommended. The guide's prose says module type support is lyrics; its sample shows `"type":"lyric"`. Treat this discrepancy as live-version-sensitive and verify against a known working module/UI before installation.

The manifest class must exist in the configured PHP module and implement:

```php
public function getLyricsList($artist, $title, $info)
public function getLyrics($id, $info)
```

Return the number of results from `getLyricsList`; return Boolean success from `getLyrics`.

## Data-minimization rules

- Send only artist/title necessary for the explicit search.
- Do not transmit DSM account, hostname, filesystem paths, IP, library contents, or unrelated metadata.
- Bound result count and lyric length.
- Avoid recording search terms unless explicitly needed and disclosed.
- Do not cache lyrics to forbidden filesystem paths; assume no shared-folder/system access.

## Completion standard

Report live compatibility evidence, manifest identity/version, provider/security assumptions, static validation, test cases, archive member list and checksum, installation result if authorized, and remaining provider/licensing risks.

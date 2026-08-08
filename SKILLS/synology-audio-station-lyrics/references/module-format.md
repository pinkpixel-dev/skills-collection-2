# Audio Station lyrics module format

## Archive

The guide defines `.aum` as a normal Unix `.tgz`/`.tar.gz` archive. Minimal root members are `INFO` and the PHP module named by the manifest, commonly `lyric.php`. Avoid absolute paths, `..`, symlinks, device files, ownership surprises, and unrelated content.

Historical packaging example:

```sh
tar zcf mymodule.aum INFO lyric.php
```

Prefer reproducible archive metadata and inspect with `tar tzf` before installation.

## INFO manifest

UTF-8 JSON keys:

| Key | Status | Meaning |
|---|---|---|
| `name` | Mandatory | Globally unique module name among Audio Station modules |
| `displayname` | Mandatory | UI label |
| `description` | Recommended | UI description/provider |
| `version` | Mandatory | Module version |
| `module` | Mandatory | PHP filename |
| `type` | Mandatory | Lyrics module type; sample says `lyric`, prose says `lyrics` |
| `class` | Mandatory | Globally unique PHP class name |

Use conservative ASCII identifiers for `name`, `module`, and `class`; use UTF-8 text for display fields. Ensure `module` is a root basename ending in `.php`, not a path.

## Mandatory PHP methods

### `getLyricsList($artist, $title, $info)`

- Receives artist and title strings plus Audio Station's plugin interface object.
- Searches the provider and parses candidates.
- Calls `$info->addTrackInfoToList($artist, $title, $id, $partialLyrics)` for each accepted result.
- Returns the number of successfully added results as an integer.

Use a stable provider identifier as `$id`. If a URL is used, validate scheme/host again in `getLyrics`; never fetch an arbitrary caller-controlled URL.

### `getLyrics($id, $info)`

- Receives the selected ID and plugin interface object.
- Retrieves/parses the full human-readable lyric.
- Calls `$info->addLyrics($lyric, $id)`.
- Returns Boolean success.

Validate ID format and ownership before any request. Return false for missing/invalid content without leaking secrets.

## Audio Station callback methods

### `addTrackInfoToList`

Arguments: artist, title, ID passed later to `getLyrics`, and optional preview/partial lyric.

### `addLyrics`

Arguments: human-readable lyric text and the selected ID.

Normalize provider markup into plain text. Avoid HTML/script injection, control characters, unbounded content, and misleading binary data.

## Runtime

The 2013 guide says modules run as `nobody` with minimal privilege and cannot access shared folders or system configuration directories. Design as stateless network parsing code. Do not attempt to bypass restrictions.

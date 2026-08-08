---
name: tauri-app-builder
description: Build, refactor, debug, harden, and package production-grade Tauri 2 desktop applications. Use for new Tauri apps or existing Tauri projects involving Rust commands and managed state, custom or transparent windows, tray-first utilities, Linux StatusNotifierItem behavior, popup positioning, custom titlebars, close-to-tray lifecycle, single-instance handling, native file dialogs, clipboard access, file drag-and-drop, frontend-to-Rust IPC, capability/CSP security, secrets, local persistence, icons, or Linux DEB/RPM/AppImage delivery.
---

# Tauri App Builder

Build the native behavior as deliberately as the product UI. Treat the webview, Rust core,
operating-system services, and package format as separate trust and lifecycle boundaries.

## Working method

1. Read repository instructions and inspect the entire native surface before editing:
   `src-tauri/Cargo.toml`, Tauri configuration, capabilities, Rust entrypoints, IPC wrappers,
   window hooks, package scripts, tests, and release configuration.
2. Fetch current Tauri documentation with Context7 before relying on API names, plugin setup,
   permissions, or platform support. Tauri and its plugins evolve independently.
3. Identify target platforms and interaction model:
   normal window, menu-bar/tray utility, transient popup, background service, or multi-window app.
4. Write a short lifecycle and trust-boundary design before implementation.
5. Implement narrow vertical slices: native setup, typed IPC, frontend state, lifecycle edge cases,
   then packaging.
6. Run the project audit script and the project's complete lint/test/build gates.
7. Verify the compiled desktop app on every target platform available. Web-only preview is not
   proof of tray, focus, drag/drop, clipboard, transparency, or close-to-tray behavior.

Do not run an existing development server when project instructions reserve that for the user.
Use an already-running app for interactive verification.

## Architecture rules

- Keep privileged behavior in Rust commands. Expose task-specific commands, never a generic shell
  or arbitrary filesystem bridge.
- Keep TypeScript IPC wrappers typed and centralized. Match Rust `serde(rename_all = "camelCase")`
  fields and Tauri invoke argument names exactly.
- Move filesystem, image decoding, keyring, process execution, and potentially blocking clipboard
  work off the async runtime thread with `tauri::async_runtime::spawn_blocking`.
- Store shared native state with `app.manage(...)`; protect mutable state with a suitable lock.
- Use platform application config/data/cache directories through `app.path()`. Do not invent
  dot-directories unless the product explicitly requires them.
- Bound file sizes, record counts, preview dimensions, diagnostic lengths, and cleanup lifetimes.
- Write persistent configuration atomically with a sibling temporary file and rename.
- Keep full binary payloads in Rust when practical; send bounded previews or opaque IDs to the
  webview.
- Validate identifiers and paths again in Rust even when the frontend validates them.
- Preserve operating-system security boundaries: keychain/Secret Service for recoverable secrets,
  native dialogs for user-selected paths, and least-privilege capabilities.

Read [security-and-ipc.md](references/security-and-ipc.md) for any privileged command, secret,
filesystem scope, child process, or persistence work. Read
[native-data-and-background-work.md](references/native-data-and-background-work.md) for files,
images, caches, long-running operations, or managed state.

## Tray and popup decision

Use Tauri's `TrayIconBuilder` first on Windows and macOS. It supports menus and
`show_menu_on_left_click(false)`.

On Linux, make a deliberate choice:

- If the app only needs a context menu, Tauri's tray is sufficient.
- If reliable left-click activation and separate right-click menu behavior are required, use a
  StatusNotifierItem implementation such as `ksni`. Tauri's official documentation currently says
  tray mouse events are unsupported on Linux even though the icon and context menu work.
- Keep a single tray owner. Do not create both Tauri and StatusNotifierItem icons.
- Keep tray callbacks lightweight; emit an app event or update state for expensive work.
- Treat activation coordinates as hints, constrain the popup to the selected monitor, then show and
  focus it.

Read [tray-and-popup.md](references/tray-and-popup.md) completely for tray-first or menu-bar apps.

## Popup window contract

For a compact tray popup, start hidden and normally use:

- `decorations: false`
- `transparent: true` only when shaped/rounded edges are required
- `visible: false`
- `alwaysOnTop: true` when the product expects a popover
- `skipTaskbar: true`
- explicit width, height, and useful minimums
- disabled minimize/maximize when those states make no sense
- `dragDropEnabled: true` when accepting native file drops

Clip and round every layer: `html`, `body`, `#root`, and the visible shell. Keep the document
background transparent and avoid webview shadows bleeding beyond the rounded shell. Native shadow
support is platform-dependent; Linux does not honor Tauri's window `shadow` setting.

Apply `data-tauri-drag-region` only to elements that should drag. The attribute is not inherited,
which protects child buttons. Use `startDragging()` only for custom gesture logic.

Read [window-lifecycle-and-input.md](references/window-lifecycle-and-input.md) before implementing
custom chrome, auto-hide, Escape behavior, native dialogs, clipboard, or file drag/drop.

## Lifecycle contract

- Register the single-instance plugin first. On a second launch, show and focus the existing window.
- Distinguish **hide**, **close**, and **exit**:
  - window close requests may be prevented and converted to hide;
  - normal application exit requests may be prevented for a tray-resident app;
  - an explicit Quit menu item must call `app.exit(...)`;
  - final `RunEvent::Exit` must shut down background services and clean cache state.
- Hide on blur only after a short delay and only when no native interaction owns focus.
- Suppress auto-hide during file drags, native dialogs, clipboard operations that open UI, and the
  brief focus transition after showing the window.
- Do not confuse a transient loss of focus with user intent to close the popup.

## Native file drag contract

Tauri drag/drop emits `enter`, `over`, `drop`, and `leave`. Start the protected drag session on
**both `enter` and `over`**. Handling only `over` creates a race where the initial `enter` can let
hide-on-blur close the window.

On `drop`, keep suppression active until the path has been imported, refocus the window, then release
suppression after a short grace period. On `leave`, release after a grace period. Clear timers and
unlisten on teardown. Add a regression test for the exact four-event classification.

## Security baseline

- Use a strict CSP; begin with bundled content and IPC only, then add the smallest required image,
  font, or network sources.
- Scope capabilities to exact window or webview labels. Avoid remote webview capabilities unless
  the threat model explicitly requires them.
- Grant only APIs used by the frontend. Rust code is not protected from itself by capabilities.
- Never disable TLS validation, SSH host-key checks, code signing checks, or equivalent security to
  make setup easier.
- Never place secrets in process arguments, logs, profile JSON, temporary scripts, or durable
  environment configuration.
- Be honest: recoverable credentials cannot be "impossible to decrypt." Their boundary is the
  unlocked operating-system account and credential vault.

## Icons and themes

- Generate the standard application iconset with `tauri icon` from a large square source, then
  inspect small sizes manually. Small tray icons often need a simpler dedicated mark.
- Preserve transparency and padding; do not use a detailed marketing logo at 16–24 px.
- Provide high-contrast light and dark artwork where the desktop cannot recolor the icon.
- StatusNotifierItem `IconPixmap` is ARGB32. When starting from RGBA bytes on little-endian Linux,
  convert to the byte order expected by the tray library; verify visually rather than assuming.
- Keep tray icon, package icon, window favicon, and in-app logo roles separate.

Read [configuration-icons-packaging.md](references/configuration-icons-packaging.md) for current
configuration, icon, Linux runtime, and release guidance.

## Verification gate

Run:

```bash
python3 ~/.codex/skills/tauri-app-builder/scripts/audit_tauri_project.py .
```

Then run the repository's full checks. For Rust, require formatting, Clippy with warnings denied, and
tests. For the frontend, require lint, typecheck, tests, and production build.

Interactively verify the native build:

- left and right tray clicks;
- second-instance activation;
- show, focus, blur, Escape, close, explicit Quit, and restart;
- popup placement at every screen edge and on multiple monitors;
- custom titlebar dragging without breaking controls;
- native dialog open/cancel;
- drag `enter`, repeated `over`, `drop`, and `leave`;
- clipboard success and empty/error cases;
- dark, light, and system theme changes;
- 320 px minimum-width layout with no corner bleed;
- clean console and native logs;
- install/launch/uninstall for each produced bundle.

Read [verification.md](references/verification.md) for the full matrix. Do not claim a native
behavior works when only the browser version was tested.

## Reference routing

- Tray, Linux SNI, menus, positioning: [tray-and-popup.md](references/tray-and-popup.md)
- Focus, hide, close, custom chrome, drag/drop: [window-lifecycle-and-input.md](references/window-lifecycle-and-input.md)
- Capabilities, CSP, commands, secrets: [security-and-ipc.md](references/security-and-ipc.md)
- State, storage, files, previews, blocking work: [native-data-and-background-work.md](references/native-data-and-background-work.md)
- Configuration, plugins, icons, releases: [configuration-icons-packaging.md](references/configuration-icons-packaging.md)
- Native test matrix and debugging: [verification.md](references/verification.md)
- Current upstream evidence and platform caveats: [research-sources.md](references/research-sources.md)

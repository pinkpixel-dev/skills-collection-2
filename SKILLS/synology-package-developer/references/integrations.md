# DSM UI, web, containers, and database integrations

## Contents

- Desktop applications
- Localization and help
- Authentication
- Wizard UI
- Web services and nginx
- Container Manager
- Databases

## Desktop applications

Use `dsmuidir` to identify package UI content and `dsmappname`/launch fields for Package Center integration. DSM creates links into its third-party web UI area.

A desktop app config is JSON with a unique application identity and fields such as:

- `type`
- `icon`
- `title`
- `desc`
- `url`
- `allUsers`
- `preloadTexts`

Security rules:

- Default to administrator-only unless ordinary-user access is intentional and authorized.
- Treat `allUsers: true` as an access-control decision, not presentation.
- Enforce authorization server-side; hiding an icon is not security.
- Use same-origin relative URLs when possible.
- Apply CSP, output escaping, CSRF protections, and safe cookie handling.
- Do not depend on undocumented global UI APIs unless the target DSM and official examples require them.

## Localization and help

Provide localized `texts/LANG/strings` resources. Reference them as `section:key`. Preload strings used in notifications.

Help integration uses a localized content tree plus a TOC configuration. Keep content offline-capable and version-matched. Do not embed external trackers or secrets.

## Authentication

The supplied guide describes `authenticate.cgi` for CGI session checks. Treat this as DSM-version-specific:

- invoke only in the documented CGI environment;
- never trust a returned username without authorization checks;
- never place credentials in query strings;
- use HTTPS;
- protect session cookies;
- avoid logging authentication requests/responses;
- use official WebAPI authentication/version discovery for API clients.

Do not copy guide examples containing `account` and `passwd` URL parameters into production code.

## Wizard UI

Wizard files cover install, upgrade, and uninstall. Values become lifecycle environment variables.

Rules:

- validate all values again in lifecycle scripts;
- never use a checkbox as the sole protection against destructive behavior;
- keep passwords out of logs and generated static files;
- localize labels and recovery warnings;
- supply stable keys;
- test every branch and back/next transition;
- use separate explicit consent for permanent data removal.

DSM 7.2.2 introduced Vue 2.7.14 render-function wizard support. Official examples require an entry returning a name/render pair, `pkg-center-step-content`, and Package Center hook functions such as `getNext`, `checkState`, and `getValues`.

Pin the build dependencies used to compile wizard bundles. Do not assume DSM's embedded Vue version outside the documented release.

## Web services and nginx

Prefer Web Station/resource workers:

- `static`
- `nginx_php`
- `apache_php`
- `reverse_proxy`
- `web-config` for supported static nginx configuration

Define service names, display names, roots, portals, and timeouts explicitly. For PHP:

- choose a supported provider/version;
- minimize extensions;
- restrict `open_basedir`;
- do not enable verbose errors in production;
- run as the package identity/group needed for the web root;
- store writable content outside immutable `target`.

For reverse proxy:

- validate the target;
- preserve the correct `Host` and forwarding headers;
- add WebSocket upgrade headers only when needed;
- set finite connection/read/send timeouts;
- do not create an unauthenticated public admin portal;
- verify DSM custom-domain, alias, and server-portal behavior.

For `web-config`:

- use only supported config types and timing;
- register port/alias resources separately as required;
- request the documented service reload through INFO fields;
- never edit `/etc/nginx` generated files as the package's installation method.

Custom nginx snippets are code. Audit for path traversal, proxy escape, unsafe regex, header injection, directory exposure, and collision.

## Container Manager

### Prefer `docker-project` on DSM 7.2.1+

The worker accepts project names and Compose directories relative to `target`, with optional preload image and build parameters. It creates/updates projects during install, starts/stops them with the package, and deletes projects on release.

Design:

- declare a Container Manager minimum provider version;
- use Compose project names unique to the package;
- pin image tags/digests;
- store Compose definitions in immutable payload;
- place persistent data in explicit package/share locations;
- use named volumes only with a documented retention/export policy;
- bind ports narrowly, preferably LAN/loopback as appropriate;
- define healthchecks and startup ordering;
- avoid privileged containers, host networking, host PID/IPC, device access, and Docker socket;
- supply secrets at runtime, not in Compose;
- test upgrade recreation flags.

Worker project deletion is not proof that data is safe. Inspect actual bind mounts and volumes and verify uninstall retention.

### Legacy Docker worker

The older worker translates a limited JSON service schema into Compose. It supports images/builds, ports, environment, dependencies, package `shares`, and payload-relative `volumes`.

Its examples contain plaintext database passwords and old images. Treat them as syntax demonstrations only. Never reuse those credentials or versions.

## Databases

For MariaDB/PostgreSQL or application databases:

- declare provider dependency and supported major version;
- generate unique random credentials at install time;
- store them in package-private configuration;
- avoid admin/root credentials in SPK resources;
- create least-privileged database users;
- use Unix sockets where appropriate;
- back up with database-native tools before migration;
- test collation, charset, timezone, and restore;
- never automatically delete the database on normal uninstall.

Collision strategies such as replace/skip/error can be destructive. Default to error and provide an explicit migration path. “Replace” means data loss unless a verified backup and explicit authorization exist.

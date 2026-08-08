# Media, retention, physical security, and privacy

## Recordings and snapshots

Before delete/truncate/unlock/bulk filter operations, resolve exact object IDs, camera, owner server, timestamps/time zone, category, lock state, incident/legal hold, retention rule, and export/backup readability. `DeleteAll` and filtered deletion are destructive. Never unlock evidence to bypass retention.

For exports/downloads, use controlled destinations, restrictive permissions, checksums, explicit retention, and secure deletion policy. Do not write sensitive media into source repositories or broadly readable temporary directories.

## Streams and live view

Stream URLs and SIDs are bearer secrets. Keep them in memory, restrict origin/referrer/logging, bound duration and bandwidth, and close connections. Do not expose raw DSM stream URLs to untrusted browsers or public pages. Use an authenticated proxy only with explicit threat design and capacity limits.

## Cameras, PTZ, doors, and outputs

Camera enable/disable and PTZ changes affect monitoring coverage and physical movement. Door controls, digital outputs, and external events can cause real-world actions. Require exact device/operation authorization, rate limits, confirmation for high-impact commands, and independent state verification.

`FormatSDCard` destroys edge-storage evidence. Require specific camera/card confirmation, backup/retention checks, and explicit permanent-deletion authorization.

## Faces, access cards, transactions, IVA

Face images/templates/results, access-card/cardholder data, transaction data, people counts, and analytics can be biometric or personally identifiable information. Apply data minimization, lawful-purpose/consent policy, access control, encryption, retention limits, auditability, and regional legal review. Do not copy raw values into troubleshooting reports.

Corrections/mark-as-stranger operations alter identity records and require strong authorization and traceability. Bulk resets/deletions can destroy audit evidence.

## Notifications, action rules, and YouTube

Changing schedules/filters/rules can silently suppress alerts. Test using a controlled non-emergency path and verify recipients. Redact SMTP/SMS/push credentials and device tokens.

YouTube Live sends surveillance media to an external service. Treat save/close/publication as an external disclosure requiring explicit destination, account, privacy, duration, and revocation approval.

## Verification matrix

| Change | Independent verification |
|---|---|
| Camera config/state | Fresh `List`/`GetInfo`, expected live snapshot if authorized |
| PTZ/output/door | Fresh device state plus physical/operator confirmation |
| Recording lock/delete/export | Fresh filtered list, exported checksum/readability, unaffected neighbors |
| Notification/rule | Read-back plus controlled test message/event |
| Analytics/face | Fresh task/result/group list with privacy-safe counts |
| Archiving/CMS | Task/status on both source and destination where applicable |

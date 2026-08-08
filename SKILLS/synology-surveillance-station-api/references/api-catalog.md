# API catalog

## Core, cameras, events, and PTZ

- `SYNO.API.Info`: `Query`.
- `SYNO.API.Auth`: `login`, `logout`.
- `SYNO.SurveillanceStation.Info`: `GetInfo` for package/version information.
- `SYNO.SurveillanceStation.Camera`: `Save`, `List`, `GetInfo`, `ListGroup`, `GetSnapshot`, `Enable`, `Disable`, capability/migration/category/size/validation/optimization operations, `Delete`, `GetLiveViewPath`.
- `SYNO.Surveillance.Camera.Event`: enumerate audio/alarm/tampering/motion, save motion/audio/DI/tampering detection parameters, long-poll alarm status.
- `Camera.Group`: enumerate, save, delete camera groups.
- `Camera.Import`: save/import archive cameras and enumerate archives.
- `Camera.Wizard`: quota/SD checks, batch/quick camera creation, `FormatSDCard`.
- `PTZ`: move, zoom, focus, iris, autofocus, absolute PTZ, home, autopan, object tracking, list/go preset, list/run patrol.
- `ExternalRecording`: start/stop external recording through `Record`.

## Recordings, exports, and CMS

- `Recording`: list, count, delete one/filter/all, apply/load advanced filters, truncate, lock/unlock one/filter, download, validate, stream, range export and progress callbacks.
- `Recording.Export`: load/check name/enumerate cameras/check availability/save/get export info.
- `Recording.Mount`: load mounted recording sources.
- `CMS`: redirect, share privileges/options, info/status/sync, Samba checks/enablement, snapshots, notification/locking.
- `CMS.GetDsStatus`: CMS enablement, pair/unpair/login/logout/test/free space/lock.
- `CMS.SlavedsWizard`: save subordinate-server configuration.
- `CMS.SlavedsList`: load subordinate server list.

## Logs, licensing, streams, rules, maps

- `Log`: count, clear, list, get/set logging settings.
- `License`: load and quota checks.
- `Stream`: `EventStream`.
- `ActionRule`: save/list/enable/disable/delete; history listing/download/delete and player data.
- `Emap`: list/load e-maps.
- `Emap.Image`: load map image.

## Notifications and add-ons

- `Notification`: registration token, customized messages, variables, advanced settings.
- `Notification.SMS`: get/set SMS and send test.
- `Notification.PushService`: get/set/test, verification email, mobile-device list/unpair.
- `Notification.Schedule`: get/set camera, alarm, access-control, door, and system-dependent schedules, including batch schedule.
- `Notification.Email`: get/set and test email.
- `Notification.Filter`: get/set filters.
- `Notification.SMS.ServiceProvider`: create/set/list/delete providers.
- `Addons`: list/info/update/enable/disable, progress and auto-update settings.

## Alerts, snapshots, and VisualStation

- `Alert`: enumerate/count/clear/lock/unlock/trigger/flush alerts and recording-server variants.
- `Alert.Setting`: save alert configuration.
- `SnapShot`: existence/validity/lock checks; list/load/take/edit/save/download/lock/unlock/delete and filtered bulk operations; get/save settings.
- `VisualStation`: enumerate, network request/edit, enable/disable, lock/unlock/delete.
- `VisualStation.Layout`: enumerate/save/delete layouts.
- `VisualStation.Search`: start/search IP/stop/get info.

## Access control, external events, and I/O

- `AxisAcsCtrler`: controller/cardholder/door/privilege/log enumeration and counts; photos, retrieve cards, save/configure, enable, alarm acknowledge, test, door control, download/clear logs, block cardholder, delete.
- `AxisAcsCtrler.Search`: start/get info.
- `DigitalOutput`: enumerate/save/poll output state.
- `ExternalEvent`: trigger external event.
- `IOModule`: enumerate devices/ports/vendors, save/enable/disable/delete/test/capabilities/port settings, poll digital inputs/outputs, counts.
- `IOModuleSearch`: start/get info.
- `Camera.Status`: one-time status query.

## PTZ configuration, camera search, and Home Mode

- `PTZ.Preset`: enumerate/get/set/delete/execute presets and set home.
- `PTZ.Patrol`: enumerate/load/save/delete/execute/stop patrols. The guide spells one method `Excute`; use live discovery/spec spelling.
- `Camera.Search`: start and get discovery info.
- `HomeMode`: switch/get info.

## Transactions, archiving, publication, and analytics

- `Transactions.Device`: enumerate transaction devices.
- `Transactions.Transaction`: enumerate, lock/unlock/delete, begin/complete/cancel/append transaction data.
- `Archiving.Pull`: save/login source/delete/list/enable/disable/batch-edit pull-archive tasks and progress.
- `YoutubeLive`: load/save/close external YouTube live publication.
- `IVA`: list/save/delete/enable/disable analytics tasks and reset people counter.
- `IVA.Report`: count/report analytics.
- `IVA.Recording`: list/delete/lock/unlock recordings and retrieve analytics results.
- `IVA.TaskGroup`: list/create/edit/delete/enable/disable groups, people counts/reset.

## Face recognition and bookmarks

- `Face`: list/save/delete/enable/disable/playable tasks; create/delete/edit/list/count face groups; detect image face; create/delete/edit/list/count/search registered faces.
- `Face.Result`: list/delete/lock/unlock results, event/analytics info, correct identity, mark stranger (guide spelling `MarkAsStanger`).
- `Recording.Bookmark`: save/delete/list bookmarks.

## Exact-method lookup

The PDF has 563 extracted page breaks and detailed version/availability, request, response, valid-value, and error tables. For exact work:

```sh
pdftotext -layout assets/Surveillance_Station_Web_API.pdf /tmp/surveillance-api.txt
rg -n '^2\.3\.[0-9]+ .*Face|CreateRegisteredFace method' /tmp/surveillance-api.txt
```

Read only the relevant section and the appendix. Never infer a mutation's parameters from this condensed catalog.

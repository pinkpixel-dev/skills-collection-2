#!/usr/bin/env python3
"""Dependency-free DSM WebAPI authentication reference client.

Import as a library. No CLI is provided so credentials cannot be accidentally
placed in shell history. The client uses SID sessions and POST form bodies.
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping


class DSMAuthError(RuntimeError):
    def __init__(self, message: str, *, code: int | None = None):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ApiDescriptor:
    path: str
    min_version: int
    max_version: int
    request_format: str | None = None


class DSMAuthClient:
    def __init__(self, origin: str, *, timeout: float = 30.0, verify_tls: bool = True):
        parsed = urllib.parse.urlsplit(origin)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.path not in {"", "/"}:
            raise ValueError("origin must contain only scheme, host, and optional port")
        if parsed.scheme != "https" and verify_tls:
            raise ValueError("use HTTPS, or explicitly set verify_tls=False for an isolated lab")
        self.origin = origin.rstrip("/")
        self.timeout = timeout
        self.context = ssl.create_default_context() if verify_tls else ssl._create_unverified_context()
        self.apis: dict[str, ApiDescriptor] = {}
        self.sid: str | None = None
        self.synotoken: str | None = None
        self.did: str | None = None

    def _post(self, path: str, fields: Mapping[str, Any]) -> Any:
        encoded = urllib.parse.urlencode({key: _wire(value) for key, value in fields.items()}).encode()
        url = f"{self.origin}/webapi/{path.lstrip('/')}"
        request = urllib.request.Request(url, data=encoded,
                                         headers={"Content-Type": "application/x-www-form-urlencoded",
                                                  "Accept": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.context) as response:
                raw = response.read(16 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            raise DSMAuthError(f"DSM returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise DSMAuthError(f"DSM transport failed: {exc.reason}") from exc
        if len(raw) > 16 * 1024 * 1024:
            raise DSMAuthError("DSM response exceeded 16 MiB")
        try:
            envelope = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DSMAuthError("DSM returned invalid JSON") from exc
        if not isinstance(envelope, dict) or not isinstance(envelope.get("success"), bool):
            raise DSMAuthError("DSM returned an invalid WebAPI envelope")
        if not envelope["success"]:
            error = envelope.get("error") if isinstance(envelope.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), int) else None
            raise DSMAuthError(f"DSM API operation failed (code {code})", code=code)
        return envelope.get("data")

    def discover(self, query: str = "all") -> dict[str, ApiDescriptor]:
        data = self._post("entry.cgi", {"api": "SYNO.API.Info", "version": 1,
                                        "method": "query", "query": query})
        if not isinstance(data, dict):
            raise DSMAuthError("Discovery response data is invalid")
        for name, item in data.items():
            if not isinstance(name, str) or not isinstance(item, dict):
                continue
            try:
                self.apis[name] = ApiDescriptor(str(item["path"]), int(item["minVersion"]),
                                                int(item["maxVersion"]), item.get("requestFormat"))
            except (KeyError, TypeError, ValueError):
                continue
        return dict(self.apis)

    def descriptor(self, api: str) -> ApiDescriptor:
        if api not in self.apis:
            self.discover(api)
        if api not in self.apis:
            raise DSMAuthError(f"DSM does not advertise {api}")
        return self.apis[api]

    def negotiate(self, api: str, client_max: int, *, client_min: int = 1) -> int:
        info = self.descriptor(api)
        selected = min(info.max_version, client_max)
        if selected < max(info.min_version, client_min):
            raise DSMAuthError(f"No compatible version for {api}")
        return selected

    def login(self, account: str, password: str, *, session: str = "FileStation", otp_code: str | None = None,
              enable_device_token: bool = False, device_name: str | None = None,
              device_id: str | None = None, client_max: int = 6) -> None:
        api = "SYNO.API.Auth"
        info = self.descriptor(api)
        fields: dict[str, Any] = {"api": api, "version": self.negotiate(api, client_max, client_min=3),
                                  "method": "login", "account": account, "passwd": password,
                                  "session": session, "format": "sid", "enable_syno_token": "yes"}
        if otp_code is not None:
            fields["otp_code"] = otp_code
        if enable_device_token:
            fields["enable_device_token"] = "yes"
        if device_name is not None:
            fields["device_name"] = device_name
        if device_id is not None:
            fields["device_id"] = device_id
        data = self._post(info.path, fields)
        if not isinstance(data, dict) or not isinstance(data.get("sid"), str):
            raise DSMAuthError("Login succeeded without a SID")
        self.sid = data["sid"]
        self.synotoken = data.get("synotoken") if isinstance(data.get("synotoken"), str) else None
        self.did = data.get("did") if isinstance(data.get("did"), str) else None

    def call(self, api: str, method: str, params: Mapping[str, Any] | None = None,
             *, client_max: int, client_min: int = 1) -> Any:
        if self.sid is None:
            raise DSMAuthError("Authenticate before calling DSM APIs")
        info = self.descriptor(api)
        fields = dict(params or {})
        fields.update({"api": api, "version": self.negotiate(api, client_max, client_min=client_min),
                       "method": method, "_sid": self.sid})
        if self.synotoken is not None:
            fields["SynoToken"] = self.synotoken
        return self._post(info.path, fields)

    def logout(self, *, client_max: int = 6) -> None:
        if self.sid is None:
            return
        sid, token = self.sid, self.synotoken
        try:
            api = "SYNO.API.Auth"
            info = self.descriptor(api)
            fields = {"api": api, "version": self.negotiate(api, client_max, client_min=3),
                      "method": "logout", "_sid": sid}
            if token is not None:
                fields["SynoToken"] = token
            self._post(info.path, fields)
        finally:
            self.sid = None
            self.synotoken = None
            self.did = None

    def __enter__(self) -> "DSMAuthClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.logout()


def _wire(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


__all__ = ["ApiDescriptor", "DSMAuthClient", "DSMAuthError"]

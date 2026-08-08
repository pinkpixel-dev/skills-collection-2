#!/usr/bin/env python3
"""Dependency-free Surveillance Station WebAPI reference client.

Import as a library. No CLI is exposed. Calls are read-only by default; callers
must pass mutation=True for any operation intended to change server/physical state.
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping


class SurveillanceError(RuntimeError):
    def __init__(self, message: str, *, api: str = "", method: str = "", code: int | None = None):
        super().__init__(message)
        self.api, self.method, self.code = api, method, code


@dataclass(frozen=True)
class ApiInfo:
    path: str
    min_version: int
    max_version: int


class SurveillanceClient:
    def __init__(self, origin: str, *, timeout: float = 30.0, verify_tls: bool = True):
        parsed = urllib.parse.urlsplit(origin)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.path not in {"", "/"}:
            raise ValueError("origin must contain only scheme, host, and optional port")
        if parsed.scheme != "https" and verify_tls:
            raise ValueError("use HTTPS or explicitly opt into an isolated HTTP lab")
        self.origin, self.timeout = origin.rstrip("/"), timeout
        self.context = ssl.create_default_context() if verify_tls else ssl._create_unverified_context()
        self.apis: dict[str, ApiInfo] = {}
        self.sid: str | None = None

    def _post(self, path: str, fields: Mapping[str, Any], *, api: str, method: str) -> Any:
        body = urllib.parse.urlencode({key: _wire(value) for key, value in fields.items()}).encode()
        request = urllib.request.Request(f"{self.origin}/webapi/{path.lstrip('/')}", data=body,
                                         headers={"Content-Type": "application/x-www-form-urlencoded",
                                                  "Accept": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=self.context) as response:
                raw = response.read(32 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            raise SurveillanceError(f"DSM returned HTTP {exc.code}", api=api, method=method) from exc
        except urllib.error.URLError as exc:
            raise SurveillanceError(f"DSM transport failed: {exc.reason}", api=api, method=method) from exc
        if len(raw) > 32 * 1024 * 1024:
            raise SurveillanceError("JSON response exceeded 32 MiB", api=api, method=method)
        try:
            envelope = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SurveillanceError("DSM returned invalid JSON", api=api, method=method) from exc
        if not isinstance(envelope, dict) or not isinstance(envelope.get("success"), bool):
            raise SurveillanceError("Invalid WebAPI envelope", api=api, method=method)
        if not envelope["success"]:
            error = envelope.get("error") if isinstance(envelope.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), int) else None
            raise SurveillanceError(f"Operation failed (code {code})", api=api, method=method, code=code)
        return envelope.get("data")

    def discover(self, query: str = "all") -> dict[str, ApiInfo]:
        data = self._post("query.cgi", {"api": "SYNO.API.Info", "method": "Query",
                                        "version": 1, "query": query}, api="SYNO.API.Info", method="Query")
        if not isinstance(data, dict):
            raise SurveillanceError("Discovery returned invalid data", api="SYNO.API.Info", method="Query")
        for name, item in data.items():
            if isinstance(name, str) and isinstance(item, dict):
                try:
                    self.apis[name] = ApiInfo(str(item["path"]), int(item["minVersion"]), int(item["maxVersion"]))
                except (KeyError, TypeError, ValueError):
                    continue
        return dict(self.apis)

    def info(self, api: str) -> ApiInfo:
        if api not in self.apis:
            self.discover(api)
        if api not in self.apis:
            raise SurveillanceError(f"DSM does not advertise {api}", api=api)
        return self.apis[api]

    def negotiate(self, api: str, client_max: int, *, client_min: int = 1) -> int:
        info = self.info(api)
        selected = min(info.max_version, client_max)
        if selected < max(info.min_version, client_min):
            raise SurveillanceError(f"No compatible version for {api}", api=api)
        return selected

    def login(self, account: str, password: str, *, client_max: int = 2) -> None:
        api = "SYNO.API.Auth"
        info = self.info(api)
        data = self._post(info.path, {"api": api, "method": "login",
                                      "version": self.negotiate(api, client_max), "account": account,
                                      "passwd": password, "session": "SurveillanceStation", "format": "sid"},
                          api=api, method="login")
        if not isinstance(data, dict) or not isinstance(data.get("sid"), str):
            raise SurveillanceError("Login succeeded without SID", api=api, method="login")
        self.sid = data["sid"]

    def call(self, api: str, method: str, params: Mapping[str, Any] | None = None,
             *, client_max: int, client_min: int = 1, mutation: bool = False) -> Any:
        if self.sid is None:
            raise SurveillanceError("Authenticate before calling Surveillance Station", api=api, method=method)
        if _looks_mutating(method) and not mutation:
            raise SurveillanceError("Potentially mutating method requires mutation=True", api=api, method=method)
        info = self.info(api)
        fields = dict(params or {})
        fields.update({"api": api, "method": method,
                       "version": self.negotiate(api, client_max, client_min=client_min), "_sid": self.sid})
        return self._post(info.path, fields, api=api, method=method)

    def logout(self, *, client_max: int = 2) -> None:
        if self.sid is None:
            return
        sid = self.sid
        try:
            api = "SYNO.API.Auth"
            info = self.info(api)
            self._post(info.path, {"api": api, "method": "logout",
                                   "version": self.negotiate(api, client_max), "session": "SurveillanceStation",
                                   "_sid": sid}, api=api, method="logout")
        finally:
            self.sid = None

    def __enter__(self) -> "SurveillanceClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.logout()


def _wire(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


def _looks_mutating(method: str) -> bool:
    prefixes = ("save", "set", "delete", "clear", "enable", "disable", "edit", "create", "format",
                "migrate", "move", "zoom", "focus", "iris", "run", "record", "trunc", "lock", "unlock",
                "apply", "trigger", "switch", "begin", "complete", "cancel", "append", "reset", "correct",
                "mark", "pair", "unpair", "close", "take", "execute", "excute", "stop", "home", "autopan",
                "absptz", "objtracking", "gopreset", "doorcontrol", "block", "ack", "sendtest")
    return method.lower().startswith(prefixes)


__all__ = ["ApiInfo", "SurveillanceClient", "SurveillanceError"]

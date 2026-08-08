#!/usr/bin/env python3
"""Small dependency-free Synology File Station WebAPI reference client.

Import this module from task-specific code. It deliberately exposes no destructive CLI.
Passwords and SIDs are never included in exception messages. Multipart upload is
intentionally bounded to small files because urllib does not stream multipart bodies.
"""

from __future__ import annotations

import json
import mimetypes
import os
import secrets
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Mapping


class FileStationError(RuntimeError):
    def __init__(self, message: str, *, api: str = "", method: str = "", code: int | None = None):
        super().__init__(message)
        self.api = api
        self.method = method
        self.code = code


@dataclass(frozen=True)
class ApiInfo:
    path: str
    min_version: int
    max_version: int


class FileStationClient:
    def __init__(self, base_url: str, *, timeout: float = 30.0, verify_tls: bool = True):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.sid: str | None = None
        self.session_name: str | None = None
        self.apis: dict[str, ApiInfo] = {}
        self._ssl_context = ssl.create_default_context() if verify_tls else ssl._create_unverified_context()

    def _url(self, path: str) -> str:
        clean = path.lstrip("/")
        if not clean.startswith("webapi/"):
            clean = "webapi/" + clean
        return f"{self.base_url}/{clean}"

    def _open(self, request: urllib.request.Request):
        try:
            return urllib.request.urlopen(request, timeout=self.timeout, context=self._ssl_context)
        except urllib.error.HTTPError as exc:
            raise FileStationError(f"DSM returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise FileStationError(f"DSM transport failed: {exc.reason}") from exc

    def _json_call(self, path: str, fields: Mapping[str, Any], *, api: str, method: str) -> Any:
        encoded = urllib.parse.urlencode({k: _wire_value(v) for k, v in fields.items()}).encode()
        request = urllib.request.Request(
            self._url(path),
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            method="POST",
        )
        with self._open(request) as response:
            raw = response.read(16 * 1024 * 1024 + 1)
        if len(raw) > 16 * 1024 * 1024:
            raise FileStationError("DSM JSON response exceeded 16 MiB", api=api, method=method)
        try:
            envelope = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FileStationError("DSM returned invalid JSON", api=api, method=method) from exc
        if not isinstance(envelope, dict) or not isinstance(envelope.get("success"), bool):
            raise FileStationError("DSM returned an invalid WebAPI envelope", api=api, method=method)
        if not envelope["success"]:
            error = envelope.get("error") if isinstance(envelope.get("error"), dict) else {}
            code = error.get("code") if isinstance(error.get("code"), int) else None
            raise FileStationError(f"DSM API operation failed (code {code})", api=api, method=method, code=code)
        return envelope.get("data")

    def discover(self, query: str = "all") -> dict[str, ApiInfo]:
        data = self._json_call(
            "query.cgi",
            {"api": "SYNO.API.Info", "version": 1, "method": "query", "query": query},
            api="SYNO.API.Info",
            method="query",
        )
        if not isinstance(data, dict):
            raise FileStationError("API discovery returned invalid data", api="SYNO.API.Info", method="query")
        discovered: dict[str, ApiInfo] = {}
        for name, item in data.items():
            if isinstance(name, str) and isinstance(item, dict):
                try:
                    discovered[name] = ApiInfo(str(item["path"]), int(item["minVersion"]), int(item["maxVersion"]))
                except (KeyError, TypeError, ValueError):
                    continue
        self.apis.update(discovered)
        return discovered

    def api_info(self, api: str) -> ApiInfo:
        if api not in self.apis:
            self.discover(api)
        try:
            return self.apis[api]
        except KeyError as exc:
            raise FileStationError(f"DSM does not advertise {api}", api=api) from exc

    def negotiate(self, api: str, client_max: int, *, client_min: int = 1) -> int:
        info = self.api_info(api)
        selected = min(info.max_version, client_max)
        if selected < max(info.min_version, client_min):
            raise FileStationError(f"No compatible version for {api}", api=api)
        return selected

    def login(self, account: str, password: str, *, session: str = "FileStation", client_max: int = 3) -> None:
        version = self.negotiate("SYNO.API.Auth", client_max)
        info = self.api_info("SYNO.API.Auth")
        data = self._json_call(
            info.path,
            {"api": "SYNO.API.Auth", "version": version, "method": "login", "account": account,
             "passwd": password, "session": session, "format": "sid"},
            api="SYNO.API.Auth",
            method="login",
        )
        if not isinstance(data, dict) or not isinstance(data.get("sid"), str):
            raise FileStationError("DSM login succeeded without a SID", api="SYNO.API.Auth", method="login")
        self.sid = data["sid"]
        self.session_name = session

    def logout(self) -> None:
        if self.sid is None or self.session_name is None:
            return
        try:
            info = self.api_info("SYNO.API.Auth")
            version = self.negotiate("SYNO.API.Auth", 3)
            self._json_call(info.path, {"api": "SYNO.API.Auth", "version": version, "method": "logout",
                                      "session": self.session_name, "_sid": self.sid},
                            api="SYNO.API.Auth", method="logout")
        finally:
            self.sid = None
            self.session_name = None

    def call(self, api: str, method: str, params: Mapping[str, Any] | None = None,
             *, client_max: int, client_min: int = 1) -> Any:
        if self.sid is None:
            raise FileStationError("Authenticate before calling File Station", api=api, method=method)
        info = self.api_info(api)
        fields = dict(params or {})
        fields.update({"api": api, "version": self.negotiate(api, client_max, client_min=client_min),
                       "method": method, "_sid": self.sid})
        return self._json_call(info.path, fields, api=api, method=method)

    def upload(self, local_path: os.PathLike[str] | str, destination_folder: str, *, overwrite: str,
               create_parents: bool = False, client_max: int = 3) -> Any:
        if self.sid is None:
            raise FileStationError("Authenticate before uploading", api="SYNO.FileStation.Upload", method="upload")
        source = Path(local_path)
        if not source.is_file():
            raise FileStationError("Upload source is not a regular file", api="SYNO.FileStation.Upload", method="upload")
        if source.stat().st_size > 64 * 1024 * 1024:
            raise FileStationError("Reference uploader is limited to 64 MiB; use a streaming HTTP client",
                                   api="SYNO.FileStation.Upload", method="upload")
        api = "SYNO.FileStation.Upload"
        info = self.api_info(api)
        version = self.negotiate(api, client_max, client_min=2)
        fields = {"api": api, "version": version, "method": "upload", "path": destination_folder,
                  "create_parents": create_parents, "overwrite": overwrite, "_sid": self.sid}
        boundary = "----codex-" + secrets.token_hex(16)
        body = _multipart_body(fields, source, boundary)
        request = urllib.request.Request(self._url(info.path), data=body,
                                         headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                                                  "Accept": "application/json"}, method="POST")
        with self._open(request) as response:
            raw = response.read(16 * 1024 * 1024 + 1)
        try:
            envelope = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FileStationError("Upload returned invalid JSON", api=api, method="upload") from exc
        if not isinstance(envelope, dict) or envelope.get("success") is not True:
            error = envelope.get("error", {}) if isinstance(envelope, dict) else {}
            code = error.get("code") if isinstance(error, dict) and isinstance(error.get("code"), int) else None
            raise FileStationError(f"Upload failed (code {code})", api=api, method="upload", code=code)
        return envelope.get("data")

    def download(self, remote_path: str, destination: os.PathLike[str] | str, *, client_max: int = 2) -> Path:
        """Stream a DSM file to a new local path without overwriting an existing file."""
        if self.sid is None:
            raise FileStationError("Authenticate before downloading", api="SYNO.FileStation.Download", method="download")
        api = "SYNO.FileStation.Download"
        info = self.api_info(api)
        fields = {"api": api, "version": self.negotiate(api, client_max, client_min=2), "method": "download",
                  "path": remote_path, "mode": "download", "_sid": self.sid}
        request = urllib.request.Request(self._url(info.path), data=urllib.parse.urlencode(fields).encode(),
                                         headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        target = Path(destination)
        if target.exists():
            raise FileStationError("Download destination already exists", api=api, method="download")
        temporary = target.with_name(target.name + ".partial-" + secrets.token_hex(6))
        try:
            with self._open(request) as response:
                content_type = response.headers.get_content_type()
                if content_type in {"application/json", "text/html"}:
                    raise FileStationError(f"Download returned unexpected content type {content_type}",
                                           api=api, method="download")
                with temporary.open("xb") as output:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
                    output.flush()
                    os.fsync(output.fileno())
            temporary.replace(target)
            return target
        except BaseException:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
            raise

    def close(self) -> None:
        self.logout()

    def __enter__(self) -> "FileStationClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def _wire_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


def _multipart_body(fields: Mapping[str, Any], source: Path, boundary: str) -> bytes:
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend([f"--{boundary}\r\n".encode(),
                       f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                       _wire_value(value).encode(), b"\r\n"])
    safe_name = source.name.replace("\r", "_").replace("\n", "_").replace('"', "_")
    mime = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    chunks.extend([f"--{boundary}\r\n".encode(),
                   f'Content-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'.encode(),
                   f"Content-Type: {mime}\r\n\r\n".encode(), source.read_bytes(), b"\r\n",
                   f"--{boundary}--\r\n".encode()])
    return b"".join(chunks)


__all__ = ["ApiInfo", "FileStationClient", "FileStationError"]

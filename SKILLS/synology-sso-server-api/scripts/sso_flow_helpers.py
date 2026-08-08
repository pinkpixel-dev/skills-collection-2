#!/usr/bin/env python3
"""Pure helpers for Synology SSO manual-flow URL and callback validation."""

from __future__ import annotations

import hmac
import secrets
import urllib.parse
from dataclasses import dataclass


@dataclass(frozen=True)
class CallbackResult:
    access_token: str
    state: str


def generate_state() -> str:
    return secrets.token_urlsafe(32)


def build_authorization_url(sso_origin: str, app_id: str, redirect_uri: str, state: str) -> str:
    origin = urllib.parse.urlsplit(sso_origin)
    redirect = urllib.parse.urlsplit(redirect_uri)
    if origin.scheme != "https" or not origin.netloc or origin.path not in {"", "/"}:
        raise ValueError("sso_origin must be an HTTPS origin")
    if redirect.scheme != "https" or not redirect.netloc or redirect.fragment:
        raise ValueError("redirect_uri must be an absolute HTTPS URI without a fragment")
    if not app_id or not state:
        raise ValueError("app_id and state are required")
    query = urllib.parse.urlencode({"app_id": app_id, "redirect_uri": redirect_uri,
                                    "synossoJSSDK": "false", "scope": "user_id", "state": state})
    return f"{sso_origin.rstrip('/')}/webman/sso/SSOOauth.cgi?{query}"


def validate_callback_fragment(fragment: str, expected_state: str) -> CallbackResult:
    values = urllib.parse.parse_qs(fragment.lstrip("#"), keep_blank_values=True, strict_parsing=True)
    if set(values) - {"access_token", "state"}:
        raise ValueError("callback contains unexpected fields")
    if len(values.get("access_token", [])) != 1 or len(values.get("state", [])) != 1:
        raise ValueError("callback must contain one access_token and one state")
    token, state = values["access_token"][0], values["state"][0]
    if not token or not state or not hmac.compare_digest(state, expected_state):
        raise ValueError("callback state validation failed")
    return CallbackResult(token, state)


__all__ = ["CallbackResult", "build_authorization_url", "generate_state", "validate_callback_fragment"]

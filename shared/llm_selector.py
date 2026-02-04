"""
LLM selector and provider helpers.

Priority: Alibaba Qwen (if AccessKeyId/Secret + endpoint provided)
Fallback: Claude (Anthropic)
Fallback: OpenAI

Provides:
- select_provider(env): returns 'alibaba'|'claude'|'openai'|None
- call_qwen_signed(...): helper to build a signed request for Alibaba Model Studio (caller must supply credentials)
- call_claude(...): simple wrapper for Claude API
- call_openai(...): simple wrapper for OpenAI

This module does not perform real Qwen signing validation here — it constructs
the canonical string and HMAC signature per Alibaba docs template. You must
provide your `ALIBABA_API_ENDPOINT`, `ALIBABA_ACCESS_KEY_ID`, and
`ALIBABA_ACCESS_KEY_SECRET` to actually invoke the endpoint.
"""
from typing import Optional, Dict, Any
import time
import hashlib
import hmac
import base64
import json
import requests


def select_provider(env: Dict[str, str]) -> Optional[str]:
    """Select provider based on available credentials.

    Priority: Alibaba (Qwen) -> Claude -> OpenAI
    Returns provider key or None.
    """
    if env.get("ALIBABA_ACCESS_KEY_ID") and env.get("ALIBABA_ACCESS_KEY_SECRET") and env.get("ALIBABA_API_ENDPOINT"):
        return "alibaba"
    if env.get("CLAUDE_API_KEY"):
        return "claude"
    if env.get("OPENAI_API_KEY"):
        return "openai"
    return None


def _build_qwen_signature(access_key: str, access_secret: str, method: str, path: str, headers: Dict[str, str], body: str) -> str:
    """Construct a simple HMAC-SHA256 signature for Model Studio.

    Note: Alibaba's exact signing algorithm can vary by service/region. This
    helper follows the common pattern of building a canonical string and
    signing with HMAC-SHA256. If your region requires a different scheme,
    adapt accordingly.
    """
    # Canonical request: METHOD + "\n" + PATH + "\n" + sorted headers + "\n" + body
    sorted_headers = "\n".join(f"{k.lower()}:{headers[k]}" for k in sorted(headers))
    canonical = f"{method}\n{path}\n{sorted_headers}\n{body}"
    digest = hmac.new(access_secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode("utf-8")
    return signature


def call_qwen_signed(endpoint: str, model: str, prompt: str, access_key: str, access_secret: str, timeout: int = 15) -> Dict[str, Any]:
    """Call Alibaba Model Studio (Qwen) with a signed request.

    Parameters:
    - endpoint: base URL for Model Studio (e.g. https://model.cn-beijing.aliyuncs.com)
    - model: model name (e.g. qwen-large)
    - prompt: prompt string
    - access_key/access_secret: RAM credentials

    Returns response JSON on success or raises an exception.
    """
    path = "/api/v1/model-invoke"  # example path; adjust per your endpoint
    url = endpoint.rstrip("/") + path

    body_dict = {"model": model, "input": prompt}
    body = json.dumps(body_dict, separators=(",", ":"))

    # Minimum headers for signing
    headers = {
        "host": endpoint.replace("https://", "").replace("http://", ""),
        "content-type": "application/json",
        "x-sdk-date": time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()),
    }

    signature = _build_qwen_signature(access_key, access_secret, "POST", path, headers, body)

    # Authorization header format (simple): AccessKeyId:Signature
    headers["Authorization"] = f"{access_key}:{signature}"

    resp = requests.post(url, headers=headers, data=body, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def call_claude(api_key: str, prompt: str, timeout: int = 15) -> Dict[str, Any]:
    """Call Claude/Anthropic simple endpoint wrapper.

    Note: caller should provide the correct model and endpoint if different.
    """
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def call_openai(api_key: str, prompt: str, timeout: int = 15) -> Dict[str, Any]:
    """Call OpenAI Chat Completions endpoint.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

"""Ahrefs API client: Bearer auth, exponential backoff on 429, log + stop on other errors (plan §10)."""
import logging

import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from brex import config

log = logging.getLogger("brex")


class RateLimited(Exception):
    pass


def _enforce_prompts(path: str, payload: dict | None) -> dict | None:
    """Force prompts="custom" on Brand Radar requests; any other value consumes units (plan §7)."""
    if not path.lstrip("/").startswith("brand-radar/"):
        return payload
    payload = dict(payload or {})
    prompts = payload.setdefault("prompts", config.PROMPTS)
    if prompts != config.PROMPTS:
        raise ValueError(f'prompts="{prompts}" consumes API units; only "{config.PROMPTS}" is allowed.')
    return payload


class AhrefsClient:
    def __init__(self, api_key: str | None = None, timeout: int = 60):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key or config.api_key()}",
            "Accept": "application/json",
        })
        self.timeout = timeout

    @retry(
        retry=retry_if_exception(lambda e: isinstance(e, RateLimited)),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        stop=stop_after_attempt(6),
        reraise=True,
    )
    def _request(self, method: str, url: str, **kwargs) -> dict:
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
        if resp.status_code == 429:
            log.warning("429 rate limit, retrying: %s", url)
            raise RateLimited(url)
        if not resp.ok:
            log.error("%s %s -> %s: %s", method, url, resp.status_code, resp.text[:500])
            resp.raise_for_status()
        return resp.json()

    def get(self, path: str, params: dict | None = None) -> dict:
        return self._request("GET", f"{config.API_ROOT}/{path.lstrip('/')}", params=_enforce_prompts(path, params))

    def post(self, path: str, body: dict) -> dict:
        return self._request("POST", f"{config.API_ROOT}/{path.lstrip('/')}", json=_enforce_prompts(path, body))

    def list_reports(self) -> dict:
        """Does not consume units; used for the initial connection test (plan §7)."""
        return self.get("management/brand-radar-reports")

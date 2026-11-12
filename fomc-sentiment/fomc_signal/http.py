"""带磁盘缓存和重试的 HTTP 下载。"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from urllib.parse import urljoin

import requests

from .config import RAW_DIR, USER_AGENT


def _cache_path(url: str, suffix: str) -> Path:
    digest = hashlib.sha1(url.encode()).hexdigest()[:16]
    return RAW_DIR / "http" / f"{digest}{suffix}"


def _get_https(url: str, timeout: int, max_redirects: int = 5) -> requests.Response:
    """跟随重定向，但始终保持 https（Fed 部分老页面会跳到 http:// 地址）。"""
    for _ in range(max_redirects):
        headers = {"User-Agent": USER_AGENT} if USER_AGENT else None
        resp = requests.get(url, headers=headers, timeout=timeout,
                            allow_redirects=False)
        if resp.is_redirect and "Location" in resp.headers:
            url = urljoin(url, resp.headers["Location"]).replace("http://", "https://", 1)
            continue
        return resp
    raise requests.TooManyRedirects(url)


def _decode(resp: requests.Response) -> str:
    """优先按 UTF-8 解码；requests 在没有 charset 时会误判成 ISO-8859-1。"""
    try:
        return resp.content.decode("utf-8")
    except UnicodeDecodeError:
        return resp.content.decode(resp.encoding or "latin-1", errors="replace")


def get_text(url: str, *, refresh: bool = False, suffix: str = ".html",
             retries: int = 4, timeout: int = 60) -> str:
    """下载 URL 文本；默认命中缓存就不再请求。"""
    path = _cache_path(url, suffix)
    if path.exists() and not refresh:
        return path.read_text(encoding="utf-8")

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            resp = _get_https(url, timeout)
            resp.raise_for_status()
            text = _decode(resp)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            return text
        except requests.RequestException as err:  # 网络抖动时指数退避
            last_err = err
            status = getattr(getattr(err, "response", None), "status_code", None)
            if status is not None and 400 <= status < 500 and status != 429:
                break
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"下载失败: {url}: {last_err}")

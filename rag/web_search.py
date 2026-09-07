from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class WebSearchService:
    """Serper-backed web search service for Self-RAG."""

    ENDPOINT = "https://google.serper.dev/search"

    def __init__(self, max_results: int = 5, timeout: int = 15):
        self.max_results = max(1, min(int(max_results), 10))
        self.timeout = timeout
        self.api_key = os.getenv("SERPER_API_KEY", "").strip()

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str) -> list[dict[str, str]]:
        if not self.api_key:
            return []

        query = (query or "").strip()
        if not query:
            return []

        payload = json.dumps({
            "q": query,
            "num": self.max_results,
            "gl": "in",
            "hl": "en",
        }).encode("utf-8")

        request = Request(
            self.ENDPOINT,
            data=payload,
            headers={
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Serper web search failed with HTTP {exc.code}: {body[:500]}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(
                f"Serper web search connection failed: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise RuntimeError("Serper web search timed out.") from exc

        results = []
        for item in data.get("organic", [])[: self.max_results]:
            title = str(item.get("title", "")).strip()
            url = str(item.get("link", "")).strip()
            snippet = str(item.get("snippet", "")).strip()

            if title or url:
                results.append({
                    "title": title or "Web result",
                    "url": url,
                    "content": snippet,
                })

        return results

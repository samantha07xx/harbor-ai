"""Crawler interface, URL allowlist checks, and guarded single-page fetches.

Step 9 intentionally fetches only one explicitly requested URL at a time. It
does not recursively crawl links or index source content.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from fnmatch import fnmatch
from urllib.parse import urlparse, urlunparse

import httpx

from app.config import get_settings
from app.schemas.sources import FetchedPage, TrustedSource


@dataclass(frozen=True)
class UrlAllowlistDecision:
    """Result of checking a URL against trusted source rules."""

    url: str
    is_allowed: bool
    source_id: str | None = None
    reason: str = "not_checked"


class CrawlerError(ValueError):
    """Base error for guarded crawler operations."""


class UrlNotAllowedError(CrawlerError):
    """Raised when a URL fails the trusted source allowlist."""


class PageFetchError(CrawlerError):
    """Raised when an allowed page cannot be fetched."""


def normalize_url(url: str) -> str:
    """Normalize a URL for allowlist comparison."""

    parsed_url = urlparse(url.strip())
    scheme = parsed_url.scheme.lower()
    hostname = (parsed_url.hostname or "").lower()
    port = parsed_url.port

    netloc = hostname
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc = f"{hostname}:{port}"

    path = parsed_url.path or "/"
    normalized = parsed_url._replace(
        scheme=scheme,
        netloc=netloc,
        path=path,
        params="",
        fragment="",
    )
    return urlunparse(normalized)


def is_same_origin(url: str, base_url: str) -> bool:
    """Return whether two URLs share scheme and hostname."""

    parsed_url = urlparse(normalize_url(url))
    parsed_base_url = urlparse(normalize_url(base_url))
    return parsed_url.scheme == parsed_base_url.scheme and parsed_url.hostname == parsed_base_url.hostname


def find_allowed_source(url: str, sources: list[TrustedSource]) -> UrlAllowlistDecision:
    """Find the trusted source that allows a URL."""

    normalized_url = normalize_url(url)

    if urlparse(normalized_url).scheme not in {"http", "https"}:
        return UrlAllowlistDecision(
            url=normalized_url,
            is_allowed=False,
            reason="unsupported_scheme",
        )

    for source in sources:
        if not source.enabled:
            continue

        if not is_same_origin(normalized_url, str(source.base_url)):
            continue

        seed_urls = {normalize_url(str(seed_url)) for seed_url in source.seed_urls}
        if normalized_url in seed_urls:
            return UrlAllowlistDecision(
                url=normalized_url,
                is_allowed=True,
                source_id=source.source_id,
                reason="seed_url",
            )

        for pattern in source.allowed_url_patterns:
            if fnmatch(normalized_url, normalize_url(pattern)):
                return UrlAllowlistDecision(
                    url=normalized_url,
                    is_allowed=True,
                    source_id=source.source_id,
                    reason="allowed_pattern",
                )

    return UrlAllowlistDecision(
        url=normalized_url,
        is_allowed=False,
        reason="no_matching_trusted_source",
    )


class Crawler:
    """Crawler boundary that future network fetching will use."""

    def __init__(
        self,
        sources: list[TrustedSource],
        *,
        http_client: httpx.Client | None = None,
        user_agent: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        settings = get_settings()
        self.sources = sources
        self.user_agent = user_agent or settings.crawler_user_agent
        self.timeout_seconds = timeout_seconds or settings.crawler_timeout_seconds
        self._http_client = http_client

    def check_url(self, url: str) -> UrlAllowlistDecision:
        """Check whether a URL can be crawled."""

        return find_allowed_source(url, self.sources)

    def get_seed_urls(self) -> list[str]:
        """Return normalized seed URLs from enabled trusted sources."""

        return [
            normalize_url(str(seed_url))
            for source in self.sources
            if source.enabled
            for seed_url in source.seed_urls
        ]

    def plan_allowed_urls(self, urls: list[str]) -> list[UrlAllowlistDecision]:
        """Create allowlist decisions for discovered URLs without fetching them."""

        return [self.check_url(url) for url in urls]

    def fetch_page(self, url: str) -> FetchedPage:
        """Fetch a single allowed page and return raw HTML plus metadata."""

        decision = self.check_url(url)
        if not decision.is_allowed or not decision.source_id:
            raise UrlNotAllowedError(f"URL is not approved for crawling: {decision.url}")

        source = self._get_source(decision.source_id)
        client = self._http_client or httpx.Client(timeout=self.timeout_seconds, follow_redirects=True)
        should_close_client = self._http_client is None

        try:
            response = client.get(
                decision.url,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "User-Agent": self.user_agent,
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise PageFetchError(f"Unable to fetch approved URL: {decision.url}") from exc
        finally:
            if should_close_client:
                client.close()

        content_type = response.headers.get("content-type", "")
        if "html" not in content_type.lower():
            raise PageFetchError(f"Approved URL did not return HTML: {decision.url}")

        return FetchedPage(
            source_id=decision.source_id,
            url=str(response.url),
            raw_html=response.text,
            http_status=response.status_code,
            fetched_at=datetime.now(UTC),
            trust_tier=source.trust_tier,
            language=source.language,
        )

    def _get_source(self, source_id: str) -> TrustedSource:
        """Return a trusted source by ID."""

        for source in self.sources:
            if source.source_id == source_id:
                return source
        raise PageFetchError(f"Trusted source disappeared during fetch: {source_id}")

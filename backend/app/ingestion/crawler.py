"""Crawler interface and URL allowlist checks.

Step 7 intentionally does not fetch remote pages. It only decides whether a URL
is eligible for future crawling based on the trusted source registry.
"""

from dataclasses import dataclass
from fnmatch import fnmatch
from urllib.parse import urlparse, urlunparse

from app.schemas.sources import TrustedSource


@dataclass(frozen=True)
class UrlAllowlistDecision:
    """Result of checking a URL against trusted source rules."""

    url: str
    is_allowed: bool
    source_id: str | None = None
    reason: str = "not_checked"


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

    def __init__(self, sources: list[TrustedSource]) -> None:
        self.sources = sources

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

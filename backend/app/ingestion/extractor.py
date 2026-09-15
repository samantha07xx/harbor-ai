"""HTML extraction utilities.

This module does not fetch pages. It only converts already-fetched HTML into
clean text and lightweight metadata.
"""

from datetime import UTC, datetime
from hashlib import sha256
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.schemas.sources import ExtractedLink, ExtractedPage, FetchedPage

REMOVABLE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "svg",
    "header",
    "footer",
    "nav",
    "aside",
    "form",
    "[role='navigation']",
    "[aria-label='breadcrumb']",
]


def hash_text(text: str) -> str:
    """Return a stable SHA-256 hash for text content."""

    return f"sha256:{sha256(text.encode('utf-8')).hexdigest()}"


def normalize_text(text: str) -> str:
    """Collapse blank lines and extra spaces while preserving paragraph breaks."""

    lines = [" ".join(line.split()) for line in text.splitlines()]
    meaningful_lines = [line for line in lines if line]
    return "\n".join(meaningful_lines)


def extract_page(fetched_page: FetchedPage) -> ExtractedPage:
    """Extract clean page text and metadata from fetched HTML."""

    soup = BeautifulSoup(fetched_page.raw_html, "html.parser")

    for selector in REMOVABLE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    title = extract_title(soup)
    canonical_url = extract_canonical_url(soup, str(fetched_page.url))
    content_root = soup.find("main") or soup.body or soup
    headings = extract_headings(content_root)
    links = extract_links(content_root, str(fetched_page.url))
    clean_text = normalize_text(content_root.get_text(separator="\n"))

    return ExtractedPage(
        source_id=fetched_page.source_id,
        url=fetched_page.url,
        canonical_url=canonical_url,
        title=title,
        clean_text=clean_text,
        clean_text_hash=hash_text(clean_text),
        headings=headings,
        links=links,
        extracted_at=datetime.now(UTC),
        language=fetched_page.language,
        trust_tier=fetched_page.trust_tier,
    )


def extract_title(soup: BeautifulSoup) -> str:
    """Extract a useful page title."""

    h1 = soup.find("h1")
    if h1:
        title = normalize_text(h1.get_text(separator=" "))
        if title:
            return title

    if soup.title and soup.title.string:
        title = normalize_text(soup.title.string)
        if title:
            return title

    return "Untitled page"


def extract_canonical_url(soup: BeautifulSoup, fallback_url: str) -> str:
    """Extract canonical URL or fall back to the fetched URL."""

    canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
    href = canonical.get("href") if canonical else None
    if isinstance(href, str) and href.strip():
        return urljoin(fallback_url, href.strip())
    return fallback_url


def extract_headings(content_root: BeautifulSoup) -> list[str]:
    """Extract page headings in document order."""

    headings: list[str] = []
    for heading in content_root.find_all(["h1", "h2", "h3"]):
        text = normalize_text(heading.get_text(separator=" "))
        if text:
            headings.append(text)
    return headings


def extract_links(content_root: BeautifulSoup, base_url: str) -> list[ExtractedLink]:
    """Extract useful content links."""

    links: list[ExtractedLink] = []
    seen_urls: set[str] = set()

    for anchor in content_root.find_all("a", href=True):
        text = normalize_text(anchor.get_text(separator=" "))
        url = urljoin(base_url, anchor["href"])
        if not text or url in seen_urls or urlparse(url).scheme not in {"http", "https"}:
            continue
        links.append(ExtractedLink(text=text, url=url))
        seen_urls.add(url)

    return links

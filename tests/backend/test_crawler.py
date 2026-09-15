import httpx
import pytest

from app.ingestion.crawler import (
    Crawler,
    PageFetchError,
    UrlNotAllowedError,
    find_allowed_source,
    normalize_url,
)
from app.ingestion.source_registry import get_enabled_sources


def test_normalize_url_removes_fragments_and_lowercases_origin() -> None:
    assert (
        normalize_url("HTTPS://WWW.ONTARIO.CA/page/apply-ohip-and-get-health-card#documents")
        == "https://www.ontario.ca/page/apply-ohip-and-get-health-card"
    )


def test_seed_url_is_allowed() -> None:
    decision = find_allowed_source(
        "https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        get_enabled_sources(),
    )

    assert decision.is_allowed is True
    assert decision.source_id == "ontario_health_pages"
    assert decision.reason == "seed_url"


def test_allowed_pattern_url_is_allowed() -> None:
    decision = find_allowed_source(
        "https://www.ontario.ca/page/renew-health-card",
        get_enabled_sources(),
    )

    assert decision.is_allowed is True
    assert decision.source_id == "ontario_health_pages"
    assert decision.reason == "allowed_pattern"


def test_unapproved_domain_is_rejected() -> None:
    decision = find_allowed_source(
        "https://example.com/page/apply-ohip-and-get-health-card",
        get_enabled_sources(),
    )

    assert decision.is_allowed is False
    assert decision.source_id is None
    assert decision.reason == "no_matching_trusted_source"


def test_unsupported_scheme_is_rejected() -> None:
    decision = find_allowed_source(
        "ftp://www.ontario.ca/page/apply-ohip-and-get-health-card",
        get_enabled_sources(),
    )

    assert decision.is_allowed is False
    assert decision.reason == "unsupported_scheme"


def test_crawler_returns_enabled_seed_urls_only() -> None:
    crawler = Crawler(get_enabled_sources())

    seed_urls = crawler.get_seed_urls()

    assert "https://www.ontario.ca/page/apply-ohip-and-get-health-card" in seed_urls
    assert "https://health811.ontario.ca/" in seed_urls


def test_crawler_plans_url_decisions_without_fetching() -> None:
    crawler = Crawler(get_enabled_sources())

    decisions = crawler.plan_allowed_urls(
        [
            "https://www.ontario.ca/page/walk-clinics",
            "https://untrusted.example.org/health",
        ]
    )

    assert [decision.is_allowed for decision in decisions] == [True, False]


def test_crawler_fetches_allowed_single_page() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["user-agent"].startswith("HarborBot/")
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="<html><body><main><h1>Apply for OHIP</h1></main></body></html>",
            request=request,
        )

    crawler = Crawler(
        get_enabled_sources(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    page = crawler.fetch_page("https://www.ontario.ca/page/apply-ohip-and-get-health-card")

    assert page.source_id == "ontario_health_pages"
    assert page.http_status == 200
    assert "Apply for OHIP" in page.raw_html
    assert page.trust_tier == "official_government"


def test_crawler_rejects_unapproved_url_before_fetching() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("Unapproved URLs must not be fetched")

    crawler = Crawler(
        get_enabled_sources(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(UrlNotAllowedError):
        crawler.fetch_page("https://example.com/not-approved")


def test_crawler_rejects_non_html_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/pdf"},
            content=b"%PDF",
            request=request,
        )

    crawler = Crawler(
        get_enabled_sources(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(PageFetchError, match="did not return HTML"):
        crawler.fetch_page("https://www.ontario.ca/page/apply-ohip-and-get-health-card")


def test_crawler_wraps_http_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, request=request)

    crawler = Crawler(
        get_enabled_sources(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(PageFetchError, match="Unable to fetch approved URL"):
        crawler.fetch_page("https://www.ontario.ca/page/apply-ohip-and-get-health-card")

import httpx
import pytest

from app.ingestion.crawler import Crawler, UrlNotAllowedError
from app.ingestion.page_ingestion import PageIngestionService
from app.ingestion.source_registry import get_enabled_sources


def make_service(handler) -> PageIngestionService:
    crawler = Crawler(
        get_enabled_sources(),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return PageIngestionService(crawler)


def test_ingest_one_page_fetches_and_extracts_allowed_html() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="""
            <html>
              <head>
                <link rel="canonical" href="/page/apply-ohip-and-get-health-card" />
              </head>
              <body>
                <header>Site navigation</header>
                <main>
                  <h1>Apply for OHIP and get a health card</h1>
                  <p>There is no longer a waiting period for OHIP coverage.</p>
                </main>
              </body>
            </html>
            """,
            request=request,
        )

    service = make_service(handler)

    result = service.ingest_one_page(
        "https://www.ontario.ca/page/apply-ohip-and-get-health-card"
    )

    assert result.fetched_page.source_id == "ontario_health_pages"
    assert result.extracted_page.title == "Apply for OHIP and get a health card"
    assert "There is no longer a waiting period" in result.extracted_page.clean_text
    assert "Site navigation" not in result.extracted_page.clean_text


def test_ingest_one_page_rejects_unapproved_url_before_fetch() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("Unapproved URLs must not be fetched")

    service = make_service(handler)

    with pytest.raises(UrlNotAllowedError):
        service.ingest_one_page("https://example.com/page/apply-ohip")

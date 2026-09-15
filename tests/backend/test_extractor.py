from datetime import UTC, datetime

from app.ingestion.extractor import extract_page, hash_text, normalize_text
from app.schemas.sources import FetchedPage, TrustTier


def make_fetched_page(raw_html: str) -> FetchedPage:
    return FetchedPage(
        source_id="ontario_health_pages",
        url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
        raw_html=raw_html,
        http_status=200,
        fetched_at=datetime.now(UTC),
        trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
    )


def test_normalize_text_collapses_extra_spacing() -> None:
    assert normalize_text(" Apply   for   OHIP\n\n\n Bring documents ") == (
        "Apply for OHIP\nBring documents"
    )


def test_hash_text_uses_expected_prefix() -> None:
    assert hash_text("Harbor").startswith("sha256:")
    assert len(hash_text("Harbor")) == 71


def test_extract_page_preserves_main_content_and_removes_boilerplate() -> None:
    page = make_fetched_page(
        """
        <html>
          <head>
            <title>Ignored title</title>
            <link rel="canonical" href="/page/apply-ohip-and-get-health-card" />
            <style>.hidden { display: none; }</style>
            <script>window.analytics = true;</script>
          </head>
          <body>
            <header>Government navigation</header>
            <nav>Menu</nav>
            <main>
              <h1>Apply for OHIP and get a health card</h1>
              <h2>Who qualifies</h2>
              <p>You need to meet Ontario residency requirements.</p>
              <a href="/page/documents-needed-get-health-card">Documents needed</a>
            </main>
            <footer>Footer links</footer>
          </body>
        </html>
        """
    )

    extracted = extract_page(page)

    assert extracted.title == "Apply for OHIP and get a health card"
    assert str(extracted.canonical_url) == (
        "https://www.ontario.ca/page/apply-ohip-and-get-health-card"
    )
    assert "You need to meet Ontario residency requirements." in extracted.clean_text
    assert "Government navigation" not in extracted.clean_text
    assert "Footer links" not in extracted.clean_text
    assert extracted.headings == ["Apply for OHIP and get a health card", "Who qualifies"]
    assert str(extracted.links[0].url) == "https://www.ontario.ca/page/documents-needed-get-health-card"


def test_extract_page_falls_back_to_title_when_h1_missing() -> None:
    page = make_fetched_page(
        """
        <html>
          <head><title>Health811 Ontario</title></head>
          <body><main><p>Call 811 for non-emergency health advice.</p></main></body>
        </html>
        """
    )

    extracted = extract_page(page)

    assert extracted.title == "Health811 Ontario"
    assert "Call 811" in extracted.clean_text

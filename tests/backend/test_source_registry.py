import json

import pytest

from app.ingestion.source_registry import (
    SourceRegistryError,
    get_enabled_sources,
    load_trusted_sources,
)


def test_default_registry_loads_trusted_sources() -> None:
    sources = load_trusted_sources()

    assert len(sources) == 3
    assert {source.source_id for source in sources} == {
        "ontario_health_pages",
        "health811",
        "ontario_health",
    }


def test_default_registry_includes_ohip_seed_url() -> None:
    sources = load_trusted_sources()
    ontario_health_pages = next(
        source for source in sources if source.source_id == "ontario_health_pages"
    )

    seed_urls = {str(url) for url in ontario_health_pages.seed_urls}

    assert "https://www.ontario.ca/page/apply-ohip-and-get-health-card" in seed_urls
    assert ontario_health_pages.trust_tier == "official_government"


def test_get_enabled_sources_filters_disabled_sources(tmp_path) -> None:
    registry_path = tmp_path / "trusted_sources.json"
    registry_path.write_text(
        json.dumps(
            [
                {
                    "source_id": "enabled_source",
                    "name": "Enabled Source",
                    "base_url": "https://example.com/",
                    "seed_urls": ["https://example.com/health"],
                    "trust_tier": "approved_nonprofit",
                    "enabled": True,
                },
                {
                    "source_id": "disabled_source",
                    "name": "Disabled Source",
                    "base_url": "https://disabled.example.com/",
                    "seed_urls": ["https://disabled.example.com/health"],
                    "trust_tier": "approved_nonprofit",
                    "enabled": False,
                },
            ]
        ),
        encoding="utf-8",
    )

    enabled_sources = get_enabled_sources(registry_path)

    assert [source.source_id for source in enabled_sources] == ["enabled_source"]


def test_invalid_registry_raises_clear_error(tmp_path) -> None:
    registry_path = tmp_path / "trusted_sources.json"
    registry_path.write_text("{not json", encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="not valid JSON"):
        load_trusted_sources(registry_path)

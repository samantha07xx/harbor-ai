import json

from app.ingestion.cli import main, run_dry_run, run_qdrant_index
from app.retrieval.qdrant_client import InMemoryVectorStore

FIXTURE_HTML = """
<html>
  <body>
    <main>
      <h1>Apply for OHIP and get a health card</h1>
      <p>There is no longer a waiting period for OHIP coverage.</p>
      <p>You need to make Ontario your primary residence.</p>
    </main>
  </body>
</html>
"""


def test_run_dry_run_returns_json_ready_summary(tmp_path) -> None:
    fixture_path = tmp_path / "ohip.html"
    fixture_path.write_text(FIXTURE_HTML, encoding="utf-8")

    summary = run_dry_run(
        fixture_html_path=fixture_path,
        embedding_dimensions=8,
        target_token_count=30,
        overlap_token_count=5,
    )

    assert summary["source_id"] == "ontario_health_pages"
    assert summary["title"] == "Apply for OHIP and get a health card"
    assert summary["chunk_count"] >= 1
    assert summary["embedding_count"] == summary["chunk_count"]
    assert summary["point_count"] == summary["chunk_count"]
    assert "OHIP" in summary["first_chunk_preview"]
    assert "text" in summary["first_point_payload_keys"]


def test_cli_main_prints_summary(tmp_path, capsys) -> None:
    fixture_path = tmp_path / "ohip.html"
    fixture_path.write_text(FIXTURE_HTML, encoding="utf-8")

    exit_code = main(
        [
            "--fixture-html",
            str(fixture_path),
            "--embedding-dimensions",
            "8",
            "--target-token-count",
            "30",
            "--overlap-token-count",
            "5",
        ]
    )

    output = capsys.readouterr().out
    summary = json.loads(output)
    assert exit_code == 0
    assert summary["source_id"] == "ontario_health_pages"
    assert summary["point_count"] >= 1


def test_run_qdrant_index_upserts_fixture_points_into_vector_store(tmp_path) -> None:
    fixture_path = tmp_path / "ohip.html"
    fixture_path.write_text(FIXTURE_HTML, encoding="utf-8")
    vector_store = InMemoryVectorStore()

    summary = run_qdrant_index(
        urls=["https://www.ontario.ca/page/apply-ohip-and-get-health-card"],
        fixture_html_path=fixture_path,
        target_token_count=30,
        overlap_token_count=5,
        ensure_collection=False,
        vector_store=vector_store,
    )

    assert summary["retrieval_mode"] == "qdrant"
    assert summary["embedding_model"] == "local-keyword-fixture"
    assert summary["indexed_page_count"] == 1
    assert summary["upserted_point_count"] >= 1
    assert summary["failed_pages"] == []
    assert len(vector_store.points) == summary["upserted_point_count"]

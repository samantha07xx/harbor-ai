from datetime import UTC, datetime

from app.agent.answer_composer import AnswerComposer
from app.agent.llm import LLMAnswerRequest
from app.retrieval.query_rewrite import QueryIntent, QueryRewriteResult
from app.retrieval.service import RewrittenRetrievalResult
from app.schemas.chunks import RetrievalHit, RetrievalResult, SourceChunk
from app.schemas.sources import TopicCategory, TrustTier

HASH = "sha256:" + "d" * 64


class FakeLLMAnswerProvider:
    model = "fake-llm"

    def __init__(self) -> None:
        self.requests: list[LLMAnswerRequest] = []

    def generate_answer(self, request: LLMAnswerRequest) -> str:
        self.requests.append(request)
        return "Use the cited official source to apply for OHIP. [1]"


def make_hit(
    *,
    chunk_id: str = "chunk_health811",
    title: str = "Health811",
    url: str = "https://health811.ontario.ca/",
    text: str = "Contact Health811 for free, secure, non-emergency health advice in Ontario.",
    topic: TopicCategory = TopicCategory.NON_EMERGENCY_ADVICE,
) -> RetrievalHit:
    return RetrievalHit(
        chunk=SourceChunk(
            chunk_id=chunk_id,
            page_id=f"page_{chunk_id}",
            source_id="local_demo_fixture",
            source_url=url,
            title=title,
            section_heading=title,
            topic=topic,
            trust_tier=TrustTier.OFFICIAL_GOVERNMENT,
            chunk_index=0,
            text=text,
            token_count=len(text.split()),
            content_hash=HASH,
            last_crawled_at=datetime(2026, 9, 15, tzinfo=UTC),
        ),
        score=1.0,
    )


def make_result(
    *,
    hits: list[RetrievalHit],
    intent: QueryIntent = QueryIntent.NON_EMERGENCY_ADVICE,
    needs_safety_check: bool = False,
) -> RewrittenRetrievalResult:
    return RewrittenRetrievalResult(
        original_question="Can I call someone?",
        rewrite=QueryRewriteResult(
            original_question="Can I call someone?",
            rewritten_queries=["Ontario non-emergency health advice call 811 Health811"],
            detected_intent=intent,
            confidence=0.88,
            needs_safety_check=needs_safety_check,
        ),
        retrieval=RetrievalResult(
            query="Ontario non-emergency health advice call 811 Health811",
            hits=hits,
            filters={"jurisdiction": "Ontario", "language": "en"},
        ),
    )


def test_composer_creates_cited_answer_from_retrieval_hits() -> None:
    composer = AnswerComposer()

    answer = composer.compose(make_result(hits=[make_hit()]))

    assert "non-emergency health advice" in answer.answer
    assert "Health811" in answer.answer
    assert "[1]" in answer.answer
    assert len(answer.citations) == 1
    assert answer.citations[0].title == "Health811"
    assert answer.citations[0].url == "https://health811.ontario.ca/"


def test_composer_deduplicates_citations_by_url() -> None:
    composer = AnswerComposer()

    answer = composer.compose(
        make_result(
            hits=[
                make_hit(chunk_id="chunk_1"),
                make_hit(chunk_id="chunk_2", text="A second Health811 passage."),
            ],
        )
    )

    assert len(answer.citations) == 1


def test_composer_returns_no_source_message_without_hits() -> None:
    composer = AnswerComposer()

    answer = composer.compose(make_result(hits=[]))

    assert "could not find" in answer.answer
    assert answer.citations == []


def test_composer_places_emergency_notice_first_when_needed() -> None:
    composer = AnswerComposer()

    answer = composer.compose(
        make_result(
            hits=[
                make_hit(
                    title="Emergency care",
                    text="For a medical emergency in Ontario, call 911.",
                    topic=TopicCategory.EMERGENCY_CARE,
                )
            ],
            intent=QueryIntent.EMERGENCY,
            needs_safety_check=True,
        )
    )

    assert answer.answer.startswith("If this may be an emergency, call 911")
    assert answer.citations[0].title == "Emergency care"


def test_composer_can_use_llm_provider_for_grounded_answer() -> None:
    provider = FakeLLMAnswerProvider()
    composer = AnswerComposer(llm_provider=provider)

    answer = composer.compose(
        make_result(
            hits=[
                make_hit(
                    title="Apply for OHIP and get a health card",
                    url="https://www.ontario.ca/page/apply-ohip-and-get-health-card",
                    text="Apply for OHIP through ServiceOntario.",
                    topic=TopicCategory.HEALTH_CARD_APPLICATION,
                )
            ],
            intent=QueryIntent.OHIP_APPLICATION,
        )
    )

    assert answer.answer == "Use the cited official source to apply for OHIP. [1]"
    assert answer.answer_mode == "openai_grounded"
    assert answer.llm_model == "fake-llm"
    assert answer.citations[0].title == "Apply for OHIP and get a health card"
    assert provider.requests[0].question == "Can I call someone?"
    assert "Apply for OHIP through ServiceOntario." in provider.requests[0].evidence[0]

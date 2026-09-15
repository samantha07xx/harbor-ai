"""Grounded draft answer composition.

Step 22 adds a deterministic answer composer. It does not call an LLM; it turns
retrieved chunks into a conservative cited draft for API contract testing.
"""

from dataclasses import dataclass

from app.retrieval.query_rewrite import QueryIntent
from app.retrieval.service import RewrittenRetrievalResult
from app.schemas.chat import Citation
from app.schemas.chunks import RetrievalHit


@dataclass(frozen=True)
class GroundedDraftAnswer:
    """A conservative answer draft grounded in retrieved chunks."""

    answer: str
    citations: list[Citation]


class AnswerComposer:
    """Compose a simple cited answer from retrieval output."""

    def compose(self, result: RewrittenRetrievalResult) -> GroundedDraftAnswer:
        """Create a cited draft answer from rewritten retrieval output."""

        if not result.retrieval.hits:
            return GroundedDraftAnswer(
                answer=(
                    "I could not find a matching trusted Harbor source for that question yet. "
                    "Try asking about OHIP, health cards, Health811, walk-in clinics, or "
                    "finding a family doctor in Ontario."
                ),
                citations=[],
            )

        citations = deduplicate_citations(result.retrieval.hits)
        evidence_lines = [
            f"- {hit.chunk.text} [{index}]"
            for index, hit in enumerate(result.retrieval.hits[:3], start=1)
        ]
        lead = lead_sentence_for_intent(result.rewrite.detected_intent)

        answer_parts = [
            lead,
            "Based on the retrieved Harbor source material:",
            *evidence_lines,
        ]
        if result.rewrite.needs_safety_check:
            answer_parts.insert(
                0,
                "If this may be an emergency, call 911 or go to the nearest emergency department.",
            )

        return GroundedDraftAnswer(
            answer="\n".join(answer_parts),
            citations=citations,
        )


def lead_sentence_for_intent(intent: QueryIntent) -> str:
    """Return a short deterministic opening for a detected query intent."""

    match intent:
        case QueryIntent.OHIP_APPLICATION:
            return "Here is the most relevant starting point for applying for OHIP."
        case QueryIntent.OHIP_ELIGIBILITY:
            return "Here is the most relevant starting point for checking OHIP eligibility."
        case QueryIntent.REQUIRED_DOCUMENTS:
            return "Here is the most relevant starting point for required health card documents."
        case QueryIntent.FINDING_FAMILY_DOCTOR:
            return "Here is the most relevant starting point for finding primary care in Ontario."
        case QueryIntent.WALK_IN_CLINIC:
            return "Here is the most relevant starting point for walk-in care options in Ontario."
        case QueryIntent.NON_EMERGENCY_ADVICE:
            return "Here is the most relevant starting point for non-emergency health advice."
        case QueryIntent.NEWCOMER_HEALTHCARE_ACCESS:
            return "Here is the most relevant starting point for newcomers accessing healthcare."
        case QueryIntent.EMERGENCY:
            return "Here is the most relevant emergency-care source Harbor found."
        case QueryIntent.GENERAL_HEALTHCARE_NAVIGATION:
            return "Here is the most relevant Ontario healthcare navigation source Harbor found."


def deduplicate_citations(hits: list[RetrievalHit]) -> list[Citation]:
    """Create citations from retrieval hits, deduplicated by URL."""

    citations: list[Citation] = []
    seen_urls: set[str] = set()
    for hit in hits:
        citation = hit.to_citation()
        url = str(citation.url)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        citations.append(Citation(title=citation.title, url=url))
    return citations

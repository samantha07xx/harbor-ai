from app.agent.answer_composer import AnswerComposer
from app.agent.tools import HealthcareRetrievalTool
from app.retrieval.demo import get_local_demo_rewritten_retrieval_service


def make_tool() -> HealthcareRetrievalTool:
    return HealthcareRetrievalTool(
        retrieval_service=get_local_demo_rewritten_retrieval_service(),
        answer_composer=AnswerComposer(),
    )


def test_healthcare_retrieval_tool_returns_cited_answer() -> None:
    tool = make_tool()

    result = tool.run("Can I call someone if it is not an emergency?", limit=1)

    assert result.tool_name == "healthcare_retrieval"
    assert "Health811" in result.answer
    assert result.citations[0].title == "Health811"
    assert result.metadata["detected_intent"] == "non_emergency_advice"
    assert result.metadata["primary_query"] == "Ontario non-emergency health advice call 811 Health811"
    assert result.metadata["retrieval_hit_count"] == 1


def test_healthcare_retrieval_tool_preserves_safety_metadata() -> None:
    tool = make_tool()

    result = tool.run("I have chest pain, is this an emergency?", limit=1)

    assert result.metadata["detected_intent"] == "emergency"
    assert result.metadata["needs_safety_check"] is True

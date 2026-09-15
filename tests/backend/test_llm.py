import httpx
import pytest

from app.agent.llm import (
    LLMAnswerRequest,
    OpenAIAnswerProvider,
    build_grounded_answer_prompt,
    extract_response_text,
)


def test_openai_answer_provider_posts_grounded_responses_request() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(
            200,
            json={"output_text": "Apply through ServiceOntario with required documents. [1]"},
            request=request,
        )

    provider = OpenAIAnswerProvider(
        api_key="test-key",
        model="gpt-5-mini",
        base_url="https://api.openai.test/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    answer = provider.generate_answer(
        LLMAnswerRequest(
            question="How do I apply for OHIP?",
            intent="ohip_application",
            evidence=["[1] Apply for OHIP\nURL: https://www.ontario.ca/\nExcerpt: Apply online."],
        )
    )

    assert captured_request is not None
    assert captured_request.url.path == "/v1/responses"
    assert captured_request.headers["authorization"] == "Bearer test-key"
    assert b'"model":"gpt-5-mini"' in captured_request.content
    assert b'"max_output_tokens":260' in captured_request.content
    assert b"Answer only from the trusted source material" in captured_request.content
    assert b"Do not mention internal words" in captured_request.content
    assert b"Do not put the heading and explanation on the same line" in captured_request.content
    assert answer == "Apply through ServiceOntario with required documents. [1]"


def test_openai_answer_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIAnswerProvider(api_key="")


def test_build_grounded_answer_prompt_includes_question_and_evidence() -> None:
    prompt = build_grounded_answer_prompt(
        LLMAnswerRequest(
            question="How do I get a health card?",
            intent="ohip_application",
            evidence=["[1] Evidence text"],
        )
    )

    assert "How do I get a health card?" in prompt
    assert "ohip_application" in prompt
    assert "[1] Evidence text" in prompt


def test_extract_response_text_supports_nested_response_output() -> None:
    body = {
        "output": [
            {
                "content": [
                    {"type": "output_text", "text": "First part."},
                    {"type": "output_text", "text": "Second part."},
                ]
            }
        ]
    }

    assert extract_response_text(body) == "First part.\nSecond part."

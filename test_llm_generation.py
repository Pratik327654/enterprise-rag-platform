

from types import SimpleNamespace

import pytest

from app.generation.generator import LLMGenerator


class FakeLLM:
    """Fake LLM for testing without starting Ollama."""

    def __init__(self, response):
        self.response = response
        self.call_count = 0

    def invoke(self, prompt):
        self.call_count += 1
        return SimpleNamespace(content=self.response)


@pytest.fixture
def sample_chunks():
    return [
        {
            "text": "Employees receive 20 annual leave days per year.",
            "metadata": {
                "source": "employee_policy_sample.pdf",
                "page_number": 1,
                "chunk_id": "test-chunk-1",
            },
        }
    ]


def test_generate_returns_answer_and_sources(sample_chunks):
    fake_llm = FakeLLM(
        "Employees receive 20 annual leave days per year."
    )

    generator = LLMGenerator(llm=fake_llm)

    result = generator.generate(
        query="How many annual leave days are provided?",
        context_chunks=sample_chunks,
    )

    assert "20" in result["answer"]
    assert result["model"] == generator.model_name
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source"] == (
        "employee_policy_sample.pdf"
    )
    assert fake_llm.call_count == 1


def test_generate_handles_empty_context():
    fake_llm = FakeLLM("This should not be called.")

    generator = LLMGenerator(llm=fake_llm)

    result = generator.generate(
        query="Who is the CEO?",
        context_chunks=[],
    )

    assert result["sources"] == []
    assert "enough information" in result["answer"].lower()
    assert fake_llm.call_count == 0


def test_generate_rejects_empty_query():
    generator = LLMGenerator(
        llm=FakeLLM("Test answer")
    )

    with pytest.raises(ValueError):
        generator.generate(
            query=" ",
            context_chunks=[
                {"text": "Sample document text."}
            ],
        )


def test_generate_rejects_invalid_context_type():
    generator = LLMGenerator(
        llm=FakeLLM("Test answer")
    )

    with pytest.raises(ValueError):
        generator.generate(
            query="Test query",
            context_chunks="invalid context",
        )

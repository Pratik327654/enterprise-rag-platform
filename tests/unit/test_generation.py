
import pytest

from app.core.exceptions import GenerationError
from app.generation.generator import LLMGenerator
from app.generation.prompt_builder import build_rag_prompt


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, response="Employees receive 20 days of annual leave. [S1]"):
        self.response = response
        self.last_prompt = None
        self.call_count = 0

    def invoke(self, prompt):
        self.last_prompt = prompt
        self.call_count += 1
        return FakeResponse(self.response)


@pytest.fixture
def sample_chunks():
    return [
        {
            "text": "Employees receive 20 days of annual leave.",
            "metadata": {
                "source": "employee_policy.pdf",
                "page_number": 3,
                "chunk_id": "chunk-001",
            },
            "rerank_score": 0.95,
            "rerank_rank": 1,
        },
        {
            "text": "Employees can request leave through HR.",
            "metadata": {
                "source": "employee_policy.pdf",
                "page_number": 4,
                "chunk_id": "chunk-002",
            },
            "rerank_score": 0.82,
            "rerank_rank": 2,
        },
    ]


# Prompt builder tests

def test_prompt_contains_user_query(sample_chunks):
    prompt = build_rag_prompt(
        "How many annual leave days?",
        sample_chunks,
    )

    assert "How many annual leave days?" in prompt


def test_prompt_contains_document_context(sample_chunks):
    prompt = build_rag_prompt(
        "How many annual leave days?",
        sample_chunks,
    )

    assert "20 days of annual leave" in prompt
    assert "Employees can request leave through HR" in prompt


def test_prompt_contains_source_references(sample_chunks):
    prompt = build_rag_prompt(
        "How many annual leave days?",
        sample_chunks,
    )

    assert "[S1]" in prompt
    assert "[S2]" in prompt



def test_prompt_contains_grounding_instructions(sample_chunks):
    prompt = build_rag_prompt(
        "How many annual leave days?",
        sample_chunks,
    )

    assert "based on the excerpts" in prompt
    assert "document excerpts" in prompt.lower()
    assert "do not know" in prompt
    assert "[S1]" in prompt
    assert "[S2]" in prompt




def test_prompt_rejects_empty_query(sample_chunks):
    with pytest.raises(ValueError):
        build_rag_prompt("", sample_chunks)


def test_prompt_rejects_invalid_chunks():
    with pytest.raises(ValueError):
        build_rag_prompt("Question?", "invalid")


def test_prompt_rejects_empty_chunks():
    with pytest.raises(ValueError):
        build_rag_prompt("Question?", [])


def test_prompt_rejects_invalid_chunk_text():
    chunks = [{"text": " ", "metadata": {}}]

    with pytest.raises(ValueError):
        build_rag_prompt("Question?", chunks)


# Generator tests

def test_generator_returns_answer(sample_chunks):
    fake_llm = FakeLLM()
    generator = LLMGenerator(llm=fake_llm)

    result = generator.generate(
        "How many annual leave days?",
        sample_chunks,
    )

    assert result["answer"] == (
        "Employees receive 20 days of annual leave. [S1]"
    )


def test_generator_returns_sources(sample_chunks):
    generator = LLMGenerator(llm=FakeLLM())

    result = generator.generate(
        "How many annual leave days?",
        sample_chunks,
    )

    assert len(result["sources"]) == 2
    assert result["sources"][0]["source_id"] == "S1"
    assert result["sources"][0]["source"] == "employee_policy.pdf"
    assert result["sources"][0]["page_number"] == 3


def test_generator_returns_model_name(sample_chunks):
    generator = LLMGenerator(
        model_name="test-model",
        llm=FakeLLM(),
    )

    result = generator.generate(
        "How many annual leave days?",
        sample_chunks,
    )

    assert result["model"] == "test-model"


def test_generator_passes_prompt_to_llm(sample_chunks):
    fake_llm = FakeLLM()
    generator = LLMGenerator(llm=fake_llm)

    generator.generate(
        "How many annual leave days?",
        sample_chunks,
    )

    assert "20 days of annual leave" in fake_llm.last_prompt


def test_generator_does_not_call_llm_without_context():
    fake_llm = FakeLLM()
    generator = LLMGenerator(llm=fake_llm)

    result = generator.generate(
        "What is the company leave policy?",
        [],
    )

    assert "don't have enough information" in result["answer"]
    assert result["sources"] == []
    assert fake_llm.call_count == 0


def test_generator_rejects_empty_query(sample_chunks):
    generator = LLMGenerator(llm=FakeLLM())

    with pytest.raises(ValueError):
        generator.generate("", sample_chunks)


def test_generator_rejects_invalid_context():
    generator = LLMGenerator(llm=FakeLLM())

    with pytest.raises(ValueError):
        generator.generate("Question?", "invalid")


def test_generator_wraps_llm_failure(sample_chunks):
    class FailingLLM:
        def invoke(self, prompt):
            raise RuntimeError("Test LLM failure")

    generator = LLMGenerator(llm=FailingLLM())

    with pytest.raises(GenerationError):
        generator.generate("Question?", sample_chunks)


def test_generator_rejects_empty_llm_response(sample_chunks):
    generator = LLMGenerator(llm=FakeLLM(response="  "))

    with pytest.raises(GenerationError):
        generator.generate("Question?", sample_chunks)


def test_generator_reuses_llm(sample_chunks):
    fake_llm = FakeLLM()
    generator = LLMGenerator(llm=fake_llm)

    generator.generate("Question one?", sample_chunks)
    generator.generate("Question two?", sample_chunks)

    assert fake_llm.call_count == 2



import logging

from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

from app.core.config import settings


logger = logging.getLogger(__name__)


# --------------------------------------------------
# 1. Structured Evaluation Schema
# --------------------------------------------------

class EvaluationScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class LLMEvaluationResult(BaseModel):
    faithfulness: EvaluationScore
    answer_relevancy: EvaluationScore
    context_relevancy: EvaluationScore
    answer_correctness: EvaluationScore


# --------------------------------------------------
# 2. LLM Evaluator
# --------------------------------------------------

class LLMEvaluator:
    """Evaluate RAG answers using an Ollama judge."""

    def __init__(
        self,
        model_name: str = settings.LLM_MODEL,
        base_url: str = settings.OLLAMA_BASE_URL,
        temperature: float = 0.0,
        llm=None,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.llm = llm

        if not isinstance(temperature, (int, float)) or isinstance(
            temperature, bool
        ):
            raise ValueError("Temperature must be numeric.")

        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1.")

    # --------------------------------------------------
    # 3. Load Judge Model
    # --------------------------------------------------

    def _load_model(self):
        """Load Ollama judge model lazily."""

        if self.llm is None:
            try:
                logger.info(
                    "Loading judge model: %s",
                    self.model_name,
                )

                self.llm = ChatOllama(
                    model=self.model_name,
                    base_url=self.base_url,
                    temperature=self.temperature,
                    format=LLMEvaluationResult.model_json_schema(),
                )

                logger.info("Judge model initialized successfully.")

            except Exception as error:
                logger.exception("Judge model initialization failed.")

                raise RuntimeError(
                    f"Failed to initialize judge model: {error}"
                ) from error

        return self.llm

    # --------------------------------------------------
    # 4. Validate Inputs
    # --------------------------------------------------

    def _validate_inputs(
        self,
        question,
        expected_answer,
        generated_answer,
        context_chunks,
        answerable,
    ):
        """Validate evaluation inputs."""

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be non-empty.")

        if not isinstance(expected_answer, str) or not expected_answer.strip():
            raise ValueError("Expected answer must be non-empty.")

        if not isinstance(generated_answer, str) or not generated_answer.strip():
            raise ValueError("Generated answer must be non-empty.")

        if not isinstance(context_chunks, list):
            raise ValueError("Context chunks must be a list.")

        if not isinstance(answerable, bool):
            raise ValueError("Answerable must be a boolean.")

        for index, chunk in enumerate(context_chunks):

            if isinstance(chunk, str):
                continue

            if not isinstance(chunk, dict):
                raise ValueError(
                    f"Invalid context chunk at index {index}."
                )

            if not isinstance(chunk.get("text"), str):
                raise ValueError(
                    f"Context chunk at index {index} must contain string text."
                )

    # --------------------------------------------------
    # 5. Format Context
    # --------------------------------------------------

    def _format_context(self, context_chunks):
        """Format retrieved chunks."""

        formatted_context = []

        for index, chunk in enumerate(context_chunks, start=1):

            if isinstance(chunk, str):
                text = chunk
            else:
                text = chunk["text"]

            formatted_context.append(
                f"Context {index}:\n{text}"
            )

        return "\n\n".join(formatted_context) or "No context retrieved."

    # --------------------------------------------------
    # 6. Build Judge Prompt
    # --------------------------------------------------

    
    def _build_judge_prompt(
        self,
        question,
        expected_answer,
        generated_answer,
        context,
        answerable,
    ):
        """Build the judge evaluation prompt."""

        return f"""
You are an independent evaluator for a RAG system.

Evaluate the generated answer using the question,
retrieved context and expected answer.

QUESTION:
{question}

EXPECTED ANSWER:
{expected_answer}

GENERATED ANSWER:
{generated_answer}

RETRIEVED CONTEXT:
{context}

ANSWERABLE:
{answerable}

Evaluate these four dimensions independently.

1. FAITHFULNESS:
Check whether factual claims in the generated answer
are supported by the retrieved context.

2. ANSWER RELEVANCY:
Check whether the generated answer directly addresses
the user's question.

3. CONTEXT RELEVANCY:
Check whether the context contains the information
needed to answer the question.

Score 1.0 if the context directly answers the question.
Score 0.5 if it provides only partial information.
Score 0.0 if it is unrelated or provides no useful information.

Do not require extra information beyond the question.

4. ANSWER CORRECTNESS:
Compare the generated answer with the expected answer.
Accept semantically equivalent answers.

SCORING RULES:

- Score must be between 0.0 and 1.0.
- 1.0 means correct or fully supported.
- 0.5 means partially correct.
- 0.0 means incorrect or unsupported.
- Give a short reason for each score.
- Do not invent facts.

IMPORTANT SCORING CONSISTENCY RULES:

- Evaluate the actual meaning, not exact wording.
- Accept semantically equivalent answers.
- If the answer correctly answers the question,
  do not assign 0.0 for answer relevancy.
- If the context explicitly contains the answer,
  do not assign 0.0 for context relevancy.
- If the generated answer matches the expected answer,
  assign 1.0 for answer correctness.
- If factual claims are supported by context,
  assign 1.0 for faithfulness.
- The score MUST agree with its reason.
- Never give score 0.0 when the reason says the answer
  is correct, relevant, supported or equivalent.
- Before returning, check all four scores against
  their reasons and correct any contradiction.

For unanswerable questions:
- Check whether the generated answer correctly abstains.
- If the context confirms that information is not specified,
  consider the context relevant.
- A correct abstention can receive 1.0 for answer relevancy
  and answer correctness.

Return the structured evaluation result only.
"""


    # --------------------------------------------------
    # 7. Evaluate Answer
    # --------------------------------------------------

    def evaluate(
        self,
        question,
        expected_answer,
        generated_answer,
        context_chunks,
        answerable=True,
    ):
        """Evaluate generated answer using an LLM judge."""

        self._validate_inputs(
            question=question,
            expected_answer=expected_answer,
            generated_answer=generated_answer,
            context_chunks=context_chunks,
            answerable=answerable,
        )

        try:
            context = self._format_context(context_chunks)

            prompt = self._build_judge_prompt(
                question=question,
                expected_answer=expected_answer,
                generated_answer=generated_answer,
                context=context,
                answerable=answerable,
            )

            llm = self._load_model()

            logger.info("Starting LLM-based evaluation.")

            response = llm.invoke(prompt)

            print("\n========== JUDGE PROMPT ==========")
            print(prompt)

            print("\n========== RAW JUDGE RESPONSE ==========")
            print(response.content)

            if not isinstance(response.content, str):
                raise ValueError("Judge returned non-text response.")

            if not response.content.strip():
                raise ValueError("Judge returned empty response.")

            result = LLMEvaluationResult.model_validate_json(
                response.content
            )

            logger.info("LLM evaluation completed successfully.")

            return result.model_dump()

        except Exception as error:
            logger.exception("LLM evaluation failed.")

            raise RuntimeError(
                f"Failed to evaluate generated answer: {error}"
            ) from error

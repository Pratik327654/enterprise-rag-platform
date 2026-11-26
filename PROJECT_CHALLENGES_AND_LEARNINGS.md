# Project Challenges & Engineering Learnings

## Enterprise RAG Knowledge & Document Intelligence Platform

> A technical record of the challenges, debugging process, solutions, and engineering learnings encountered while building this project.

---

## 1. About This Document

This document records the real engineering challenges encountered during the development of the Enterprise RAG Knowledge & Document Intelligence Platform.

It focuses on:
- Technical problems encountered during development
- Root cause investigation
- Debugging and troubleshooting approaches
- Solutions implemented
- Lessons learned
- Challenges currently under investigation

This document will be updated as the project evolves.

## 2. Technical Challenges

### 2.1 Document Ingestion and Text Extraction

**Challenge:** Extracting useful information from PDF documents while preserving relevant content and metadata.

**Areas investigated:**
- PDF text extraction
- Document metadata preservation
- Page-level information
- Preparing extracted text for chunking

**Engineering learning:** The quality of extracted document content directly affects downstream chunking and retrieval.

**Status:** Implemented; further improvements may be documented as they arise.

### 2.2 Chunking Strategy

**Challenge:** Splitting documents into meaningful chunks without losing important context.

**Areas investigated:**
- Chunk boundaries
- Context preservation
- Chunk metadata and identifiers
- The effect of chunk size on retrieval

**Engineering learning:** Poor chunk boundaries can separate important information and reduce retrieval effectiveness.

**Status:** Implemented.

### 2.3 Embedding Generation and Vector Storage

**Challenge:** Generating consistent vector embeddings and storing document chunks for semantic retrieval.

**Technology used:**
- Sentence Transformers
- `all-MiniLM-L6-v2`
- ChromaDB
- 384-dimensional normalized embeddings

**Areas investigated:**
- Embedding dimensions
- Document and query embedding consistency
- Vector identifiers
- Metadata storage
- Cosine similarity search

**Engineering learning:** Consistent embeddings and accurate metadata are essential for reliable vector search.

**Status:** Implemented.

### 2.4 Retrieval and Reranking

**Challenge:** Retrieving the most useful information from a collection containing semantically related but conceptually different content.

**Current configuration:**
- Top-K retrieval: 5
- Top-N reranking: 3
- Vector database: ChromaDB

**Observed difficulty:**

A retrieved chunk may be related to the question's topic without containing the exact information required to answer it.

**Engineering learning:** Retrieval relevance and answer relevance are different. Both retrieval and reranking need independent evaluation.

**Status:** Implemented; quality improvements are ongoing.

### 2.5 LLM Answer Generation

**Challenge:** Generating accurate answers from retrieved context, particularly when the document discusses multiple related concepts.

**Observed difficulty:**

The generator may select the wrong concept even when the correct information is present in the retrieved context.

**Example – D02:**

The document discusses multiple data classifications:

- Qualitative and Quantitative Data
- Structured and Unstructured Data
- Raw and Processed Data

The original question, "What are the two main types of data?", was ambiguous.

The smaller generator model produced a different classification instead of the expected answer.

**Investigation:**
- Inspected the source PDF.
- Examined retrieved and reranked chunks.
- Verified the relevant chunk IDs in ChromaDB.
- Updated the evaluation dataset's ground-truth chunk IDs.
- Tested a more specific question.
- Observed the generator's response with the correct information in its retrieved context.

**Current learning:** A RAG system can retrieve the correct information and still generate an incorrect answer. Generator capability and prompt design must also be evaluated.

**Status:** Under investigation.

### 2.6 LLM-as-a-Judge Evaluation

**Challenge:** Obtaining consistent and meaningful evaluation scores from a local LLM judge.

**Observed difficulty:**

The initial judge model sometimes returned zero scores even when its explanations indicated that the generated answer was correct or semantically equivalent.

**Investigation and improvements:**
- Introduced structured Pydantic evaluation schemas.
- Used Ollama structured output.
- Improved scoring consistency instructions in the judge prompt.
- Tested Qwen2.5:3B as an alternative judge to the earlier Llama3.2:1B configuration.

**Engineering learning:** Successful structured output does not automatically mean that the evaluation itself is correct. Judge reliability must be independently tested.

**Status:** Improved; further validation required.

### 2.7 Evaluation Dataset and Ground-Truth Validation

**Challenge:** Ensuring that evaluation labels accurately represent the chunks stored in ChromaDB.

**D02 investigation:**

The original relevant chunk ID in the evaluation dataset could not be found in the current ChromaDB collection.

The investigation involved:
1. Inspecting the ChromaDB collection.
2. Checking the number of stored chunks.
3. Identifying the source document.
4. Searching the stored chunks for the expected information.
5. Locating the relevant content in the source PDF.
6. Updating the D02 relevant chunk IDs.

**Engineering learning:** Incorrect ground-truth labels can distort retrieval evaluation. Dataset identifiers must be verified against the actual vector database.

**Status:** D02 labels updated; broader dataset validation remains important.

### 2.8 Question Ambiguity and Evaluation Design

**Challenge:** Designing questions that identify the intended concept without unintentionally introducing ambiguity.

**Example:**

Original question:

"What are the two main types of data?"

More specific version:

"According to the section on statistical data classification, what are the two broad categories of statistical data?"

**Engineering learning:** Evaluation questions should be clear, specific, and aligned with the intended source content. Question changes must also be reflected in their expected answers and evaluation labels where necessary.

**Status:** Ongoing improvement.

### 2.9 JSON Dataset Debugging

**Challenge:** A JSON decoding error occurred while modifying the evaluation dataset.

**Observed error:**

`JSONDecodeError: Expecting ',' delimiter`

**Troubleshooting:**
- Inspected the reported line number.
- Checked commas and object boundaries.
- Corrected the JSON structure.
- Re-ran the evaluation command.

**Engineering learning:** Dataset validation is an important part of reliable evaluation workflows.

**Status:** Resolved for the encountered issue.

### 2.10 Environment and Docker Configuration

**Challenge:** Configuring the application and its supporting services for containerized execution.

**Areas encountered during development:**
- Docker networking
- Host-to-container communication with Ollama
- Environment configuration
- Persistent storage
- Python dependency installation
- Shell and command-line troubleshooting

**Engineering learning:** A locally working application still needs environment-specific configuration and validation before deployment.

**Status:** Deployment work and validation are ongoing.

---

## 3. Current Investigation: D02

D02 is an important example of debugging multiple stages of a RAG pipeline.

| Investigation stage | Observation |
|---|---|
| Original question | Ambiguous |
| Original relevant chunk ID | Not found in ChromaDB |
| ChromaDB inspection | Correct source document was present |
| Ground-truth correction | Relevant chunk IDs updated |
| More specific question | Tested |
| Retrieval | Correct information appeared in retrieved context |
| Generation | Still produced an incorrect classification |

**Current focus:** Understanding why the generator selects an incorrect classification even when the retrieved context contains the expected answer.

No final resolution has been claimed yet.

---

## 4. Engineering Problem-Solving Approach

The project follows a systematic troubleshooting process:

1. Observe the unexpected behavior.
2. Reproduce the issue.
3. Identify the affected pipeline component.
4. Inspect actual inputs and outputs.
5. Investigate the root cause.
6. Apply the smallest appropriate change.
7. Run focused tests.
8. Validate the result.
9. Document the learning.

This approach helps avoid unnecessary changes to components that are already working.

---

## 5. Key Engineering Learnings

- Successful pipeline execution does not guarantee answer correctness.
- Retrieval quality and generation quality must be evaluated separately.
- Ground-truth dataset labels must match actual stored chunk identifiers.
- Ambiguous questions can affect retrieval and generation.
- Smaller local models may struggle with complex context interpretation.
- LLM-as-a-Judge evaluations require independent validation.
- Structured output validation ensures format consistency, not semantic correctness.
- Debugging individual pipeline stages is more reliable than changing multiple components simultaneously.
- Focused tests help identify regressions before full evaluation.

---

## 6. Challenge Status Tracker

| Area | Current status |
|---|---|
| Document ingestion | Implemented |
| Chunking | Implemented |
| Embedding generation | Implemented |
| ChromaDB integration | Implemented |
| Retrieval | Implemented; under quality investigation |
| Reranking | Implemented; under quality investigation |
| Answer generation | Under investigation |
| LLM-as-a-Judge | Improved; further validation required |
| Dataset ground-truth validation | Ongoing |
| JSON dataset issue | Resolved |
| Docker and deployment | Ongoing |

---

## 7. Future Updates

This document will be maintained throughout the development lifecycle.

Future entries should capture:

- Newly discovered technical challenges
- Root cause analysis
- Experiments performed
- Changes implemented
- Before-and-after results
- Test evidence
- Remaining limitations
- New engineering lessons

---

## Conclusion

Building a reliable RAG platform involves more than connecting an LLM to a vector database.

It requires careful engineering across document processing, embeddings, retrieval, reranking, generation, evaluation, and deployment.

The challenges documented here represent the practical problem-solving journey behind building an enterprise-oriented RAG system.

The objective is not simply to generate answers, but to build a system that retrieves the right information, interprets it correctly, and produces reliable, verifiable responses.

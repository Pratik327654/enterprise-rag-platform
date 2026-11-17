# Enterprise RAG Platform
## Project Foundation & Architecture

### 1. Project Overview
Enterprise RAG Knowledge & Document Intelligence Platform.

Objective: Build a production-oriented RAG system
for enterprise document intelligence.

### 2. Core Infrastructure

| Component | File / Folder | Responsibility |
|---|---|---|
| Project Configuration | pyproject.toml | Metadata and dependencies |
| Environment Variables | .env | Local configuration and secrets |
| Environment Template | .env.example | Configuration reference |
| Git Exclusions | .gitignore | Ignore unnecessary files |
| Central Settings | app/core/config.py | Manage application settings |
| Logging | app/core/logging_config.py | Track application events |
| Exceptions | app/core/exceptions.py | Custom error handling |

### 3. Python Environment
- Virtual environment: venv
- Package manager: pip
- Editable installation configured
- Development dependencies: pytest, ruff

### 4. Application Architecture

- api: Backend API
- core: Shared infrastructure
- ingestion: Document loading and parsing
- chunking: Intelligent text splitting
- embeddings: Vector generation
- vectorstore: Vector storage
- retrieval: Relevant information retrieval
- reranking: Relevance ranking
- generation: LLM response generation
- evaluation: RAG quality evaluation
- monitoring: System monitoring
- security: Access control and security

### 5. Testing
- Logging test implemented
- Custom exception tests implemented
- Pytest configured

### 6. Local AI Configuration
- LLM Runtime: Ollama
- LLM Model: llama3.2:1b
- Embedding Model: all-MiniLM-L6-v2
- Vector Database: ChromaDB

### 7. Current Progress
Foundation architecture established.
Core configuration verified.
Logging tested.
Custom exception tests passed.

### 8. Next Development Phase
Enterprise Document Ingestion & Processing.


## Document Ingestion Engine

### Implemented Components

- File validation using validators.py
- Supported formats: PDF, DOCX, TXT
- PDF text extraction with page-level metadata
- DOCX paragraph extraction
- TXT content extraction
- Automatic loader selection using loader_registry.py
- Standardized extraction output containing text and metadata
- Custom DocumentProcessingError handling

### Validation Rules

- File must exist.
- File extension must be supported.
- Maximum file size: 20 MB.

### Testing Results

- Exception tests: 6 passed
- Validator tests: 6 passed
- Loader tests: 3 passed
- Loader registry tests: 3 passed
- Total: 18 unit tests passed

### Current Limitations

- Scanned PDF OCR is not implemented.
- DOCX table extraction is not implemented.
- Actual PDF text extraction needs a dedicated positive test.
- HTML, CSV, JSON, SQL, XLSX and PPTX loaders are planned.
- File signature and malware validation are not implemented yet.


### 9. Document Extraction Reliability

**Implemented & Tested**

आपण existing Document Ingestion Engine अधिक मजबूत केला.

**1. Actual PDF Text Extraction Testing**

File: `tests/unit/test_loaders.py`

आपण ReportLab वापरून actual text असलेली PDF तयार केली आणि `pypdf` वापरून text extraction verify केले.

खालील गोष्टी test केल्या:

- Actual PDF text extraction.
- Extracted content verification.
- PDF file type metadata.
- Page number metadata.

Test successfully passed.

**2. DOCX Table Extraction**

File: `app/ingestion/loaders.py`

आपण `load_docx()` function update केला.

आता DOCX loader खालील content extract करतो:

- Document paragraphs.
- Document tables.
- Table rows and cells.

Table content standardized text format मध्ये convert केला जातो.

Test file: `tests/unit/test_loaders.py`

DOCX table extraction साठी dedicated unit test तयार केला आणि successfully pass केला.

**3. Combined Unit Testing**

Command:

`python -m pytest tests/unit/ -v`

Final results:

- Exception tests: 6 passed
- Validator tests: 6 passed
- Loader tests: 4 passed
- Loader Registry tests: 3 passed

**Total: 19 unit tests passed.**

### Current Limitations

- Scanned PDF OCR अजून implement केलेले नाही.
- Complex DOCX tables, merged cells आणि nested tables साठी advanced handling बाकी आहे.
- HTML, CSV, JSON, SQL, XLSX आणि PPTX support planned आहे.
- File signature validation आणि malware scanning अजून implement केलेले नाही.

## 10. Document Metadata & Identification

### 10.1 Objective

Implemented a standardized metadata generation utility for identifying and tracking ingested documents across supported file formats.

### 10.2 Implementation

**File: `app/ingestion/metadata.py`**

Implemented `build_document_metadata()` to generate:

- `document_id`: UUID4-based unique document identifier.
- `source`: Original filename.
- `file_type`: Normalized document format.
- `file_size_bytes`: Original file size.
- `ingested_at`: UTC ingestion timestamp.

**File: `app/ingestion/loaders.py`**

Integrated common metadata generation into:

- PDF loader — shared document ID across page-level records, with individual page numbers.
- DOCX loader — common metadata with paragraph and table extraction.
- TXT loader — common metadata with UTF-8 text extraction.

### 10.3 Testing

**File: `tests/unit/test_loaders.py`**

Added tests for:

- Common metadata fields and UUID validity.
- PDF page-level metadata consistency.
- Unique IDs for separate documents.
- Empty TXT document handling.
- Existing PDF, DOCX, TXT, and table extraction behavior.

**Test command:** `python -m pytest tests/unit/ -v`

**Result:** 22 tests passed.

### 10.4 Current Limitations

- Content hashing and duplicate detection are pending.
- OCR for scanned PDFs is not implemented.
- Complex DOCX table structures do not have specialized handling.
- Ingestion timestamp represents processing time, not actual upload time.

### 10.5 Status

**Completed.**

The metadata utility is integrated with all three supported document loaders. All 22 unit tests pass.

**Next:** Document Chunking Engine.

## 5. Document Chunking Engine

### 5.1 Objective

Implemented a document chunking component to split extracted document text into smaller segments suitable for embedding generation and semantic retrieval.

### 5.2 Implementation

**File: `app/chunking/text_splitter.py`**

Implemented `chunk_documents()` using LangChain's `RecursiveCharacterTextSplitter`.

Initial configuration:

- Chunk size: 800 characters.
- Chunk overlap: 150 characters.
- Character-based length function.
- Original text start-index tracking enabled.

### 5.3 Chunk Metadata

Each generated chunk contains:

- Original document metadata.
- Unique UUID4-based `chunk_id`.
- Sequential `chunk_index`.
- Original text `start_index`.

Original document identifiers, source filenames, file types and PDF page numbers are preserved.

PDF page-level records are chunked independently to maintain source-page traceability.

### 5.4 Validation

Implemented validation for:

- Invalid chunk sizes.
- Invalid overlap configuration.
- Invalid document structures.
- Empty and whitespace-only document content.

### 5.5 Testing

**File: `tests/unit/test_chunking.py`**

Added 11 unit tests covering chunk creation, overlap, metadata preservation, unique identifiers, indexing, start positions and input validation.

**Test command:** `python -m pytest tests/unit/ -v`

**Result:** 33 tests passed across the complete unit test suite.

### 5.6 Current Limitations

- Chunk size and overlap are initial configurations and require evaluation-based tuning.
- Character-based splitting is currently used instead of token-based splitting.
- Semantic chunking and cross-page context merging are not implemented.

### 5.7 Status

**Completed.**

The Document Chunking Engine is implemented and integrated as a standalone processing component. All 33 unit tests pass.

**Next:** Embedding Engine.

## 6. Embedding Engine

### 6.1 Objective

Implemented an embedding generation component to convert document chunks into numerical vector representations for semantic retrieval.

### 6.2 Implementation

**File: `app/embeddings/embedding_generator.py`**

Implemented the `EmbeddingGenerator` class using Sentence Transformers.

Configured model:

`sentence-transformers/all-MiniLM-L6-v2`

Key capabilities:

- Lazy model loading and reuse.
- Batch embedding generation.
- Configurable batch size (default: 32).
- NumPy-based vector output.
- Embedding normalization.
- Embedding dimension validation.
- Invalid numerical value detection.
- Original chunk text and metadata preservation.
- Custom embedding error handling.

Expected embedding dimension: **384**.

### 6.3 Testing

**File: `tests/unit/test_embeddings.py`**

Implemented 11 unit tests using a mocked embedding model.

Coverage includes:

- Single and multiple embedding generation.
- Text and metadata preservation.
- Empty input and invalid input handling.
- Batch size validation.
- Model reuse.
- Embedding dimension validation.
- Model failure handling.

**Test command:** `python -m pytest tests/unit/ -v`

**Result:** 44 tests passed across the complete unit test suite.

### 6.4 Actual Model Verification

Downloaded and executed the configured Sentence Transformer model locally.

Verified:

- Successful model loading.
- Actual embedding generation.
- Output shape: `(1, 384)`.
- Embedding dimension: 384.

Actual local model inference was verified separately from mock-based unit testing.

### 6.5 Current Limitations

- Embeddings are currently generated in memory.
- Persistent vector storage is not implemented.
- Retrieval relevance evaluation is pending.
- Batch size requires further performance evaluation.

### 6.6 Status

**Completed.**

The embedding generation component is implemented, all 44 unit tests pass, and actual local model inference has been verified.

**Next:** Vector Store using ChromaDB.

## 5. Milestone 5 — Vector Store with ChromaDB

### 5.1 Objective

Implement a persistent vector storage layer to store document chunk embeddings, original text, and metadata, and enable semantic similarity search.

### 5.2 Technology

- ChromaDB 1.5.9
- Python
- Persistent local storage
- Cosine distance
- Pytest

### 5.3 Implementation

**File:** `app/vectorstore/chroma_store.py`

Implemented the `ChromaVectorStore` class with the following responsibilities:

1. Persistent ChromaDB client initialization.
2. Collection creation and retrieval.
3. Embedding dimension and numerical validation.
4. Metadata validation.
5. Document chunk insertion and updates using `upsert()`.
6. Semantic similarity search using query embeddings.
7. Stored record counting.

**Collection name:** `enterprise_rag_documents`

**Distance metric:** Cosine distance (`hnsw:space = cosine`).

**Storage directory:** Configured through `CHROMA_PERSIST_DIR`.

### 5.4 Data Storage Structure

Each stored record contains:

- Unique chunk ID.
- Original chunk text.
- Document metadata.
- 384-dimensional embedding vector.

The embedding vector is stored as a ChromaDB embedding, while text and metadata are stored in their respective collection fields.

### 5.5 Retrieval Capability

Implemented `similarity_search()` to retrieve the nearest document chunks using query embeddings.

Supported inputs:

- Query embedding.
- Top-K result limit.

Returned information:

- Chunk ID.
- Original document text.
- Metadata.
- Cosine distance.

The implementation returns results ordered by ChromaDB's similarity-search distance.

### 5.6 Validation and Error Handling

Implemented validation for:

- Embedding input type.
- Embedding dimension.
- Invalid numerical values.
- Missing chunk IDs.
- Empty document text.
- Unsupported metadata values.
- Invalid Top-K parameters.

Custom `RetrievalError` exceptions are used for database initialization, storage, search, and counting failures.

### 5.7 Testing

**Test file:** `tests/unit/test_vectorstore.py`

Test coverage includes:

- Collection initialization.
- Single and multiple embedding storage.
- Empty input handling.
- Metadata preservation.
- Similarity search.
- Distance retrieval.
- Invalid input handling.
- Upsert updates.
- Persistence after reinitialization.

**Reported test result:** 59 tests passed across the complete test suite.

### 5.8 Current Limitations

- Complete end-to-end document ingestion and vector storage integration is pending.
- Query embedding generation is not yet integrated into the retrieval workflow.
- Retrieval quality evaluation has not yet been implemented.
- Storage currently uses a local persistent ChromaDB instance.
- Embedding model fine-tuning has not been performed.

### 5.9 Milestone Status

**Status: Implemented and tested.**

The persistent vector storage foundation is ready for integration with the Retrieval Engine.

### 5.10 Next Milestone

**Milestone 6 — Retrieval Engine**

Planned components:

- Query embedding generation.
- Semantic retrieval.
- Metadata-based filtering.
- Top-K result handling.
- Retrieved document context preparation.
- Integration with ChromaDB.

## 6. Milestone 6 — Retrieval Engine

### 6.1 Objective

Implement a retrieval orchestration layer that converts user questions into embeddings and retrieves relevant document chunks from ChromaDB.

The engine coordinates the existing Embedding Generator and Vector Store components.

### 6.2 Technology

- Python
- Sentence Transformers
- ChromaDB 1.5.9
- Logging
- Pytest

Embedding model: `sentence-transformers/all-MiniLM-L6-v2`

Embedding dimension: 384.

### 6.3 Files Implemented

**Main implementation:** `app/retrieval/retriever.py`

Implemented the `DocumentRetriever` class.

**Unit tests:** `tests/unit/test_retrieval.py`

Implemented fake dependencies and unit tests for retrieval orchestration.

**Updated component:** `app/vectorstore/chroma_store.py`

Extended `similarity_search()` with optional metadata filtering through the `where` parameter.

### 6.4 Retrieval Workflow

The retrieval workflow consists of:

1. Accepting a user query.
2. Validating query content and parameters.
3. Removing leading and trailing whitespace.
4. Preparing the query in the format expected by the existing embedding generator.
5. Generating a 384-dimensional query embedding.
6. Passing the embedding to the ChromaDB Vector Store.
7. Performing cosine-distance-based similarity search.
8. Applying an optional metadata filter.
9. Returning retrieved chunks with IDs, text, metadata, and distances.

The query embedding is generated for retrieval and is not stored as a document record.

### 6.5 DocumentRetriever Responsibilities

The `DocumentRetriever` class provides:

- Dependency initialization and injection.
- Query validation.
- Top-K validation.
- Metadata filter validation.
- Query embedding generation.
- Vector Store coordination.
- Retrieved result handling.
- Logging and exception propagation.

Default retrieval limit: 5 chunks.

### 6.6 Dependency Injection

The constructor accepts optional `EmbeddingGenerator` and `ChromaVectorStore` dependencies.

When custom instances are not provided, the class initializes the actual components.

This supports loose coupling and independent testing through fake dependencies.

### 6.7 Metadata Filtering

The retrieval interface supports optional ChromaDB metadata filters.

Example:

`{"source": "employee_policy.pdf"}`

The filter is passed to the Vector Store and forwarded to ChromaDB through the `where` query parameter.

### 6.8 Result Structure

Each retrieved result includes:

- Chunk ID.
- Original document text.
- Document metadata.
- Cosine distance.

The structured results are suitable for subsequent reranking and context preparation.

### 6.9 Testing

**Test file:** `tests/unit/test_retrieval.py`

Testing uses:

- `FakeEmbeddingGenerator`
- `FakeVectorStore`
- Pytest fixtures
- Parametrized tests
- Monkeypatching

Test coverage includes:

- Retrieval result handling.
- Query embedding generation.
- Embedding forwarding.
- Default and custom Top-K.
- Metadata filter forwarding.
- Query whitespace normalization.
- Invalid query handling.
- Invalid Top-K handling.
- Invalid metadata filter handling.
- Empty search results.
- Embedding failure propagation.
- Unexpected embedding count handling.

The test file contains 13 test functions. Parametrized cases expand the executed test count.

### 6.10 Test Results

**User-reported complete project test result: 78 passed.**

All reported tests passed.

The Retrieval Engine unit tests use fake dependencies to verify orchestration independently. Actual end-to-end query execution against documents stored in ChromaDB remains pending.

### 6.11 Current Limitations

- Full document ingestion-to-retrieval integration has not yet been implemented.
- Actual query embedding and persistent ChromaDB search have not yet been verified together through the complete application workflow.
- Retrieval relevance evaluation is pending.
- Reranking is not implemented.
- LLM answer generation is pending.

### 6.12 Milestone Status

**Status: Implemented and unit-tested.**

The Retrieval Engine foundation is ready for subsequent reranking and end-to-end integration work.

### 6.13 Next Milestone

**Milestone 7 — Reranking Engine**

Planned components:

- Retrieved chunk relevance re-evaluation.
- Improved result ordering.
- Best-context selection.
- Preparation of relevant context for LLM generation.

## 7. Milestone 7 — Reranking Engine

### 7.1 Objective

Implement a Cross-Encoder-based reranking component to improve the relevance ordering of candidate document chunks returned by the Retrieval Engine.

### 7.2 Technology

- Python
- Sentence Transformers
- Cross-Encoder
- Pytest
- Logging

**Reranker model:** `cross-encoder/ms-marco-MiniLM-L-6-v2`

### 7.3 Files Implemented

**Main implementation:** `app/reranking/reranker.py`

Implemented the `DocumentReranker` class.

**Unit tests:** `tests/unit/test_reranking.py`

Implemented fake Cross-Encoder dependencies and unit tests.

### 7.4 Reranking Workflow

The reranking workflow consists of:

1. Accepting the original user query.
2. Receiving candidate chunks from the retrieval stage.
3. Validating query and candidate inputs.
4. Creating query-document pairs.
5. Generating relevance scores through the Cross-Encoder.
6. Validating the score count.
7. Sorting candidates in descending score order.
8. Selecting the highest-scoring Top-N chunks.
9. Assigning final reranking positions.

### 7.5 DocumentReranker Responsibilities

Implemented functionality includes:

- Configurable Cross-Encoder model name.
- Optional model dependency injection.
- Lazy model loading.
- Model instance reuse.
- Query and chunk validation.
- Query-document pair preparation.
- Relevance score generation.
- Descending score sorting.
- Top-N result selection.
- Final rank assignment.
- Logging and custom error handling.

### 7.6 Result Structure

Each reranked result preserves:

- Original chunk ID.
- Original text.
- Original metadata.
- Original retrieval distance.

Additional fields:

- `rerank_score`
- `rerank_rank`

The original retrieval distance and reranking score represent different scoring stages and are not interchangeable.

Cross-Encoder scores are used for relative ranking and should not be interpreted as calibrated probabilities.

### 7.7 Unit Testing

**Test file:** `tests/unit/test_reranking.py`

Implemented a `FakeCrossEncoder` to independently test reranking behavior.

Test coverage includes:

- Relevant chunk selection.
- Descending score ordering.
- Score and rank assignment.
- Metadata and retrieval distance preservation.
- Query-document pair creation.
- Top-N selection.
- Empty input handling.
- Input validation.
- Model reuse.
- Model loading failure.
- Prediction failure.
- Score count mismatch.

### 7.8 Actual Model Verification

The configured pretrained Cross-Encoder model was separately loaded and tested through actual inference.

Two query-document pairs were evaluated:

- Annual leave entitlement.
- Company office location.

The user confirmed successful execution and the expected relevance ordering.

### 7.9 Test Results

**User-reported complete project test result: 95 passed.**

The complete test suite passed after the Reranking Engine implementation.

Actual pretrained Cross-Encoder inference was also separately verified.

### 7.10 Current Limitations

- Unit tests use a fake Cross-Encoder for isolated reranking logic.
- Actual pretrained model inference has been separately verified.
- Full integration with actual ChromaDB retrieval results remains pending.
- Domain-specific relevance evaluation has not been implemented.
- Cross-Encoder fine-tuning has not been performed.
- LLM generation is not implemented yet.

### 7.11 Milestone Status

**Status: Implemented, unit-tested, and actual model inference verified.**

The reranking foundation is ready for integration with the Retrieval Engine and subsequent LLM generation workflow.

### 7.12 Next Milestone

**Milestone 8 — LLM Generation Engine**

Planned components:

- Local Llama 3.2 1B integration through Ollama.
- Context preparation from reranked chunks.
- Prompt construction.
- Context-grounded response generation.
- Generation error handling.
- Response formatting.

## 8. Milestone 8 — LLM Generation Engine

### 8.1 Objective

Implement a local LLM generation component that generates context-grounded answers from reranked document chunks and returns source metadata.

### 8.2 Implementation

**Files created:**

| File | Purpose |
|---|---|
| `app/generation/prompt_builder.py` | Builds structured prompts from user queries and document context. |
| `app/generation/generator.py` | Initializes the Ollama model and generates answers. |
| `tests/unit/test_generation.py` | Tests prompt construction and generation behaviour using a fake LLM. |

### 8.3 Model and Configuration

- LLM provider: Ollama
- Model: `llama3.2:1b`
- Integration: LangChain `ChatOllama`
- Model URL: Configured through `OLLAMA_BASE_URL`
- Model name: Configured through `LLM_MODEL`

### 8.4 Key Capabilities

- Context-aware prompt construction.
- Query and context validation.
- Source reference generation.
- Grounding instructions.
- Lazy LLM initialization and reuse.
- Dependency injection for testing.
- Generation error handling.
- Answer and source metadata output.
- Missing-context handling without invoking the LLM.

### 8.5 Output Structure

The generator returns:

- `answer`: Generated answer.
- `sources`: Source ID, document name, page number and chunk ID.
- `model`: Model used for generation.

Source metadata is extracted from the original context chunks by the application, not generated by the LLM.

### 8.6 Validation and Test Results

| Validation | Result |
|---|---|
| Generation unit tests | 18 passed |
| Complete project test suite | 113 passed |
| Actual Ollama inference | Verified |
| Context-based answer | Verified |
| Source metadata extraction | Verified |
| Missing-context behaviour | Verified for manual test case |

### 8.7 Limitations

- Prompt instructions do not guarantee complete hallucination prevention.
- Generated citations are not yet independently validated.
- Manual grounding validation covers only a limited test case.
- Domain-specific answer quality evaluation is pending.
- End-to-end integration of ingestion, embedding, retrieval, reranking and generation remains pending.

### 8.8 Next Steps

- Integrate the individual engines into a complete RAG pipeline.
- Implement end-to-end document ingestion and question answering.
- Add citation validation and answer evaluation.
- Build retrieval and generation quality evaluation.
- Continue with API and application interface development.

## 9. Milestone 9 — End-to-End RAG Pipeline Integration

### 9.1 Objective

Integrate the previously developed RAG engines into a unified pipeline that supports document ingestion, vector storage, retrieval, reranking and grounded LLM generation.

### 9.2 Implementation

**Files created:**

| File | Purpose |
|---|---|
| `app/pipeline/__init__.py` | Initializes the pipeline package. |
| `app/pipeline/rag_pipeline.py` | Orchestrates document ingestion and query processing. |
| `tests/unit/test_pipeline.py` | Tests pipeline orchestration using fake dependencies. |
| `test_rag_integration.py` | Executes actual component integration using a real PDF and local models. |

### 9.3 Document Ingestion Workflow

1. Load PDF, DOCX or TXT documents.
2. Extract document text and metadata.
3. Split documents into chunks.
4. Generate embeddings.
5. Store chunks, embeddings and metadata in ChromaDB.

### 9.4 Query Processing Workflow

1. Accept a user question.
2. Generate query embeddings.
3. Retrieve relevant document chunks.
4. Rerank retrieved chunks using a Cross-Encoder.
5. Generate a context-aware prompt.
6. Generate the answer using Ollama.
7. Return the answer and source metadata.

### 9.5 Architecture Decisions

- Centralized orchestration through `RAGPipeline`.
- Separate ingestion and query operations.
- Shared embedding generator and vector store instances.
- Dependency injection for component testing.
- Isolated temporary ChromaDB directory for integration testing.

### 9.6 Actual Integration Environment

| Component | Technology |
|---|---|
| Document format | PDF |
| Document loader | pypdf |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector database | ChromaDB |
| Retrieval | Cosine similarity |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| LLM | Ollama Llama 3.2 1B |

### 9.7 Integration Test Results

Sample document: `employee_policy_sample.pdf`

- Pages processed: 2
- Chunks created: 5
- Chunks stored: 5
- Retrieved chunks: 5
- Reranked chunks: 3
- Relevant annual leave information identified in the first retrieved and reranked chunk.
- Correct annual leave answer generated: 20 days.
- Source metadata successfully returned.
- Missing-context handling successfully verified.
- Temporary database cleanup issue resolved.

### 9.8 Unit Test Results

Complete project unit test suite: 122 passed.

Actual end-to-end integration was additionally verified using the real document, embedding model, ChromaDB, Cross-Encoder and Ollama LLM.

### 9.9 Current Limitations

- Duplicate document detection and document versioning are not implemented.
- Document deletion and update workflows are pending.
- Citation validation is not implemented.
- Retrieval and answer quality evaluation across a larger dataset is pending.
- Enterprise authentication and authorization are pending.
- API and user interface integration are pending.

### 9.10 Next Steps

- Build a document ingestion API.
- Build a question-answering API.
- Implement document management and duplicate detection.
- Add citation validation and retrieval evaluation.
- Develop the Streamlit user interface.
- Implement monitoring, security and operational controls.

## 10. FastAPI Backend Integration

### 10.1 Objective

Expose the Enterprise RAG Platform through REST APIs using FastAPI, allowing external applications and clients to interact with document ingestion, knowledge retrieval, and question-answering capabilities.

### 10.2 Architecture

The FastAPI backend provides an HTTP interface to the existing RAG service layer.

Request lifecycle:

`Client → FastAPI → RAGPipeline → Retriever → Reranker → LLM Generator → JSON Response`

Document ingestion lifecycle:

`Client → FastAPI → File Validation → RAGPipeline → Document Loader → Chunking → Embeddings → ChromaDB`

### 10.3 Implementation

**Application and lifecycle**
- Created the FastAPI application in `app/api/main.py`.
- Configured application metadata and version information.
- Implemented application lifespan initialization.
- Initialized a shared RAGPipeline instance at application startup.
- Stored the pipeline in `app.state.rag_pipeline`.

**API routes**
- `GET /health` — Application health check.
- `POST /documents/upload` — Document upload and ingestion.
- `GET /documents/count` — Stored chunk count.
- `POST /query` — RAG question answering.

**Request and response validation**

Created Pydantic schemas in `app/api/schemas.py`:
- QueryRequest
- QueryResponse
- SourceResponse
- IngestionResponse
- DocumentCountResponse
- HealthResponse
- ErrorResponse

**API documentation**

FastAPI automatically generates OpenAPI documentation and Swagger UI.

- Swagger UI: `/docs`
- OpenAPI specification: `/openapi.json`

### 10.4 Files

| File | Purpose |
|---|---|
| `app/api/main.py` | FastAPI application and lifespan management |
| `app/api/routes.py` | API route definitions and request handling |
| `app/api/schemas.py` | Pydantic request and response models |
| `tests/unit/test_api.py` | API unit tests |

Additional modifications:
- `app/generation/generator.py` — LLM temperature configured to 0.0.
- `app/generation/prompt_builder.py` — Simplified grounded prompt.
- `tests/unit/test_generation.py` — Updated prompt grounding assertions.

### 10.5 Verification and Test Results

**Unit tests:** 131 passed.

**Manual API verification through Swagger UI:**

| Test | Observed Result | Status |
|---|---|---|
| Health check | HTTP 200, healthy | PASS |
| PDF upload | 2 pages processed | PASS |
| Chunk creation | 5 chunks created | PASS |
| Vector storage | 5 chunks stored | PASS |
| Document count | 5 chunks | PASS |
| Annual leave query | 20 days | PASS |
| Sick leave query | 10 days | PASS |
| Missing CEO information | No unsupported CEO name generated | PASS |

### 10.6 Engineering Findings

During integration testing, the initial LLM prompt produced inconsistent fallback answers despite relevant context being available.

Investigation verified:
- Correct source text was stored in ChromaDB.
- Retrieval returned the relevant annual leave chunk.
- Cross-encoder reranking placed the relevant chunk first.
- The actual generation prompt contained the correct annual leave information.

The prompt was subsequently simplified. Correct answers were obtained in subsequent manual tests.

Temperature was changed from 0.1 to 0.0 as a separate experiment. This change alone did not resolve the issue.

### 10.7 Limitations

- API authentication and authorization are not implemented.
- Rate limiting is not implemented.
- Document duplicate detection and version management are deferred.
- Production deployment and cloud hosting are not implemented.
- Advanced API monitoring and observability are deferred.

### 10.8 Status

**COMPLETED**

The RAG platform is accessible through FastAPI REST endpoints, with Swagger-based manual verification and 131 passing unit tests.

### 10.9 Next Milestone

Prepare the platform for MCP integration by exposing selected RAG capabilities as standardized tools for AI assistants and agents.

# Milestone 11 — MCP Server Integration

**Status:** Completed

## 1. Objective

Integrate the Enterprise RAG Knowledge and Document Intelligence Platform with the Model Context Protocol (MCP), enabling AI clients to interact with existing RAG capabilities through standardized tools.

## 2. Technology

- MCP Python SDK: 2.3.0
- MCP Server API: `MCPServer`
- Transport: STDIO
- Existing RAG pipeline
- ChromaDB
- Sentence Transformers
- Ollama — Llama 3.2 1B

## 3. Architecture

AI Client / MCP Host → MCP Server → Registered MCP Tools → Existing RAG Pipeline

The MCP implementation reuses the existing retrieval, reranking, generation, and vector storage components. No duplicate RAG processing logic was introduced.

## 4. Implemented MCP Tools

### 4.1 ask_knowledge_base_tool

**Purpose:** Generate answers grounded in enterprise documents.

**Implementation:** Calls `RAGPipeline.ask()` with query, retrieval limit, and reranking limit.

### 4.2 search_company_documents_tool

**Purpose:** Retrieve and rerank relevant document chunks.

**Implementation:**
- Calls `DocumentRetriever.retrieve()`.
- Calls `DocumentReranker.rerank()`.
- Returns chunk text, metadata, distance, reranking score, and rank.

### 4.3 get_document_count_tool

**Purpose:** Return the total number of stored document chunks.

**Implementation:** Calls the existing ChromaDB vector store count method.

## 5. Files Created / Updated

| File | Purpose |
|---|---|
| `app/mcp/__init__.py` | MCP package initialization |
| `app/mcp/server.py` | MCP server initialization, tool registration, and STDIO execution |
| `app/mcp/tools.py` | Three MCP tool implementations and shared pipeline initialization |
| `tests/unit/test_mcp.py` | MCP tool unit tests |
| `scripts/test_mcp_client.py` | MCP client integration test |
| `pyproject.toml` | Added MCP SDK dependency |

## 6. Design Decisions

- Reused the existing RAGPipeline rather than duplicating business logic.
- Reused a shared pipeline instance to avoid repeated component initialization.
- Selected STDIO transport for local MCP development and integration testing.
- Implemented three read-only tools.
- Applied input validation to query and retrieval parameters.
- Deferred document ingestion as an MCP tool to avoid exposing unrestricted filesystem access.

## 7. Testing and Validation

### Unit Tests

MCP unit tests cover:
- Knowledge base question answering.
- Document search and reranking.
- Document count.
- Empty query validation.
- Invalid retrieval limit.
- Invalid reranking limit.

**MCP unit test result:** 6 passed.

### MCP Client Integration Test

The client successfully launched the MCP server using STDIO transport, established communication, discovered all three tools, and executed tool calls.

| Validation | Result |
|---|---|
| MCP server startup | Successful |
| STDIO communication | Successful |
| Tool discovery | 3 tools available |
| Document count | 5 chunks |
| Document search | 3 reranked chunks returned |
| Answer generation | Correct answer: 20 annual leave days per year |
| Complete project test suite | 137 passed |

## 8. Limitations

- Local STDIO transport only.
- No remote HTTP transport configuration.
- No MCP authentication or authorization layer.
- Document ingestion is not exposed through MCP.
- Only three read-only MCP tools are currently available.

## 9. Next Steps

- Add a secure document ingestion MCP tool with approved-directory restrictions.
- Evaluate MCP resource and prompt capabilities.
- Explore Streamable HTTP transport for remote integrations.
- Introduce authentication and authorization before remote deployment.
- Integrate the MCP server with a compatible external AI client.

## 10. Milestone Completion

**Milestone 11 — MCP Server Integration: COMPLETED**

The platform now exposes its existing RAG functionality through three MCP tools while retaining its FastAPI REST backend.

The MCP server has been validated through unit tests and an actual STDIO client integration test. The complete project test suite passed with 137 tests.


## 11. LangGraph Workflow Orchestration

### 11.1 Objective

Integrate LangGraph into the existing Enterprise RAG Knowledge and Document Intelligence Platform to orchestrate retrieval, reranking, context checking and answer generation through a state-based workflow.

The implementation reuses the existing RAG components rather than duplicating retrieval or generation logic.

### 11.2 Architecture

The final workflow is:

```text
START
  |
  v
Retrieve Documents
  |
  v
Rerank Documents
  |
  v
Check Context Availability
  |
  +--------------------------+
  |                          |
Context Available       Context Missing
  |                          |
  v                          v
Generate Answer         Safe Fallback
  |                          |
  +-------------+------------+
                |
                v
               END
```

### 11.3 Implementation

**Core LangGraph concepts used:**

- **State:** Shared TypedDict structure used to pass query, retrieved chunks, reranked chunks, answer, sources, model and status between nodes.
- **Nodes:** Independent processing functions for retrieval, reranking, context checking, answer generation and insufficient-context handling.
- **Edges:** Define sequential execution between workflow nodes.
- **Conditional edges:** Route execution to answer generation or safe fallback based on context availability.
- **Graph compilation:** Converts the StateGraph builder into an executable graph.
- **Graph invocation:** Executes the compiled workflow using an initial state.

### 11.4 Files Created or Updated

| File | Purpose |
|---|---|
| `app/graph/__init__.py` | Python package initialization |
| `app/graph/state.py` | Shared workflow state |
| `app/graph/nodes.py` | Retrieval, reranking, context checking, generation and fallback nodes |
| `app/graph/edges.py` | Context-based conditional routing |
| `app/graph/_workflow.py` | Graph construction, compilation, caching and invocation |
| `app/generation/generator.py` | Existing LLM generation implementation restored without the experimental answer validator |
| `tests/unit/test_graph.py` | Graph unit tests |
| `test_llm_generation.py` | Root-level generator unit tests |
| `run_langgraph_integration.py` | Actual LangGraph integration tests |
| `pyproject.toml` | Project dependency configuration updated during the milestone |

### 11.5 Runtime Design

The workflow uses the existing local Ollama model:

- Model: `llama3.2:1b`
- Retrieval: Existing `DocumentRetriever`
- Reranking: Existing `DocumentReranker`
- Generation: Existing `LLMGenerator`

The compiled graph is reused through a shared graph instance.

When no reranked context is available, the graph returns an insufficient-context response without invoking the LLM.

### 11.6 Design Decisions and Limitations

A separate LLM-based answer-validation node was experimentally introduced and tested.

The local 1B model incorrectly classified a supported annual-leave answer as unsupported. The validation node was therefore removed from the final implementation to avoid adding unreliable complexity.

The final workflow checks context availability but does not independently verify every factual claim generated by the LLM.

This is a documented limitation and a possible future enhancement.

### 11.7 Testing and Verification

**Unit tests**

- Graph answer-generation path.
- Missing-context path.
- Empty-query validation.
- Invalid `top_k` validation.
- Invalid `top_n` validation.
- Conditional routing.

The complete project pytest suite completed successfully:

**147 passed**

**Integration tests**

Two real-model integration scenarios were executed using the local Ollama model.

| Scenario | Expected result | Observed result |
|---|---|---|
| Annual leave query | 20 days per calendar year | Correct answer; `success` |
| CEO query | Missing-information response | Correct abstention; `success` |

Source metadata was returned in both integration scenarios.

**Integration result: 2 passed**

### 11.8 Version Control

- Branch: `feature/langgraph-rag`
- Commit: `Simplify LangGraph RAG workflow`
- GitHub push: Successful
- Branch status at documentation time: One commit ahead of `main`
- Merge into `main`: Not yet performed

### 11.9 Milestone Status

**Status: COMPLETED**

LangGraph orchestration has been implemented, unit-tested and verified through actual integration tests.

The workflow is intentionally kept lightweight and reuses the existing RAG architecture.

### 11.10 Next Steps

Potential future engineering milestones include:

- Docker-based application packaging.
- Application observability and structured metrics.
- Prometheus and Grafana monitoring.
- Infrastructure provisioning with Terraform.
- CI/CD pipeline and deployment automation.
- Kubernetes deployment and GitOps using Argo CD.

These items are planned future work and are not included in this completed milestone.


# Observability & Monitoring

## 1. Objective

Integrate application-level monitoring and observability into the Enterprise RAG Platform using Prometheus and Grafana.

The objective is to measure API performance, monitor RAG pipeline execution stages, track server errors, and visualize operational metrics through a centralized dashboard.

## 2. Architecture

**Monitoring Flow:**

FastAPI Application → Prometheus Metrics Endpoint → Prometheus Server → Grafana Dashboard

Components:

- FastAPI middleware for HTTP request instrumentation.
- Prometheus Client for application metric collection.
- Prometheus Server for metric scraping and time-series storage.
- Grafana for metric visualization.
- Docker Compose for local monitoring infrastructure.

## 3. Metrics Implemented

| Metric | Type | Purpose |
|---|---|---|
| `rag_api_requests_total` | Counter | Total HTTP requests grouped by method, endpoint and status |
| `rag_api_request_duration_seconds` | Histogram | HTTP request processing duration |
| `rag_api_errors_total` | Counter | HTTP server errors (status 500 and above) |
| `rag_pipeline_stage_duration_seconds` | Histogram | Individual RAG pipeline stage execution duration |

### Pipeline stages monitored

**Document ingestion**
- document_loading
- chunking
- embedding
- vector_storage

**Query processing**
- retrieval
- reranking
- generation

## 4. Implementation

### FastAPI Instrumentation

Updated `app/api/main.py` with HTTP middleware using `perf_counter()`.

The middleware records request count, response status, processing duration and server errors.

Exposed the Prometheus metrics endpoint at `/metrics`.

The metrics endpoint is excluded from the custom HTTP request instrumentation to avoid self-monitoring overhead.

### RAG Pipeline Instrumentation

Updated `app/pipeline/rag_pipeline.py` with a shared stage measurement helper.

The helper records execution duration for document ingestion and query processing stages while reusing existing pipeline operations.

Duration observations are recorded in a `finally` block to capture execution time even when an operation raises an exception.

### Prometheus

Added `monitoring/prometheus.yml`.

Configured the `enterprise-rag-api` scrape job to collect metrics from the FastAPI service through `host.docker.internal:8000`.

Prometheus target health was manually verified as `UP`.

### Grafana

Added a custom RAG dashboard and dashboard provisioning configuration.

Dashboard panels:

1. Total API Requests
2. API Request Rate
3. API 95th Percentile Latency
4. RAG Pipeline Stage Duration
5. API Server Errors

Prometheus datasource connectivity was verified successfully. Dashboard queries were manually executed and saved.

### Docker Compose

Added `docker-compose.monitoring.yml` to run Prometheus and Grafana.

Configuration includes:
- Prometheus port 9090.
- Grafana port 3000.
- Persistent storage volumes.
- Seven-day Prometheus retention.
- 256 MB memory limit per service.
- Automatic container restart policy.

## 5. Files

| File | Purpose |
|---|---|
| `app/monitoring/metrics.py` | Central Prometheus metric definitions |
| `app/api/main.py` | HTTP request instrumentation and `/metrics` endpoint |
| `app/pipeline/rag_pipeline.py` | RAG stage duration instrumentation |
| `monitoring/prometheus.yml` | Prometheus scrape configuration |
| `monitoring/grafana/rag-dashboard.json` | Grafana dashboard definition |
| `monitoring/grafana/provisioning/dashboards/dashboard.yml` | Dashboard provisioning |
| `docker-compose.monitoring.yml` | Prometheus and Grafana services |
| `tests/unit/test_monitoring.py` | Monitoring endpoint and metric tests |
| `tests/unit/test_api.py` | API test updates |
| `pyproject.toml` | Prometheus client dependency |

## 6. Testing and Verification

- Full project test suite: **150 tests passed**.
- Prometheus `/metrics` endpoint manually verified.
- Prometheus scrape target verified as `UP`.
- Prometheus metric queries returned data after API and RAG operations.
- Grafana Prometheus datasource connection test succeeded.
- Dashboard panels manually queried and saved.
- Grafana container verified in running state with zero restart count at final status verification.

## 7. Limitations and Follow-up Work

1. Datasource provisioning through YAML was not reliably verified on a fresh Grafana deployment. The working local setup uses a manually configured datasource and persisted Grafana volume.
2. The local datasource backup file is excluded from Git and is not part of the deployment configuration.
3. Grafana credentials require environment-based configuration before production deployment.
4. Pipeline stage duration metrics need additional independent unit-test coverage.
5. HTTP error monitoring currently counts status codes of 500 and above; client-side 4xx errors are not included.
6. Alerting rules, distributed tracing, and production monitoring security remain future improvements.

## 8. Git Status

- Branch: `feature/observability-monitoring`
- Commit: `245fa16` — `feat: add Prometheus and Grafana monitoring`
- Implementation commit pushed to the remote feature branch.
- Main branch has not been merged or modified by this milestone.


# Project Foundation — Enterprise RAG Platform

## 1. Project Overview

The Enterprise RAG Platform is a document intelligence application that enables users to upload documents and retrieve context-aware answers using Retrieval-Augmented Generation (RAG).

The platform combines document ingestion, text chunking, embedding generation, vector storage, retrieval, reranking, and LLM-based response generation.

It exposes its functionality through a FastAPI application and includes monitoring through Prometheus and Grafana.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Language | Python |
| LLM Runtime | Ollama |
| LLM Model | llama3.2:1b |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Reranking | CrossEncoder |
| Workflow Orchestration | LangGraph |
| Monitoring | Prometheus |
| Visualization | Grafana |
| Containerization | Docker |
| Multi-container Management | Docker Compose |

## 3. High-Level Architecture

The platform consists of three primary runtime services:

1. **API Service:** Handles document uploads and RAG queries.
2. **Prometheus:** Collects application metrics.
3. **Grafana:** Visualizes the collected metrics through dashboards.

The API communicates with Ollama running on the host machine. ChromaDB and uploaded documents are persisted using mounted storage.

## 4. RAG Workflow

The document processing and question-answering pipeline includes:

1. Document ingestion
2. Text extraction and chunking
3. Embedding generation
4. Vector storage
5. Relevant document retrieval
6. Cross-encoder reranking
7. Context validation
8. LLM response generation

The LangGraph workflow uses the following nodes:

- `retrieve`
- `rerank`
- `check_context`
- `generate`
- `insufficient_context`

The context validation step determines whether the workflow should generate an answer or return an insufficient-context response.

## 5. Dockerization

The application is containerized using a Dockerfile and Docker Compose.

### Dockerfile

The Dockerfile defines the application image, Python runtime, system dependencies, project installation, working directory, and API startup command.

### .dockerignore

The `.dockerignore` file excludes unnecessary local files and directories from the Docker build context, including local environments, Git metadata, environment files, local databases, and development artifacts.

### Docker Compose Services

| Service | Container | Port |
|---|---|---:|
| API | enterprise-rag-api | 8000 |
| Prometheus | rag-prometheus | 9090 |
| Grafana | rag-grafana | 3000 |

### Service Connectivity

The API connects to Ollama through:

`http://host.docker.internal:11434`

Prometheus scrapes the API using the Docker Compose service hostname:

`api:8000`

### Persistent Storage

The deployment uses persistent mounts and named volumes for:

- ChromaDB data
- Uploaded documents
- Hugging Face model cache
- Prometheus time-series data
- Grafana data

This prevents important application and monitoring data from being tied only to the lifecycle of an individual container.

## 6. Monitoring

Prometheus collects API and RAG pipeline metrics.

The monitoring setup includes:

- API request counts
- API request duration
- API error metrics
- RAG pipeline stage duration

Grafana provides dashboards for monitoring request activity, latency, errors, and pipeline-stage performance.

The pipeline-stage duration metric tracks the existing pipeline stages, including document loading, chunking, embedding, vector storage, retrieval, reranking, and generation.

The current dashboard visualizes available observations. A missing observation for a stage should not be interpreted as a zero-duration operation.

## 7. API and Validation

The FastAPI application is accessible through:

- Health endpoint: `/health`
- API documentation: `/docs`
- Prometheus metrics: `/metrics`

Validation performed:

- Docker Compose configuration validation
- API image build
- Container startup and health verification
- Prometheus target verification
- Grafana dashboard verification
- PDF document upload
- RAG question-answering tests
- Document persistence verification after API container restart

## 8. Deployment Commands

```powershell
docker compose config
docker compose build api
docker compose up -d
docker compose ps
```

To inspect API logs:

```powershell
docker compose logs api
```

To restart the API:

```powershell
docker compose restart api
```

## 9. Current Deployment Status

The API, Prometheus, and Grafana containers have been started successfully.

The API health check is passing, Prometheus can scrape the API, and Grafana displays the available monitoring data.

A PDF upload created and stored five additional chunks. The document count increased from 10 to 15 and remained at 15 after restarting the API container, verifying persistent ChromaDB storage.

## 10. Future Scope

Potential future improvements include:

- More comprehensive automated integration testing
- Improved observability and alerting
- Production deployment configuration
- Authentication and authorization
- Performance and resource optimization

---

**Project:** Enterprise RAG Platform  
**Documentation:** Project Foundation and Deployment Overview
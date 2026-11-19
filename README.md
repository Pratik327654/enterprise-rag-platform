# Enterprise RAG Platform

An end-to-end Retrieval-Augmented Generation (RAG) platform for intelligent document processing, semantic search, and context-aware question answering using Large Language Models.

The platform combines vector search, document retrieval, reranking, LangGraph workflow orchestration, and LLM-based response generation. It also includes application monitoring and Docker-based deployment.

## Key Features

- **Document Intelligence:** Upload and process PDF, DOCX, and TXT documents.
- **Semantic Search:** Generate embeddings and store document chunks in ChromaDB.
- **Retrieval-Augmented Generation:** Generate context-aware answers using retrieved document information.
- **Reranking:** Improve retrieval relevance using a CrossEncoder reranker.
- **LangGraph Workflow:** Orchestrate retrieval, reranking, context validation, and conditional response generation.
- **LLM Integration:** Use Ollama for local LLM inference.
- **MCP Integration:** Support Model Context Protocol integration.
- **Monitoring:** Track API performance and RAG pipeline metrics using Prometheus and Grafana.
- **Dockerization:** Run the API and monitoring services using Docker Compose.
- **Persistent Storage:** Preserve vector database, uploaded documents, and monitoring data.


  ## Monitoring Dashboard

The platform includes Grafana dashboards for monitoring API performance and RAG pipeline execution.

![Grafana Monitoring Dashboard](docs/images/grafana-dashboard.png)

 ### API Documentation (Swagger UI)

The platform provides interactive API documentation using FastAPI Swagger UI.

![Swagger API Documentation](docs/images/swagger-api.png)

## System Architecture

```text
                    USER
                     |
                     v
                  FASTAPI
                 /       \
                /         \
       DOCUMENT PROCESSING  RAG QUERY
              |               |
          CHUNKING          LANGGRAPH
              |               |
          EMBEDDINGS       RETRIEVAL
              |               |
           CHROMADB       RERANKING
                              |
                       CONTEXT VALIDATION
                              |
                          OLLAMA LLM
                              |
                       GENERATED ANSWER

       MONITORING: PROMETHEUS --> GRAFANA
```

## RAG Workflow

The platform uses a LangGraph-based workflow to manage the question-answering process.

1. **Retrieve:** Fetch relevant document chunks from ChromaDB.
2. **Rerank:** Reorder retrieved chunks using a CrossEncoder model.
3. **Context Validation:** Check whether sufficient relevant context is available.
4. **Generate:** Generate a grounded response using the local LLM.
5. **Insufficient Context:** Return an appropriate response when the retrieved context is insufficient.

### LangGraph Nodes

- `retrieve`
- `rerank`
- `check_context`
- `generate`
- `insufficient_context`

## Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| LLM Runtime | Ollama |
| LLM Model | llama3.2:1b |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Reranking | CrossEncoder |
| Workflow Orchestration | LangGraph |
| Monitoring | Prometheus |
| Visualization | Grafana |
| Containerization | Docker |
| Container Management | Docker Compose |
| Testing | Pytest |

## Project Structure

```text
enterprise-rag-platform/
│
├── app/
│   ├── api/
│   ├── generation/
│   ├── graph/
│   ├── monitoring/
│   └── pipeline/
│
├── data/
│   └── raw/
│
├── docs/
│   └── PROJECT_FOUNDATION.md
│
├── monitoring/
│   ├── grafana/
│   └── prometheus.yml
│
├── scripts/
├── tests/
│   └── unit/
│
├── .dockerignore
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── docker-compose.monitoring.yml
├── pyproject.toml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker Desktop
- Ollama
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Pratik327654/enterprise-rag-platform.git
cd enterprise-rag-platform
```

### 2. Configure Environment

Create your local `.env` file using the example configuration:

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables locally. Do not commit your `.env` file or secrets to GitHub.

### 3. Configure Ollama

Install Ollama and download the required model:

```bash
ollama pull llama3.2:1b
```

Ensure Ollama is running and accessible from the Docker environment.

### 4. Start the Application

Build and start the services:

```bash
docker compose up -d --build
```

Check container status:

```bash
docker compose ps
```

## Application Access

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger API Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Metrics Endpoint | http://localhost:8000/metrics |

## Monitoring and Observability

The platform uses Prometheus to collect application metrics and Grafana to visualize them.

### Monitoring Capabilities

- API request counts
- API request duration
- API error metrics
- RAG pipeline stage duration

### RAG Pipeline Stages

- Document Loading
- Chunking
- Embedding
- Vector Storage
- Retrieval
- Reranking
- Generation

Grafana dashboards provide visibility into application performance, request latency, traffic, errors, and available pipeline-stage observations.

## Testing and Validation

The platform has been validated through:

- API health checks
- Document upload testing
- RAG question-answering tests
- LangGraph workflow testing
- Retrieval and reranking validation
- Prometheus target verification
- Grafana dashboard verification
- Docker container health checks
- ChromaDB persistence testing after API container restart

## Docker Services

| Service | Container | Port |
|---|---|---|
| FastAPI | enterprise-rag-api | 8000 |
| Prometheus | rag-prometheus | 9090 |
| Grafana | rag-grafana | 3000 |

Persistent Docker volumes and mounted directories are used to retain application and monitoring data.

## Future Enhancements

- Advanced Agentic AI capabilities
- Multi-Agent workflow orchestration
- Improved authentication and authorization
- Advanced observability and alerting
- Production deployment and scalability improvements

## Author

**Pratik Nichal**

AI Engineering | Generative AI | Machine Learning | RAG | LangGraph

GitHub: [Pratik327654](https://github.com/Pratik327654)

---

If you find this project useful, feel free to explore the repository and its implementation.

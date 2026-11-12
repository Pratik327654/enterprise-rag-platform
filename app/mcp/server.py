
import logging

from mcp.server import MCPServer

from app.mcp.tools import (
    ask_knowledge_base,
    search_company_documents,
    get_document_count,
)

logger = logging.getLogger(__name__)

mcp_server = MCPServer(
    "Enterprise RAG Knowledge and Document Intelligence Platform"
)


@mcp_server.tool()
def ask_knowledge_base_tool(
    query: str,
    top_k: int = 5,
    top_n: int = 3,
) -> dict:
    """Ask a question and receive an answer grounded in company documents."""

    return ask_knowledge_base(
        query=query,
        top_k=top_k,
        top_n=top_n,
    )


@mcp_server.tool()
def search_company_documents_tool(
    query: str,
    top_k: int = 5,
    top_n: int = 3,
) -> list[dict]:
    """Find and rerank relevant chunks from company documents."""

    return search_company_documents(
        query=query,
        top_k=top_k,
        top_n=top_n,
    )


@mcp_server.tool()
def get_document_count_tool() -> dict:
    """Get the total number of chunks stored in the document knowledge base."""

    return get_document_count()


def main():
    logger.info("Starting Enterprise RAG MCP server.")

    mcp_server.run(transport="stdio")


if __name__ == "__main__":
    main()

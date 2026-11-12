

import asyncio
import sys

from mcp import Client, StdioServerParameters


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"],
    )

    print("Connecting to Enterprise RAG MCP Server...")

    async with Client(server_params) as client:

        print("\nMCP connection established!")

        # 1. Discover tools.
        tools_result = await client.list_tools()

        print("\nAvailable MCP tools:")
        for tool in tools_result.tools:
            print(f"- {tool.name}")

        # 2. Test document count.
        print("\n--- DOCUMENT COUNT TEST ---")

        count_result = await client.call_tool(
            "get_document_count_tool",
            {},
        )

        print(count_result.structured_content or count_result.content)

        # 3. Test document search.
        print("\n--- DOCUMENT SEARCH TEST ---")

        search_result = await client.call_tool(
            "search_company_documents_tool",
            {
                "query": "How many annual leave days are provided?",
                "top_k": 5,
                "top_n": 3,
            },
        )

        print(search_result.structured_content or search_result.content)

        # 4. Test RAG answer generation.
        print("\n--- KNOWLEDGE BASE ANSWER TEST ---")

        answer_result = await client.call_tool(
            "ask_knowledge_base_tool",
            {
                "query": "How many annual leave days are provided?",
                "top_k": 5,
                "top_n": 3,
            },
        )

        print(answer_result.structured_content or answer_result.content)


if __name__ == "__main__":
    asyncio.run(main())

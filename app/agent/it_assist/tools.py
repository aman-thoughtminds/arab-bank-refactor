# type: ignore
from time import perf_counter
from typing import Annotated
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command


from app.core.config import settings
from app.agent.clients import async_openai_embedding_client, pc_asyncio


# @tool
# async def similarity_search(
#     query: str,
#     category: Optional[str],
#     state: Annotated[dict, InjectedState],
#     tool_call_id: Annotated[str, InjectedToolCallId],
# ) -> Command:
#     """Perform similarity search in Pinecone and append results to state messages."""

#     new_messages: List[BaseMessage] = []

#     if not query.strip():
#         new_messages.append(
#             ToolMessage(content="Query is empty.", tool_call_id=tool_call_id)
#         )
#     else:
#         pinecone_filter = {}
#         if category:
#             pinecone_filter["category"] = category.upper()

#         try:
#             # Step 1: Get embedding from OpenAI
#             vector_response = await async_openai_embedding_client.embeddings.create(
#                 model="text-embedding-ada-002", input=query
#             )
#             query_vector = vector_response.data[0].embedding

#             # Step 2: Describe and query the index
#             index_description = await pc_asyncio.describe_index(
#                 name=settings.PINECONE_INDEX_NAME
#             )
#             index = pc_asyncio.IndexAsyncio(
#                 host=index_description.host, name=settings.PINECONE_INDEX_NAME
#             )

#             response = await index.query_namespaces(
#                 vector=query_vector,
#                 namespaces=[
#                     settings.PINECONE_NAMESPACE,
#                     f"{settings.PINECONE_NAMESPACE}-summarized",
#                     f"{settings.PINECONE_NAMESPACE}-solution-testing",
#                 ],
#                 top_k=5,
#                 include_metadata=True,
#                 filter=pinecone_filter if pinecone_filter else None,
#                 metric="cosine",
#             )

#             matches = response.matches or []
#             if not matches:
#                 new_messages.append(
#                     ToolMessage(content="No matches found.", tool_call_id=tool_call_id)
#                 )
#             else:
#                 for m in matches:
#                     content = (
#                         f"Category: {m.metadata.get('category', 'N/A')}\n"
#                         f"Problem: {m.metadata.get('problem', 'N/A')}\n"
#                         f"Solution: {m.metadata.get('solution', 'N/A')}\n"
#                         f"Reference URL: {m.metadata.get('referrence_url', 'N/A')}"
#                     )
#                     new_messages.append(
#                         ToolMessage(content=content, tool_call_id=tool_call_id)
#                     )

#         except Exception as e:
#             new_messages.append(
#                 ToolMessage(
#                     content=f"Similarity search failed: {str(e)}",
#                     tool_call_id=tool_call_id,
#                 )
#             )

#     # Return Command with new messages to be merged via `add_messages`
#     return Command(add_messages=new_messages)


@tool
async def general_similarity_search(
    query: str,
    agent_state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Performs similarity search across general-purpose namespaces using Pinecone's async gRPC client."""

    try:
        # Step 1: Get embedding
        start = perf_counter()
        vector_response = await async_openai_embedding_client.embeddings.create(
            model="text-embedding-ada-002", input=query
        )
        query_vector = vector_response.data[0].embedding

        # Step 2: Get Pinecone index
        index = pc_asyncio.IndexAsyncio(
            host=settings.PINECONE_HOST_URL,
            name=settings.PINECONE_INDEX_NAME,
        )

        # Step 3: Query Pinecone
        response = await index.query_namespaces(
            vector=query_vector,
            namespaces=[
                settings.PINECONE_NAMESPACE,
                f"{settings.PINECONE_NAMESPACE}-solution-testing",
            ],
            top_k=3,
            include_metadata=True,
            metric="cosine",
        )

        matches = response.matches or []
        if not matches:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="No relevant results found.",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

        contents = []
        for m in matches:
            content = (
                f"Category: {m.metadata.get('category', 'N/A')}\n"
                f"Problem: {m.metadata.get('problem', 'N/A')}\n"
                f"Solution: {m.metadata.get('solution', 'N/A')}\n"
                f"Reference URL: {m.metadata.get('referrence_url', 'N/A')}"
            )
            contents.append(content)
        agent_state["messages"] = [
            ToolMessage(content="\n\n".join(contents), tool_call_id=tool_call_id)
        ]

        # breakpoint()
        print(
            f"Similarity search took {perf_counter() - start:.4f} seconds"
        )  # Debugging line
        return Command(update=agent_state)

    except Exception as e:
        agent_state["messages"] = [ToolMessage(content=e, tool_call_id=tool_call_id)]
        breakpoint()
        return Command(update=agent_state)
    finally:
        await pc_asyncio.close()

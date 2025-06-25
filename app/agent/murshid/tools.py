# type: ignore
from typing import List, Annotated
from langchain_core.messages import ToolMessage, BaseMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command


from app.core.config import settings
from app.agent.object_facotry import pc_asyncio, async_openai_embedding_client


@tool
async def similarity_search(
    query: str,
    category: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Perform similarity search in Pinecone and append results to state messages."""

    new_messages: List[BaseMessage] = []

    if not query.strip():
        new_messages.append(
            ToolMessage(content="Query is empty.", tool_call_id=tool_call_id)
        )
    else:
        pinecone_filter = {}
        if category:
            pinecone_filter["category"] = category.upper()

        try:
            # Step 1: Get embedding from OpenAI
            vector_response = await async_openai_embedding_client.embeddings.create(
                model="text-embedding-ada-002", input=query
            )
            query_vector = vector_response.data[0].embedding

            # Step 2: Describe and query the index
            index_description = await pc_asyncio.describe_index(
                name=settings.PINECONE_INDEX_NAME
            )
            index = pc_asyncio.IndexAsyncio(
                host=index_description.host, name=settings.PINECONE_INDEX_NAME
            )

            response = await index.query_namespaces(
                vector=query_vector,
                namespaces=[
                    settings.PINECONE_NAMESPACE,
                    f"{settings.PINECONE_NAMESPACE}-summarized",
                    f"{settings.PINECONE_NAMESPACE}-solution-testing",
                ],
                top_k=5,
                include_metadata=True,
                filter=pinecone_filter if pinecone_filter else None,
                metric="cosine",
            )

            matches = response.matches or []
            if not matches:
                new_messages.append(
                    ToolMessage(content="No matches found.", tool_call_id=tool_call_id)
                )
            else:
                for m in matches:
                    content = (
                        f"Category: {m.metadata.get('category', 'N/A')}\n"
                        f"Problem: {m.metadata.get('problem', 'N/A')}\n"
                        f"Solution: {m.metadata.get('solution', 'N/A')}\n"
                        f"Reference URL: {m.metadata.get('referrence_url', 'N/A')}"
                    )
                    new_messages.append(
                        ToolMessage(content=content, tool_call_id=tool_call_id)
                    )

        except Exception as e:
            new_messages.append(
                ToolMessage(
                    content=f"Similarity search failed: {str(e)}",
                    tool_call_id=tool_call_id,
                )
            )

    # Return Command with new messages to be merged via `add_messages`
    return Command(add_messages=new_messages)


# async def similarity_search_for_general_questions(
#     query: str,
# ) -> Tuple[List[str], List[str]]:
#     """Performs similarity search across general-purpose namespaces using Pinecone's async gRPC client."""
#     if not query.strip():
#         return ["Query is empty."], []

#     try:
#         # Step 1: Get embedding
#         vector_response = await async_openai_embedding_client.embeddings.create(
#             model="text-embedding-ada-002", input=query
#         )
#         query_vector = vector_response.data[0].embedding
#         index_description = await pc_asyncio.describe_index(
#             name=settings.PINECONE_INDEX_NAME
#         )

#         # Step 2: Get async Pinecone index
#         index = pc_asyncio.IndexAsyncio(
#             host=index_description.host, name=settings.PINECONE_INDEX_NAME
#         )

#         # Step 3: Query across multiple namespaces using query_namespaces
#         response = await index.query_namespaces(
#             vector=query_vector,
#             namespaces=[
#                 settings.PINECONE_NAMESPACE,
#                 f"{settings.PINECONE_NAMESPACE}-solution-testing",
#             ],
#             top_k=3,
#             include_metadata=True,
#             metric="cosine",
#         )

#         # Step 4: Process results
#         matches = response.matches or []
#         if not matches:
#             return ["No matches found."], []

#         results_list = [
#             f"Category: {m.metadata.get('category', 'N/A')}\n"
#             f"Problem: {m.metadata.get('problem', 'N/A')}\n"
#             f"Solution: {m.metadata.get('solution', 'N/A')}\n"
#             f"Reference URL: {m.metadata.get('referrence_url', 'N/A')}\n"
#             for m in matches
#         ]
#         category_list = list(
#             {m.metadata.get("category") for m in matches if m.metadata.get("category")}
#         )

#         return results_list, category_list

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Similarity search for general questions failed: {str(e)}",
#         )

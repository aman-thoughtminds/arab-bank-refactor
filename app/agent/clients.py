"""
This module initializes and provides clients for external services used in the application.

Clients:
- `async_openai_embedding_client`: An asynchronous client for Azure OpenAI embeddings, configured with API key, endpoint, and API version from application settings.
- `pc_asyncio`: An asynchronous Pinecone client for vector database operations, initialized with the API key from application settings.

"""

from langchain_openai import AzureChatOpenAI
from langfuse.openai import AsyncAzureOpenAI
from pinecone import PineconeAsyncio
from app.core import settings

async_openai_embedding_client = AsyncAzureOpenAI(
    api_key=settings.AZURE_OPENAI_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_EMBEDDING_VERSION,
)

azure_openai_client = AzureChatOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    api_version=settings.AZURE_OPENAI_GPT4o_VERSION,
    azure_deployment="gpt-4o-mini",
    temperature=0.7,
)

pc_asyncio = PineconeAsyncio(api_key=settings.PINECONE_API_KEY)

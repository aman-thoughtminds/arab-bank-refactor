from langfuse.openai import AsyncAzureOpenAI
from pinecone import PineconeAsyncio

from app.core import settings

async_openai_embedding_client = AsyncAzureOpenAI(
    api_key=settings.AZURE_OPENAI_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_EMBEDDING_VERSION,
)

# pc = Pinecone(api_key=settings.PINECONE_API_KEY)
# pc_index = pc.Index(settings.PINECONE_INDEX_NAME)
# Create Pinecone gRPC client once
# pc_grpc = PineconeGRPC(api_key=settings.PINECONE_API_KEY)
# pc_grpc_index = pc_grpc.Index(name=settings.PINECONE_INDEX_NAME, pool_threads=20)
pc_asyncio = PineconeAsyncio(api_key=settings.PINECONE_API_KEY)

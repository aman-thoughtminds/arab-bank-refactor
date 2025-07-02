import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Langgraph Demo"
    PROJECT_VERSION: str = "0.0.1"
    API_PREFIX: str = "/api"
    DOMAIN: str

    def HTTP_OR_HTTPS(self) -> str:
        return "http" if self.DOMAIN == "localhost" else "https"

    BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES: int
    BACKEND_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    BACKEND_SECRET_KEY: str
    ENABLE_SSO: str
    BACKEND_URL: str

    ADMIN_USER_NAME: str
    ADMIN_USER_EMAIL: str

    PINECONE_NAMESPACE: str
    PINECONE_INDEX_NAME: str
    PINECONE_API_KEY: str
    PINECONE_HOST_URL: str

    AZURE_TRANSLATE_KEY: str
    AZURE_TRANSLATE_ENDPOINT: str
    BLOB_CONNECTION_STRING: str
    BLOB_CONTAINER_NAME: str
    AZURE_DOC_INTELLIGENCE_ENDPOINT: str
    AZURE_DOC_INTELLIGENCE_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_EMBEDDING_VERSION: str
    AZURE_OPENAI_GPT4o_VERSION: str
    LANGFUSE_PUBLIC_KEY: str = ""

    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    SMTP_PASSWORD: str
    SMTP_USERNAME: str
    SMTP_SERVER: str
    SMTP_PORT: int

    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: str

    class Config:
        case_sensitive = True
        env_file = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            ".env",
        )
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()  # type: ignore

import logging
from time import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from app.db import AsyncPostgresPool
from app.core import settings
from app.api import api_router

# configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the singleton connection pool
    await AsyncPostgresPool.initialize(
        dsn=settings.SQLALCHEMY_DATABASE_URI, min_size=1, max_size=10
    )
    yield
    # Cleanup
    await AsyncPostgresPool.close_pool()


app = FastAPI(
    title="Langraph Agent",
    description="Langgraph agent demo",
    version="0.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ServerErrorMiddleware, handler=None)
app.add_middleware(GZipMiddleware)
app.include_router(api_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time()
    response = await call_next(request)
    process_time = time() - start
    response.headers["x-process-time"] = str(process_time)
    return response


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import export, import_, records


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Kantata Reddit Intelligence API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(records.router, prefix="/records", tags=["records"])
app.include_router(import_.router, prefix="/import", tags=["import"])
app.include_router(export.router, prefix="/export", tags=["export"])


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

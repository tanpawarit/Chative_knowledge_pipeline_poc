"""FastAPI dependency helpers."""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, HTTPException, Request
from piccolo.engine.postgres import PostgresEngine
from qstash import Receiver
from qstash.errors import SignatureError

from src.app.repositories import DocumentsRepository
from src.app.services import PipelineService
from src.app.settings import AppSettings
from src.shared.db.postgres import engine_from_env
from src.shared.storage import StorageClient
from src.shared.logging.logger import get_logger

logger = get_logger("app.qstash")


def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache(maxsize=1)
def _postgres_engine() -> PostgresEngine:
    return engine_from_env(prefix="DB")


def get_postgres_engine() -> PostgresEngine:
    return _postgres_engine()


def get_documents_repository(
    engine: PostgresEngine = Depends(get_postgres_engine),
) -> DocumentsRepository:
    return DocumentsRepository(engine)


@lru_cache(maxsize=1)
def _storage_client() -> StorageClient:
    return StorageClient.from_env()


def get_storage_client() -> StorageClient:
    return _storage_client()


def get_qstash_receiver(
    settings: AppSettings = Depends(get_app_settings),
) -> Receiver:
    signature = settings.qstash_signature
    current = signature.current_signing_key
    next_key = signature.next_signing_key
    if not current or not next_key:
        raise RuntimeError("QStash signing keys must be configured together")
    logger.info("QStash signature verification enabled")
    return Receiver(current, next_key)


def get_pipeline_service(
    settings: AppSettings = Depends(get_app_settings),
    documents: DocumentsRepository = Depends(get_documents_repository),
    storage: StorageClient = Depends(get_storage_client),
) -> PipelineService:
    return PipelineService(
        chunking_settings=settings.chunking,
        embedding_settings=settings.embedding,
        milvus_settings=settings.milvus,
        documents_repo=documents,
        storage_client=storage,
    )


async def get_request_body(request: Request) -> bytes:
    return await request.body()


async def verify_qstash_signature(
    request: Request,
    body: bytes = Depends(get_request_body),
    receiver: Receiver = Depends(get_qstash_receiver),
) -> None:
    signature = request.headers.get("Upstash-Signature")
    if not signature:
        logger.error("Missing Upstash-Signature header")
        raise HTTPException(status_code=401, detail="Missing Upstash signature")

    url_for_verify = _resolve_request_url(request)
    try:
        receiver.verify(signature=signature, body=body.decode("utf-8"), url=url_for_verify)
    except SignatureError as exc:
        logger.exception("Signature verification failed", error=str(exc))
        raise HTTPException(status_code=401, detail="Invalid Upstash signature") from exc


def _resolve_request_url(request: Request) -> str:
    f_proto = request.headers.get("x-forwarded-proto")
    f_host = request.headers.get("x-forwarded-host")
    if f_proto and f_host:
        base = f"{f_proto}://{f_host}{request.url.path}"
        if request.url.query:
            return f"{base}?{request.url.query}"
        return base
    return str(request.url)

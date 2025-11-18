"""Adapter that orchestrates the document embedding pipeline."""

from __future__ import annotations

import anyio

from src.app.domain.events import DocumentEmbeddingEvent
from src.app.repositories import DocumentRecord, DocumentsRepository
from src.document_chunking import generate_document_chunks
from src.document_embedding import embed_chunks
from src.document_extraction.application.extraction_service import extract_markdown
from src.document_store.application.upsert_service import main_upsert
from src.shared.config import ChunkingSettings, EmbeddingSettings, MilvusSettings
from src.shared.logging.logger import get_logger
from src.shared.storage import StorageClient

logger = get_logger(__name__)


class PipelineService:
    """Coordinates the chunking, embedding, and persistence pipeline."""

    def __init__(
        self,
        *,
        chunking_settings: ChunkingSettings,
        embedding_settings: EmbeddingSettings,
        milvus_settings: MilvusSettings,
        documents_repo: DocumentsRepository,
        storage_client: StorageClient,
    ) -> None:
        self._chunking_settings = chunking_settings
        self._embedding_settings = embedding_settings
        self._milvus_settings = milvus_settings
        self._documents = documents_repo
        self._storage = storage_client

    async def run_document_embedding(self, event: DocumentEmbeddingEvent) -> int:
        """Execute the end-to-end pipeline for a document event."""

        return await anyio.to_thread.run_sync(self._run_sync, event)

    def _run_sync(self, event: DocumentEmbeddingEvent) -> int:
        workspace_id = event.workspace_id
        document = self._get_document(event.document_id, workspace_id)
        doc_name = document.filename
        document_id = document.id
        source_uri = document.file_path

        logger.info(
            "Starting embedding pipeline",
            document=doc_name,
            workspace=workspace_id,
        )

        markdown = self._load_markdown(document)
        chunks = generate_document_chunks(
            markdown,
            source=source_uri,
            doc_name=doc_name,
            document_id=document_id,
            settings=self._chunking_settings,
        )
        if not chunks:
            logger.info("No chunks produced", document=doc_name)
            return 0

        embedded_rows = embed_chunks(
            chunks,
            settings=self._embedding_settings,
        )
        if not embedded_rows:
            logger.info("Embedding produced no rows", document=doc_name)
            return 0

        for row in embedded_rows:
            row.setdefault("workspace_id", workspace_id)

        main_upsert(embedded_rows, settings=self._milvus_settings)

        logger.info(
            "Pipeline complete",
            document=doc_name,
            chunks_embedded=len(embedded_rows),
        )
        return len(embedded_rows)

    def _get_document(self, document_id: str, workspace_id: str) -> DocumentRecord:
        try:
            return self._documents.get(document_id=document_id, workspace_id=workspace_id)
        except LookupError as exc:
            raise ValueError(
                f"Document not found for embedding: id={document_id} workspace_id={workspace_id}"
            ) from exc

    def _load_markdown(self, document: DocumentRecord) -> str:
        fetched = self._storage.fetch(document)
        fallback_name = document.file_path.split("/")[-1] or document.file_path
        if "\\" in fallback_name:
            fallback_name = fallback_name.split("\\")[-1]
        filename = document.filename or fallback_name or document.file_path
        return extract_markdown(fetched.data, filename=filename)

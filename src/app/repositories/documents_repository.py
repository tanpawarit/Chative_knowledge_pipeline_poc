"""Repository for loading document metadata from Postgres via Piccolo."""

from __future__ import annotations

from dataclasses import dataclass

from piccolo.engine.postgres import PostgresEngine

from src.app.db import DocumentTable


@dataclass(slots=True)
class DocumentRecord:
    """subset of document metadata required by the pipeline."""

    id: str
    workspace_id: str
    filename: str
    file_extension: str | None
    mime_type: str
    size_bytes: int
    storage_provider: str
    file_path: str
    checksum: str


class DocumentsRepository:
    """Piccolo-powered repository for the `documents` table."""

    def __init__(self, engine: PostgresEngine) -> None:
        self._engine = engine
        DocumentTable._meta.db = engine

    def get(self, *, document_id: str, workspace_id: str) -> DocumentRecord:
        """Return an active document or raise LookupError."""

        query = (
            DocumentTable.objects()
            .where(
                (DocumentTable.id == document_id)
                & (DocumentTable.workspace_id == workspace_id)
                & (DocumentTable.deleted_at.is_null())
            )
            .first()
        )
        row = query.run_sync()
        if row is None:
            raise LookupError(
                f"Document not found: id={document_id} workspace_id={workspace_id}"
            )

        return DocumentRecord(
            id=row.id,
            workspace_id=row.workspace_id,
            filename=row.filename,
            file_extension=row.file_extension,
            mime_type=row.mime_type,
            size_bytes=int(row.size_bytes),
            storage_provider=row.storage_provider,
            file_path=row.file_path,
            checksum=row.checksum,
        )


__all__ = ["DocumentRecord", "DocumentsRepository"]

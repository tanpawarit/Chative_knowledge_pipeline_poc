"""Pydantic models describing webhook events."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentEmbeddingEvent(BaseModel):
    """Payload describing a QStash document embedding job."""

    document_id: str = Field(
        ...,
        alias="documentId",
        serialization_alias="documentId",
    )
    workspace_id: str = Field(
        ...,
        alias="workspaceId",
        serialization_alias="workspaceId",
    )

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "extra": "ignore",
    }

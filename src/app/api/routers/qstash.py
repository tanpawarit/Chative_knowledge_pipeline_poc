"""QStash webhook endpoints."""

from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from src.app.api.dependencies import (
    get_pipeline_service,
    get_request_body,
    verify_qstash_signature,
)
from src.app.domain.events import DocumentEmbeddingEvent
from src.app.services import PipelineService
from src.shared.logging.logger import get_logger

logger = get_logger("app.qstash")

router = APIRouter(prefix="/consume/documents", tags=["qstash"])


@router.post(
    "/embed",
    dependencies=[Depends(verify_qstash_signature)],
)
async def receive_from_qstash(
    body: bytes = Depends(get_request_body),
    pipeline: PipelineService = Depends(get_pipeline_service),
) -> Dict[str, Any]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        logger.exception(
            "Invalid JSON payload from QStash", error=str(exc)
        )
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    try:
        event = DocumentEmbeddingEvent.model_validate(payload)
    except ValidationError as exc:
        logger.exception(
            "Invalid event payload from QStash", error=str(exc)
        )
        raise HTTPException(status_code=422, detail="Invalid event payload") from exc

    logger.info(
        "Received QStash event",
        document_id=event.document_id,
        workspace_id=event.workspace_id,
    )

    chunk_count = await pipeline.run_document_embedding(event)

    return {
        "status": "processed",
        "documentId": event.document_id,
        "workspaceId": event.workspace_id,
        "chunksEmbedded": chunk_count,
    }


@router.get("/healthz")
async def healthz() -> Dict[str, str]:
    return {"status": "ok"}

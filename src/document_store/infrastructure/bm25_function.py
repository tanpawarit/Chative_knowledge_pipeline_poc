"""Helpers for configuring Milvus BM25 sparse embeddings (load-layer)."""

from __future__ import annotations

from typing import Final

from pymilvus import Function, FunctionType

BM25_FUNCTION_NAME: Final[str] = "text_bm25_emb"


def build_bm25_function(
    *,
    input_field: str = "text",
    output_field: str = "sparse_vector",
    name: str = BM25_FUNCTION_NAME,
) -> Function:
    """Return a Milvus function that materializes BM25 sparse vectors."""
    return Function(
        name=name,
        input_field_names=[input_field],
        output_field_names=[output_field],
        function_type=FunctionType.BM25,
    )


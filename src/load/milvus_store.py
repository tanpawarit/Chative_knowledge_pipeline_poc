"""High-level Milvus helpers for storing hybrid embeddings."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from pymilvus import DataType, MilvusClient

from src.embedding.config import MilvusSettings
from src.load.sparse import BM25_FUNCTION_NAME, build_bm25_function


class MilvusStore:
    """Lazy-initialized Milvus client tailored to chunk storage."""

    def __init__(self, settings: MilvusSettings):
        self._settings = settings.ensure_ready()
        token = self._settings.token()
        client_kwargs = {"uri": self._settings.uri}
        if token:
            client_kwargs["token"] = token
        self._client = MilvusClient(**client_kwargs)
        self._collection = self._settings.collection_name
        self._initialized = False

    @property
    def client(self) -> MilvusClient:
        return self._client

    def ensure_collection(self, dense_dim: int) -> None:
        if self._initialized:
            return

        if self._client.has_collection(collection_name=self._collection):
            self._validate_dimension(dense_dim)
            self._initialized = True
            return

        schema = self._client.create_schema(
            auto_id=False,
            enable_dynamic_fields=False,
        )
        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            max_length=64,
        )
        schema.add_field(
            field_name="text",
            datatype=DataType.VARCHAR,
            max_length=65535,
            enable_analyzer=True,
        )
        schema.add_field(
            field_name="metadata",
            datatype=DataType.JSON,
        )
        schema.add_field(
            field_name="dense_vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=dense_dim,
        )
        schema.add_field(
            field_name="sparse_vector",
            datatype=DataType.SPARSE_FLOAT_VECTOR,
        )

        schema.add_function(
            build_bm25_function(
                input_field="text",
                output_field="sparse_vector",
            )
        )

        index_params = self._client.prepare_index_params()
        index_params.add_index(
            field_name="dense_vector",
            index_name="dense_autoindex",
            index_type="AUTOINDEX",
            metric_type=self._settings.dense_metric,
        )
        index_params.add_index(
            field_name="sparse_vector",
            index_name="sparse_bm25_index",
            index_type="AUTOINDEX",
            metric_type=self._settings.sparse_metric,
        )

        self._client.create_collection(
            collection_name=self._collection,
            schema=schema,
            index_params=index_params,
            consistency_level=self._settings.consistency_level,
        )
        self._initialized = True

    def _validate_dimension(self, dense_dim: int) -> None:
        try:
            info = self._client.describe_collection(collection_name=self._collection)
        except Exception:
            # Best-effort validation only; if the call fails we skip validation.
            return

        fields: Iterable[Dict[str, Any]] = info.get("schema", {}).get("fields", [])
        for field in fields:
            if field.get("name") == "dense_vector":
                params = field.get("params", {})
                existing = params.get("dim") or params.get("max_length")
                if existing is not None and int(existing) != dense_dim:
                    raise RuntimeError(
                        "Existing Milvus collection 'dense_vector' dimension "
                        f"{existing} does not match expected {dense_dim}"
                    )
                break

        functions: Iterable[Dict[str, Any]] = info.get("schema", {}).get("functions", [])
        has_bm25 = any(func.get("name") == BM25_FUNCTION_NAME for func in functions)
        if not has_bm25:
            raise RuntimeError(
                "Existing Milvus collection is missing the BM25 function required for "
                "sparse indexing. Drop the collection or enable the function before "
                "continuing."
            )

    def upsert(self, rows: Iterable[Dict[str, Any]]) -> None:
        payload = []
        for row in rows:
            if not row:
                continue
            sanitized = dict(row)
            sanitized.pop("sparse_vector", None)
            payload.append(sanitized)
        if not payload:
            return
        self.ensure_collection(dense_dim=len(payload[0]["dense_vector"]))
        self._client.insert(collection_name=self._collection, data=payload)

    def load(self) -> None:
        """Explicitly load the Milvus collection for search readiness."""
        self._client.load_collection(collection_name=self._collection)

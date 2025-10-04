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
        # Name of the partition-key field in the schema when enabled.
        # We keep the field name stable and use the value from MILVUS_PARTITION_KEY.
        self._pk_field = "workspace_id"
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
        # Conditionally add partition-key field when configured via .env.
        # The value for this field will be supplied on every upsert.
        enable_partition_key = bool(self._settings.partition_key_value)
        if enable_partition_key:
            schema.add_field(
                field_name=self._pk_field,
                datatype=DataType.VARCHAR,
                max_length=128,
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

        create_kwargs: Dict[str, Any] = {
            "collection_name": self._collection,
            "schema": schema,
            "index_params": index_params,
            "consistency_level": self._settings.consistency_level,
        }
        if enable_partition_key:
            # Let Milvus manage partitions automatically using the partition-key field.
            # A moderate default for number of partitions; tune as needed.
            create_kwargs["partition_key_field"] = self._pk_field
            create_kwargs["num_partitions"] = 64

        self._client.create_collection(**create_kwargs)
        self._initialized = True

    def _validate_dimension(self, dense_dim: int) -> None:
        try:
            info = self._client.describe_collection(collection_name=self._collection)
        except Exception:
            # Best-effort validation only; if the call fails we skip validation.
            return

        fields: Iterable[Dict[str, Any]] = info.get("schema", {}).get("fields", [])
        # If partition key is configured in .env, ensure the field exists.
        if self._settings.partition_key_value:
            has_pk_field = any(f.get("name") == self._pk_field for f in fields)
            if not has_pk_field:
                raise RuntimeError(
                    "Existing Milvus collection is missing the partition-key field "
                    f"'{self._pk_field}'. Drop/recreate the collection with partition "
                    "key enabled or unset MILVUS_PARTITION_KEY."
                )
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
            # Stamp partition-key value if configured; ensures routing on insert.
            if self._settings.partition_key_value:
                sanitized[self._pk_field] = self._settings.partition_key_value
            payload.append(sanitized)
        if not payload:
            return
        self.ensure_collection(dense_dim=len(payload[0]["dense_vector"]))
        self._client.insert(collection_name=self._collection, data=payload)

    def load(self) -> None:
        """Explicitly load the Milvus collection for search readiness."""
        self._client.load_collection(collection_name=self._collection)

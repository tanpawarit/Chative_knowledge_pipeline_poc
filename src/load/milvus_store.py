"""High-level Milvus helpers for storing hybrid embeddings."""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

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
        self._pk_field = "workspace_id"
        self._initialized = False

    @property
    def client(self) -> MilvusClient:
        return self._client

    def ensure_collection(self, dense_dim: int) -> None:
        if self._initialized:
            return

        if self._client.has_collection(collection_name=self._collection):
            self._validate_collection(dense_dim)
            self._initialized = True
            return

        schema = self._build_schema(dense_dim)
        index_params = self._build_indexes()

        self._client.create_collection(
            collection_name=self._collection,
            schema=schema,
            index_params=index_params,
            partition_key_field=self._pk_field,
            num_partitions=64,
            consistency_level=self._settings.consistency_level,
        )
        self._initialized = True

    def document_exists(
        self,
        *,
        doc_name: str,
        doc_hash: str,
        workspace_id: Optional[str] = None,
    ) -> bool:
        """Return True when a document with matching identifiers is already stored."""

        workspace = (workspace_id or self._settings.partition_key_value or "").strip()
        if not workspace:
            return False
        if not doc_name or not doc_hash:
            return False

        try:
            if not self._client.has_collection(collection_name=self._collection):
                return False
        except Exception:
            return False

        filter_expr = self._and_filters(
            self._eq_expr(self._pk_field, workspace),
            self._eq_expr("doc_hash", doc_hash),
            self._eq_expr("doc_name", doc_name),
        )
        if not filter_expr:
            return False

        try:
            hits = self._client.query(
                collection_name=self._collection,
                filter=filter_expr,
                output_fields=["id"],
                limit=1,
                consistency_level=self._settings.consistency_level,
            )
        except Exception:
            return False

        return bool(hits)

    def _build_schema(self, dense_dim: int):
        schema = self._client.create_schema(auto_id=False, enable_dynamic_fields=False)
        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            max_length=36,
        )
        schema.add_field(
            field_name=self._pk_field,
            datatype=DataType.VARCHAR,
            max_length=64,
            is_partition_key=True,
        )
        schema.add_field(
            field_name="doc_hash",
            datatype=DataType.VARCHAR,
            max_length=64,
        )
        schema.add_field(
            field_name="doc_name",
            datatype=DataType.VARCHAR,
            max_length=512,
        )
        schema.add_field(
            field_name="chunk_index",
            datatype=DataType.INT32,
        )
        schema.add_field(
            field_name="total_chunks",
            datatype=DataType.INT32,
        )
        schema.add_field(
            field_name="text",
            datatype=DataType.VARCHAR,
            max_length=8192,
            enable_analyzer=True,
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
        schema.add_field(
            field_name="metadata",
            datatype=DataType.JSON,
        )
        schema.add_field(
            field_name="created_at",
            datatype=DataType.INT64,
        )
        schema.add_field(
            field_name="updated_at",
            datatype=DataType.INT64,
        )

        schema.add_function(
            build_bm25_function(
                input_field="text",
                output_field="sparse_vector",
                name=BM25_FUNCTION_NAME,
            )
        )
        return schema

    def _build_indexes(self):
        index_params = self._client.prepare_index_params()
        index_params.add_index(
            field_name="dense_vector",
            index_type="AUTOINDEX",
            metric_type=self._settings.dense_metric,
        )
        sparse_metric = self._settings.sparse_metric or "IP"
        index_params.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type=sparse_metric,
        )
        return index_params

    def _validate_collection(self, dense_dim: int) -> None:
        """Validate an existing collection without being brittle to SDK variants.

        Different pymilvus client versions return slightly different shapes for
        describe_collection(). This method normalizes those shapes so we don't
        incorrectly report that fields are missing when they are present.
        """
        try:
            info = self._client.describe_collection(collection_name=self._collection)
        except Exception:
            # If we can't describe, don't block collection usage.
            return

        # Normalize where fields are located and how their names are keyed.
        schema: Dict[str, Any] = info.get("schema", {}) or {}
        raw_fields: Iterable[Dict[str, Any]] = (
            schema.get("fields")
            or schema.get("field_schemas")
            or info.get("fields")
            or []
        )

        def field_name(f: Dict[str, Any]) -> Optional[str]:
            return f.get("name") or f.get("field_name") or f.get("fieldName")

        fields: List[Dict[str, Any]] = list(raw_fields)
        field_names = {n for n in (field_name(f) for f in fields) if n}
        required = {
            "id",
            self._pk_field,
            "doc_hash",
            "doc_name",
            "chunk_index",
            "total_chunks",
            "text",
            "dense_vector",
            "sparse_vector",
            "metadata",
            "created_at",
            "updated_at",
        }
        missing = sorted(required - field_names)
        if missing:
            raise RuntimeError(
                "Existing Milvus collection is missing required fields: "
                + ", ".join(missing)
            )

        def get_params(f: Dict[str, Any]) -> Dict[str, Any]:
            return f.get("params") or f.get("type_params") or {}

        dense_field = next((f for f in fields if field_name(f) == "dense_vector"), None)
        if dense_field:
            params = get_params(dense_field)
            # Some SDKs return dim under "dim", others under "dimension".
            existing = params.get("dim") or params.get("dimension") or params.get("max_length")
            if existing is not None and int(existing) != dense_dim:
                raise RuntimeError(
                    "Existing Milvus collection 'dense_vector' dimension "
                    f"{existing} does not match expected {dense_dim}"
                )

        # BM25 function inspection isn't available in all client variants; only
        # enforce when the data is present in the response.
        functions: Iterable[Dict[str, Any]] = schema.get("functions", [])
        if isinstance(functions, list) and functions:
            has_bm25 = any(func.get("name") == BM25_FUNCTION_NAME for func in functions)
            if not has_bm25:
                raise RuntimeError(
                    "Existing Milvus collection is missing the BM25 function required for "
                    "sparse indexing. Drop the collection or enable the function before continuing."
                )

        partition_field = next((f for f in fields if field_name(f) == self._pk_field), None)
        if partition_field is not None:
            is_pk = (
                partition_field.get("is_partition_key")
                or partition_field.get("isPartitionKey")
                or False
            )
            if not is_pk:
                raise RuntimeError(
                    "Existing Milvus collection does not have the workspace_id field configured "
                    "as a partition key. Drop the collection or recreate it with partition keys enabled."
                )

    def upsert(self, rows: Iterable[Dict[str, Any]]) -> None:
        prepared = self._prepare_rows(rows)
        if not prepared:
            return

        dense_dim = len(prepared[0]["dense_vector"])
        self.ensure_collection(dense_dim=dense_dim)

        workspace_id = prepared[0][self._pk_field]
        doc_hash = prepared[0]["doc_hash"]
        doc_name = prepared[0]["doc_name"]

        for row in prepared:
            if row[self._pk_field] != workspace_id:
                raise ValueError("All rows in a batch must share the same workspace_id")
            if row["doc_hash"] != doc_hash:
                raise ValueError("All rows in a batch must share the same doc_hash")
            if row["doc_name"] != doc_name:
                raise ValueError("All rows in a batch must share the same doc_name")

        hash_filter = self._and_filters(
            self._eq_expr(self._pk_field, workspace_id),
            self._eq_expr("doc_hash", doc_hash),
        )
        existing_same_hash = self._client.query(
            collection_name=self._collection,
            filter=hash_filter,
            output_fields=["doc_name"],
            consistency_level=self._settings.consistency_level,
        )

        if any(hit.get("doc_name") == doc_name for hit in existing_same_hash):
            # Case 2: identical content + name; nothing to do.
            return

        name_filter = self._and_filters(
            self._eq_expr(self._pk_field, workspace_id),
            self._eq_expr("doc_name", doc_name),
        )
        existing_same_name = self._client.query(
            collection_name=self._collection,
            filter=name_filter,
            output_fields=["doc_hash"],
            consistency_level=self._settings.consistency_level,
        )

        if existing_same_name and any(hit.get("doc_hash") != doc_hash for hit in existing_same_name):
            self._client.delete(
                collection_name=self._collection,
                filter=name_filter,
            )

        self._client.insert(collection_name=self._collection, data=prepared)

    def load(self) -> None:
        """Explicitly load the Milvus collection for search readiness."""
        self._client.load_collection(collection_name=self._collection)

    def _prepare_rows(self, rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prepared: List[Dict[str, Any]] = []
        now_ms = int(time.time() * 1000)

        for row in rows:
            if not row:
                continue
            base = dict(row)
            base.pop("sparse_vector", None)
            metadata = dict(base.pop("metadata", base.pop("meta", {})))
            metadata.setdefault("doc_hash", base.get("doc_hash"))
            metadata.setdefault("doc_name", base.get("doc_name"))

            workspace_id = (
                base.get(self._pk_field)
                or metadata.get(self._pk_field)
                or self._settings.partition_key_value
            )
            if not workspace_id:
                raise ValueError("workspace_id is required for Milvus upsert")

            doc_hash = base.get("doc_hash") or metadata.get("doc_hash")
            doc_name = base.get("doc_name") or metadata.get("doc_name")
            if not doc_hash or not doc_name:
                raise ValueError("Each row must include doc_hash and doc_name")

            chunk_index = base.get("chunk_index") or metadata.get("chunk_index")
            total_chunks = base.get("total_chunks") or metadata.get("chunk_total")
            if chunk_index is None:
                raise ValueError("Each row must include chunk_index")
            if total_chunks is None:
                raise ValueError("Each row must include total_chunks")

            dense_vector = list(base.get("dense_vector") or [])
            if not dense_vector:
                raise ValueError("Each row must include dense_vector")

            chunk_id = base.get("id")
            if not chunk_id:
                raise ValueError("Each row must include id")

            prepared.append(
                {
                    "id": str(chunk_id),
                    self._pk_field: str(workspace_id),
                    "doc_hash": str(doc_hash),
                    "doc_name": str(doc_name),
                    "chunk_index": int(chunk_index),
                    "total_chunks": int(total_chunks),
                    "text": base.get("text", ""),
                    "dense_vector": dense_vector,
                    "metadata": metadata,
                    "created_at": int(base.get("created_at") or now_ms),
                    "updated_at": int(base.get("updated_at") or now_ms),
                }
            )

        return prepared

    @staticmethod
    def _eq_expr(field: str, value: str) -> str:
        escaped = str(value).replace('"', '\\"')
        return f'{field} == "{escaped}"'

    @staticmethod
    def _and_filters(*filters: Optional[str]) -> str:
        clauses = [f for f in filters if f]
        return " && ".join(clauses)

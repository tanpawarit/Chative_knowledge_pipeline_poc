# Milvus Load-Layer Schema

This document describes the current Milvus collection schema and load/upsert behavior implemented by the code in this repo. It is intended to serve as a reference when redesigning the schema.

## Overview

- Storage model: hybrid embeddings (dense + sparse) with automatic sparse materialization via a Milvus BM25 function.
- Collection name: taken from `MILVUS_COLLECTION` in `.env`.
- Optional partition key: if `MILVUS_PARTITION_KEY` is set in `.env`, the collection is created with a partition-key field `workspace_id` and inserts will populate this field with the provided value.
- Creation and validation logic: `src/load/milvus_store.py:30` creates the collection if missing and validates critical properties if it already exists.

## Collection Schema

Defined in `src/load/milvus_store.py:39`.

- `id` — `VARCHAR(64)` primary key
  - `is_primary=True`, `max_length=64`.
- `text` — `VARCHAR(65535)`
  - `enable_analyzer=True` to support tokenization for BM25.
- `metadata` — `JSON`
- `dense_vector` — `FLOAT_VECTOR(dim=<dense_dim>)`
  - `<dense_dim>` equals the embedding dimension produced at runtime and is validated on reuse.
- `sparse_vector` — `SPARSE_FLOAT_VECTOR`
  - Not inserted by the app; it is produced by a BM25 function bound to `text`.

- When `MILVUS_PARTITION_KEY` is set
  - `workspace_id` — `VARCHAR(128)`
  - The collection is created with `partition_key_field="workspace_id"` and `num_partitions=64`.

Dynamic fields are disabled: `enable_dynamic_fields=False`.

## Functions (Automatic Sparse Materialization)

- Function builder: `src/load/sparse.py:12`
  - `BM25_FUNCTION_NAME = "text_bm25_emb"` (`src/load/sparse.py:9`).
  - Creates a `Function(function_type=FunctionType.BM25)` mapping `text -> sparse_vector`.
- Binding in schema: `src/load/milvus_store.py:69`
  - `schema.add_function(build_bm25_function(input_field="text", output_field="sparse_vector"))`.
- Validation on existing collections: `src/load/milvus_store.py:117`
  - Ensures a function with name `text_bm25_emb` exists; otherwise raises a runtime error to avoid silently missing sparse search capability.

Requirements: Milvus version with `SPARSE_FLOAT_VECTOR` and Functions API (e.g., Milvus 2.4+) and a compatible PyMilvus.

## Indexes and Metrics

Built during collection creation: `src/load/milvus_store.py:76`.

- Dense index
  - Field: `dense_vector`
  - `index_type = "AUTOINDEX"`, `index_name = "dense_autoindex"`
  - `metric_type = MILVUS_DENSE_METRIC` (defaults to `COSINE`) from `src/embedding/config.py:17`.

- Sparse index
  - Field: `sparse_vector`
  - `index_type = "AUTOINDEX"`, `index_name = "sparse_bm25_index"`
  - `metric_type = MILVUS_SPARSE_METRIC` (defaults to `BM25`) from `src/embedding/config.py:18`.

Consistency level for creation/loading operations is taken from `MILVUS_CONSISTENCY_LEVEL` (default `Bounded`) in `src/embedding/config.py:19` and used at collection creation.

## Upsert Contract

Implementation: `src/load/milvus_store.py:126`.

- Expected input row shape (from embedding stage): `{"id", "text", "metadata", "dense_vector"}`.
  - Produced by `src/embedding/dense.py` (`embed_chunks`), where `id` is provided or derived from `text`, and `dense_vector` is a `List[float]`.
- The loader removes any user-provided `sparse_vector` (if present): `sanitized.pop("sparse_vector", None)`.
- If `MILVUS_PARTITION_KEY` is set, the loader also adds `workspace_id = <MILVUS_PARTITION_KEY>` to each row before insert.
- The loader ensures the collection exists and has the correct dense dimension: `ensure_collection(dense_dim=len(payload[0]["dense_vector"]))`.
- Insert is executed via `MilvusClient.insert(collection_name, data=payload)`.

Dimension and Function Validation on existing collections: `src/load/milvus_store.py:98`

- Dense dimension must match the current model output; mismatch raises a clear error.
- The BM25 function must be defined; otherwise a runtime error instructs to drop or recreate the collection with BM25 enabled.
 

## Migration and Redesign Considerations

If you plan to evolve the schema, here are options grounded in current usage:

- Keys and identity
  - Keep `id` stable across re-embeddings; consider adding a `doc_id` (source document identifier) separate from `id` if you split documents into multiple chunks.
- Metadata normalization
  - Today metadata is a single `JSON` field. Consider promoting frequently-filtered attributes (e.g., `source`, `page`, `section`) to typed columns for better filtering and indexing.
- Partitioning
  - With the built-in partition-key path, use `MILVUS_PARTITION_KEY` per run/tenant to route data automatically. For existing collections without the `workspace_id` field, drop and recreate to enable partition-key.
- Auditing
  - Add timestamps (`created_at`, `updated_at`) and embedding model/version fields to manage re-embedding and backfills.
- Vector config
  - If changing embedding models, ensure `dense_vector.dim` is updated accordingly, and plan for side-by-side collections or reindexing.
- Analyzer configuration
  - Currently `text` uses default analyzer. If your data is multilingual or domain-specific, you may want to configure analyzers accordingly.

## Minimal Insert Example

Example payload (what the loader inserts). Note: do not include `sparse_vector` — it is computed by the BM25 function.

```json
{
  "id": "chunk_001",
  "text": "Your chunk text …",
  "metadata": { "source": "file.pdf", "page": 3 },
  "dense_vector": [0.01, -0.02, 0.03, "…"]
}
```
 
schema = client.create_schema(auto_id=False, enable_dynamic_fields=False)
schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=64)
schema.add_field(field_name="workspace_id", datatype=DataType.VARCHAR, max_length=128)  # ใช้เป็น Partition Key
schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535, enable_analyzer=True)
schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=dim)
schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)

schema.add_function(build_bm25_function(input_field="text", output_field="sparse_vector"))

index_params = client.prepare_index_params()
index_params.add_index(field_name="dense_vector", index_type="AUTOINDEX", metric_type="IP")
index_params.add_index(field_name="sparse_vector", index_type="AUTOINDEX", metric_type="IP")

client.create_collection(
    collection_name="docs",
    schema=schema,
    index_params=index_params,
    # จุดสำคัญ: เปิด partition key
    partition_key_field="workspace_id",
    num_partitions=64,  # ให้ Milvus สร้าง/จัดการพาร์ทิชันอัตโนมัติ
)

workspace_id (partition key)

doc_id (UUID คงที่ตลอดอายุ “เอกสารตรรกะ” เดิม)

doc_version (INT)

doc_hash (SHA-256 ของเนื้อหาหลัง normalize)

doc_name (VARCHAR — สเกลาร์) ← ตอบโจทย์คุณที่สุด

r2_key (path/key บน R2), r2_etag (เผื่อ debug/เทียบเร็ว), อาจเสริม size_bytes, last_modified

เนื้อหา: text, dense_vector, sparse_vector, metadata (JSON สำหรับของจุกจิก)

<!-- =============== -->
index_params = client.prepare_index_params()
index_params.add_index(field_name="dense_vector", index_type="AUTOINDEX", metric_type="IP")
index_params.add_index(field_name="sparse_vector", index_type="AUTOINDEX", metric_type="IP")

client.create_collection(
    collection_name="knowledge_base", # .env MILVUS_COLLECTION=knowledge_base
    schema=schema,
    index_params=index_params, 
    partition_key_field="workspace_1", # .env MILVUS_PARTITION_KEY=workspace_1
    num_partitions=64,  # ให้ Milvus สร้าง/จัดการพาร์ทิชันอัตโนมัติ
)
schema = client.create_schema(auto_id=False, enable_dynamic_fields=False)
schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=64) # id="{workspace_id}::{doc_id}::{chunk_id}
schema.add_field(field_name="doc_id", datatype=DataType.VARCHAR, max_length=64) # 
# ส่วนเนื้อหา
schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535, enable_analyzer=True)
schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=dim)
schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)

# meta data
{"h1":"","h2":"Example Priming for ISTP Profile (without explicitely naming the profile)","h3":"","source":"data/2509.04343v1.pdf","header_index":117,"section_parent_type":"markdown_header","parent_type":"semantic_chunk","semantic_chunk_index":0,"semantic_chunk_total":1}

<!-- ========= -->
requirment multitenent เเบ่งตาม workspace เเต่ละ workspace อัพโหลดเอกสารเข้า r2 
ที่คิดเบื้องต้นคือ 
    -ใช้ r2 hash key ไว้ระบุตัวตนเอกสารสำหรับ upsert
    -ใช้ workspace_id เป็น partition_key (น่าจะสเกลได้ ถ้ามี workspace 2000+)
    -ถ้าลูกค้าอัพโหลด เอกสารเนื้อหาใหม่ เเต่ชื่อเดิม (do upsert)
    -ถ้าลูกค้าอัพโหลด เอกสารเนื้อหาใหม่ เเต่ชื่อใหม่ (do insert)
    -ถ้าลูกค้าอัพโหลด เอกสารเนื้อหาเดิม เเต่ชื่อใหม่ (do insert)
    -ถ้าลูกค้าอัพโหลด เอกสารเนื้อหาเดิม เเต่ชื่อเดิม (do nothing)
ไม่ต้องการ versioning 
ใช้ ETag จาก r2

# ============================================
# MILVUS SCHEMA FOR MULTI-TENANT RAG SYSTEM
# ============================================
# Requirements:
# - Multi-workspace isolation via partition_key
# - Deduplication via content hash (SHA256)
# - Hybrid search (dense + sparse vectors)
# - Upsert logic based on (workspace, hash, name)
# ============================================
 
# ────────────────────────────────────────────
# Schema Definition
# ────────────────────────────────────────────
schema = client.create_schema(
    auto_id=False,              # เราจะ generate id เอง
    enable_dynamic_fields=False # ป้องกัน field ไม่ได้กำหนด
)

# ────────────────────────────────────────────
# 1. Primary Key
# ────────────────────────────────────────────
# ใช้ UUID แทน composite string เพื่อ:
# - ลดขนาด index
# - เพิ่มความเร็ว query
# - ง่ายต่อการ debug
schema.add_field(
    "id",
    DataType.VARCHAR,
    is_primary=True,
    max_length=36  # UUID format: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
)

# ────────────────────────────────────────────
# 2. Partition Key (Multi-tenant Isolation)
# ────────────────────────────────────────────
# Milvus จะแบ่ง data ตาม workspace_id อัตโนมัติ
# Benefits:
# - Query เฉพาะ workspace เร็วขึ้น (ไม่ scan ทุก partition)
# - Scale ได้ถึง 10K+ workspaces
schema.add_field(
    "workspace_id",
    DataType.VARCHAR,
    max_length=64  # เพียงพอสำหรับ UUID หรือ custom ID
)

# ────────────────────────────────────────────
# 3. Document Identity (Deduplication)
# ────────────────────────────────────────────
# doc_hash: SHA256 ของไฟล์ต้นฉบับ 
# - ใช้ตรวจสอบว่าเนื้อหาซ้ำหรือไม่ 
schema.add_field(
    "doc_hash",
    DataType.VARCHAR,
    max_length=64  # SHA256 = 64 hex characters
)

# doc_name: ชื่อไฟล์ที่ user อัพโหลด
# - อนุญาตให้ซ้ำได้ (เพราะอาจมีหลาย workspace ใช้ชื่อเดียวกัน)
# - ใช้ร่วมกับ doc_hash ในการตัดสินใจ upsert/insert
schema.add_field(
    "doc_name",
    DataType.VARCHAR,
    max_length=512  # รองรับชื่อไฟล์ยาว + unicode
)

# ────────────────────────────────────────────
# 4. Chunk Information
# ────────────────────────────────────────────
# chunk_index: ลำดับของ chunk นี้ในเอกสาร (0-indexed)
# - ใช้เรียงลำดับเมื่อแสดงผล
# - ช่วยในการ reconstruct เอกสารเดิม
schema.add_field(
    "chunk_index",
    DataType.INT32
)

# total_chunks: จำนวน chunk ทั้งหมดของเอกสารนี้
# - ใช้ตรวจสอบว่า insert ครบหรือยัง
# - แสดง progress ให้ user
schema.add_field(
    "total_chunks",
    DataType.INT32
)

# ────────────────────────────────────────────
# 5. Content
# ────────────────────────────────────────────
# text: เนื้อหาของ chunk นี้
# - ขนาดแนะนำ: 512-1024 tokens (2K-4K chars)
# - enable_analyzer=True: รองรับ full-text search
schema.add_field(
    "text",
    DataType.VARCHAR,
    max_length=8192,  # ~2K tokens (เหมาะกับ LLM context)
    enable_analyzer=True
)

# ────────────────────────────────────────────
# 6. Vector Embeddings (Hybrid Search)
# ────────────────────────────────────────────
# dense_vector: Semantic embedding
# - จาก model เช่น OpenAI, Cohere, BGE
# - ใช้สำหรับ semantic similarity search
schema.add_field(
    "dense_vector",
    DataType.FLOAT_VECTOR,
    dim=1024  # ปรับตาม embedding model ที่ใช้
              # OpenAI text-embedding-3-large: 3072
              # Cohere embed-multilingual-v3: 1024
              # BGE-M3: 1024
)

# sparse_vector: Lexical features (BM25)
# - Generate อัตโนมัติจาก text field
# - ใช้สำหรับ keyword-based search
schema.add_field(
    "sparse_vector",
    DataType.SPARSE_FLOAT_VECTOR
)

# ────────────────────────────────────────────
# 7. Metadata (Flexible JSON)
# ────────────────────────────────────────────
# เก็บข้อมูลเพิ่มเติมที่อาจต้องใช้:
# {
#   "file_type": "application/pdf",
#   "file_size": 2048000,
#   "r2_key": "ws_abc/sha256_def/report.pdf",
#   "page_number": 5,
#   "language": "th",
#   "tags": ["financial", "q4-2024"]
# }
schema.add_field(
    "metadata",
    DataType.JSON
)

# ────────────────────────────────────────────
# 8. Timestamps
# ────────────────────────────────────────────
# created_at: เวลาที่ chunk นี้ถูกสร้าง (epoch milliseconds)
schema.add_field(
    "created_at",
    DataType.INT64
)

# updated_at: เวลาที่ chunk นี้ถูกอัพเดตล่าสุด
# - ใช้สำหรับ audit trail
# - filter เอาเฉพาะข้อมูลล่าสุด
schema.add_field(
    "updated_at",
    DataType.INT64
)

# ────────────────────────────────────────────
# 9. BM25 Function (Auto-generate sparse_vector)
# ────────────────────────────────────────────
# Milvus จะ generate sparse_vector จาก text อัตโนมัติ
def build_bm25_function(input_field: str, output_field: str):
    return Function(
        name="bm25_fn",
        function_type=FunctionType.BM25,
        input_field_names=[input_field],
        output_field_names=[output_field]
    )

schema.add_function(
    build_bm25_function(
        input_field="text",
        output_field="sparse_vector"
    )
)

# ────────────────────────────────────────────
# Index Configuration
# ────────────────────────────────────────────
index_params = client.prepare_index_params()

# Dense vector index
# - AUTOINDEX: Milvus เลือก algorithm ให้เอง (HNSW/IVF)
# - IP (Inner Product): ใช้กับ normalized vectors
#   ถ้า vectors ไม่ normalized ให้ใช้ COSINE หรือ L2
index_params.add_index(
    field_name="dense_vector",
    index_type="AUTOINDEX",
    metric_type="COSINE"   
)

# Sparse vector index
# - SPARSE_INVERTED_INDEX: เหมาะกับ BM25
# - IP: เพราะ BM25 scores เป็น positive
index_params.add_index(
    field_name="sparse_vector",
    index_type="SPARSE_INVERTED_INDEX",
    metric_type="IP"
)

# ────────────────────────────────────────────
# Collection Creation
# ────────────────────────────────────────────
client.create_collection(
    collection_name="knowledge_base",
    schema=schema,
    index_params=index_params,
    
    # Partition Strategy
    partition_key_field="workspace_id",
    
    # Number of partitions:
    # - เริ่มที่ 64 สำหรับ < 1K workspaces
    # - Scale ไป 128 เมื่อมี 1K-5K workspaces
    # - Scale ไป 256 เมื่อมี 5K+ workspaces
    # Rule of thumb: num_partitions ≈ sqrt(num_workspaces)
    num_partitions=64
)

┌─────────────────────────────────────────────────────────────┐
│                    UPLOAD DECISION TREE                      │
└─────────────────────────────────────────────────────────────┘

1. Compute doc_hash = SHA256(file_content)

2. Query Milvus:
   filter = (workspace_id == X) && (doc_hash == Y)
   
3. Check results:

   ┌─────────────────────────────────────────────────┐
   │  Case 1: No results                             │
   │  → เอกสารใหม่ทั้งเนื้อหาและชื่อ                  │
   │  → Action: INSERT                               │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │  Case 2: Found + same doc_name                  │
   │  → เนื้อหาเดิม + ชื่อเดิม                        │
   │  → Action: SKIP (do nothing)                    │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │  Case 3: Found + different doc_name             │
   │  → เนื้อหาเดิม + ชื่อใหม่                        │
   │  → Action: INSERT (เก็บทั้ง 2 ชื่อ)              │
   └─────────────────────────────────────────────────┘

4. Query Milvus again:
   filter = (workspace_id == X) && (doc_name == Z)
   
5. If found:
   
   ┌─────────────────────────────────────────────────┐
   │  Case 4: Different doc_hash                     │
   │  → เนื้อหาใหม่ + ชื่อเดิม                        │
   │  → Action: UPSERT                               │
   │    1. Delete old chunks (same doc_name)         │
   │    2. Insert new chunks                         │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │  Case 5: Same doc_hash (already handled)        │
   │  → Covered by Case 2 above                      │
   └─────────────────────────────────────────────────┘
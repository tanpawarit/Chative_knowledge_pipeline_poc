# Milvus Load Layer  

This document explains the load-layer schema and upsert rules for a multi-tenant RAG system using Milvus. It focuses on clarity and simple English.

Key ideas
- Partition by `workspace_id` to isolate tenants and scale.
- Identify document content by a SHA-256 `doc_hash` for deduplication.
- Support hybrid search with both dense and sparse vectors.
- Use straightforward upsert rules based on content and name.

Upsert rules
- New content, same name: upsert (replace existing document version).
- New content, new name: insert (add a new document).
- Same content, new name: insert (treat as a different document).
- Same content, same name: no-op (do nothing).

Schema overview
- Primary key: `id` (UUID string).
- Partition key: `workspace_id` (string).
- Content identity: `doc_hash` (SHA-256 hex string).
- Document name: `doc_name` (string, can repeat across workspaces).
- Chunk info: `chunk_index` (int), `total_chunks` (int).
- Content: `text` (string, sized for LLM context; analyzer enabled for full-text).
- Embeddings: `dense_vector` (float vector, e.g., 1024 or per your model), `sparse_vector` (BM25-generated).
- Metadata: `metadata` (JSON for extra attributes like file type, size, language, tags).
- Timestamps: `created_at` (int64 epoch ms), `updated_at` (int64 epoch ms).

Indexing
- Dense: AUTOINDEX with `COSINE` (or match the metric to your embedding normalization).
- Sparse: BM25 over `text`, generating `sparse_vector` for keyword search.

Why this design
- Multi-tenant isolation: queries filter by `workspace_id`, improving performance and scale.
- Deduplication: `doc_hash` prevents duplicate content from accidental re-uploads.
- Hybrid search: combine semantic similarity (dense) and lexical relevance (sparse) so downstream retrieval stays strong.

Notes
- Choose `dense_vector` dimension to match your embedding model (e.g., 1024 for many multilingual models; 3072 for OpenAI text-embedding-3-large).
- Keep `text` chunks sized for your downstream context window (commonly 2K–4K characters per chunk).
- If you need examples or code, see `src/knowledge_store/infrastructure/milvus_store.py` for the implementation details.
# - IP: BM25 scores are positive
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
    # - Start with 64 for < 1K workspaces
    # - Scale to 128 for 1K–5K workspaces
    # - Scale to 256 for 5K+ workspaces
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
   │  → New content and new name                     │
   │  → Action: INSERT                               │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │  Case 2: Found + same doc_name                  │
   │  → Same content + same name                     │
   │  → Action: SKIP (do nothing)                    │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │  Case 3: Found + different doc_name             │
   │  → Same content + new name                      │
   │  → Action: INSERT (keep both names)             │
   └─────────────────────────────────────────────────┘

4. Query Milvus again:
   filter = (workspace_id == X) && (doc_name == Z)
   
5. If found:
   
   ┌─────────────────────────────────────────────────┐
   │  Case 4: Different doc_hash                     │
   │  → New content + same name                      │
   │  → Action: UPSERT                               │
   │    1. Delete old chunks (same doc_name)         │
   │    2. Insert new chunks                         │
   └─────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────┐
   │  Case 5: Same doc_hash (already handled)        │
   │  → Covered by Case 2 above                      │
   └─────────────────────────────────────────────────┘

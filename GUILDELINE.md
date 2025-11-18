# Knowledge Pipeline Development Guideline

## Project Overview

This repository is a proof-of-concept knowledge ingestion pipeline. It extracts content from documents, creates retrieval-friendly chunks, generates dense embeddings, and optionally upserts them into Milvus with hybrid search support.

High-level flow:
- Document Extraction: Docling-based conversion enriched with OCR and picture descriptions.
- Chunking: Markdown-aware pre-splitting followed by semantic splitting/merging.
- Embedding: OpenAI embeddings applied to chunks via a shared runtime factory.
- Storage: Upsert into Milvus with dense + BM25-sparse indexing.

## Project Structure

```
├── main.py                      # FastAPI entry point (imported by uvicorn)
├── src/
│   ├── app/                        # Composition + API (current FastAPI app)
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routers/
│   │   │       └── qstash.py
│   │   ├── domain/
│   │   │   └── events.py
│   │   ├── services/
│   │   │   └── pipeline_service.py
│   │   ├── settings.py 
│   │
│   ├── document_extraction/        # Extracts Markdown from input docs
│   │   ├── application/extraction_service.py
│   │   ├── domain/ocr_policy.py
│   │   └── infrastructure/
│   │       ├── adapter/{ocr,picture_description}.py
│   │       ├── config.py
│   │       ├── docling_extractor.py
│   │       ├── picture_serializer.py
│   │       └── pipeline_option.py
│   │
│   ├── document_chunking/          # Markdown-aware + semantic chunking
│   │   ├── application/chunking_service.py
│   │   ├── domain/{models,services}.py
│   │   └── infrastructure/{markdown_splitter,semantic_chunker}.py
│   │
│   ├── document_embedding/         # Embedding orchestration
│   │   ├── application/embed_pipeline.py
│   │   ├── domain/{models,services}.py
│   │   └── infrastructure/openai_client.py
│   │
│   ├── document_store/             # Milvus/BM25 persistence
│   │   ├── application/upsert_service.py
│   │   └── infrastructure/{bm25_function,milvus_store}.py
│   │
│   └── shared/                     # Cross-cutting helpers
│       ├── config.py               # Env-driven settings
│       ├── logging/logger.py
│       ├── embeddings/{factory,providers}.py
│       └── cost_management/{openai_cost_tracker,mistral_cost_tracker}.py
│
├── asset/                          # Architecture diagrams / flow images
├── testfiles/                      # Sample documents (gitignored)
├── README.md                       # Component-level context and diagrams
├── GUILDELINE.md                   # This guide
├── pyproject.toml                  # Project, deps, and build backend (uv)
└── uv.lock                         # Resolved dependency lockfile (uv)
```

## Architecture Principles

### 1. Domain-Driven Design (DDD) by Folders
- Domain Layer (`src/*/domain`): Pure business rules and models. No I/O or API calls.
- Application Layer (`src/*/application`): Use cases/orchestration; composes domain services and infra.
- Infrastructure Layer (`src/*/infrastructure`): Frameworks, external services, adapters, and I/O.

### 2. Dependency Direction
- Application depends on Domain; Infrastructure depends on Domain.
- Domain is independent and must not import application/infra.
- Keep boundaries explicit: pass data structures across  

### 3. Logging
- Use `src/shared/logging/logger.py::configure_logging()` to initialize logging at entry points.
- Libraries no longer print to stdout; they emit via `logging`.

## Development Workflow

### 1. Setup
- With `uv` (recommended):
  - `uv sync` to install dependencies from `pyproject.toml`/`uv.lock`.
- With `pip`:
  - Create venv (`python -m venv .venv && source .venv/bin/activate`).
  - `pip install -r <generated requirements>` or install from `pyproject.toml` manually.

### 2. Configure Environment
- Copy `.env` and fill required keys (see Configuration section).
- Minimal run requires the OpenAI embedding API key/model plus Milvus settings when upserting.

Embedding configuration:
- `OPENAI_API_KEY`, `OPENAI_EMBED_MODEL` (e.g., `text-embedding-3-small`), optional `OPENAI_EMBED_USD_PER_MILLION`

Milvus configuration:
- `MILVUS_ADDR`, `MILVUS_USERNAME`, `MILVUS_PASSWORD`, `MILVUS_COLLECTION`
- Optional fallback partition: `MILVUS_PARTITION_KEY` (only needed when events do not include `workspace_id`, e.g., manual CLI runs)
- `MILVUS_DENSE_METRIC` (default `COSINE`), `MILVUS_SPARSE_METRIC` should be `IP` when using SPARSE_INVERTED_INDEX
- BM25 sparse function is added programmatically; you do not set `BM25` as a metric

### 3. Run the Pipeline
- Start the FastAPI receiver: `uv run uvicorn main:app --host 0.0.0.0 --port 8080`.
  - Alternatively: `uv run python main.py`.
- Publish QStash events pointing to `/consume/documents/embed` with the required payload fields (`documentId`, `workspaceId`, `filePath`, `filename`, `checksum`).

# Knowledge Pipeline Development Guideline

## Project Overview

This repository is a proof-of-concept knowledge ingestion pipeline. It extracts content from documents, creates retrieval-friendly chunks, generates dense embeddings, and optionally upserts them into Milvus with hybrid search support.

High-level flow:
- Document Extraction: Docling-based conversion enriched with OCR and picture descriptions.
- Chunking: Markdown-aware pre-splitting followed by semantic splitting/merging.
- Embedding: Gemini embeddings applied to chunks.
- Storage: Upsert into Milvus with dense + BM25-sparse indexing.

## Project Structure

```
├── main.py                         # Pipeline entry function
├── src/
│   ├── document_extraction/        # Extracts Markdown from input docs
│   │   ├── application/
│   │   │   └── extraction_service.py
│   │   ├── domain/
│   │   │   └── ocr_policy.py
│   │   └── infrastructure/
│   │       ├── adapter/
│   │       │   ├── ocr.py                   # Mistral OCR adapter
│   │       │   └── picture_description.py   # Mistral picture description adapter
│   │       ├── config.py
│   │       ├── docling_extractor.py
│   │       ├── picture_serializer.py
│   │       └── pipeline_option.py
│   │
│   ├── document_chunking/          # Turns Markdown into retrieval-ready chunks
│   │   ├── application/
│   │   │   └── chunking_service.py
│   │   ├── domain/
│   │   │   ├── models.py
│   │   │   └── services.py
│   │   └── infrastructure/
│   │       ├── markdown_splitter.py
│   │       └── semantic_chunker.py
│   │
│   ├── knowledge_embedding/        # Embeds chunks with Gemini
│   │   ├── application/
│   │   │   └── embed_pipeline.py
│   │   ├── domain/
│   │   │   ├── models.py
│   │   │   └── services.py
│   │   └── infrastructure/
│   │       └── gemini_client.py
│   │
│   ├── knowledge_store/            # Storage and upsert logic (Milvus + BM25)
│   │   ├── application/
│   │   │   └── upsert_service.py
│   │   └── infrastructure/
│   │       ├── bm25_function.py
│   │       └── milvus_store.py
│   │
│   ├── cost_management/
│   │   └── infrastructure/
│   │       ├── gemini_cost_tracker.py
│   │       └── mistral_cost_tracker.py
│   │
│   └── shared/                     # Cross-cutting helpers
│       ├── config.py               # Env-driven settings
│       └── logging/
│           └── logger.py
│
├── script/                         # Helper scripts and experiments
├── tests/                          # Pytest-based tests
├── asset/                          # Architecture diagrams / flow images
├── data/                           # Sample input documents
├── README.md                       # Component-level context and diagrams
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
- Keep boundaries explicit: pass data structures across layers, not framework-specific objects.

## Development Workflow

### 1. Setup
- With `uv` (recommended):
  - `uv sync` to install dependencies from `pyproject.toml`/`uv.lock`.
- With `pip`:
  - Create venv (`python -m venv .venv && source .venv/bin/activate`).
  - `pip install -r <generated requirements>` or install from `pyproject.toml` manually.

### 2. Configure Environment
- Copy `.env` and fill required keys (see Configuration section).
- Minimal run requires at least `GEMINI_API_KEY` to embed; Milvus settings are only needed for upsert.

### 3. Run the Pipeline
- Quick start: `python main.py` (uses default sample under `data/`).
- To choose a file: edit `main(source=...)` or run `python -c "import main; main.main('data/your.pdf')"`.


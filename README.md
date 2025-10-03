# Extraction Module

This module wraps Docling with two custom adapters to improve text and image understanding during document conversion:

- Mistral OCR: recovers text from scanned PDFs or images
- Mistral Picture Description: generates short, useful descriptions for figures and pictures

The pipeline decides when to run OCR, enriches pictures with descriptions, and serializes to Markdown with the descriptions preserved as HTML comments next to each image.

![Extraction Flow](asset/extraction_flow.png)
 
# Chunking Module

This module converts Markdown into retrieval-ready chunks using a two-stage strategy:

- Markdown-aware pre-split: preserves `H1/H2/H3`, with adaptive sub-splitting for long sections.
- Semantic split: Gemini-powered `SemanticChunker` finds natural boundaries; tiny pieces are merged to meet a minimum size.

Outputs stable `id`, `text`, and rich `meta` (headers, source, indices) for each chunk.

![Chunking Flow](asset/chunking_flow.png)

# Embedding Module
 
 
 

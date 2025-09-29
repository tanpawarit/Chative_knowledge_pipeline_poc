# Extraction Module

This module wraps Docling with two custom adapters to improve text and image understanding during document conversion:

- Mistral OCR: recovers text from scanned PDFs or images
- Mistral Picture Description: generates short, useful descriptions for figures and pictures

The pipeline decides when to run OCR, enriches pictures with descriptions, and serializes to Markdown with the descriptions preserved as HTML comments next to each image.

![Extraction Flow](asset/extraction_flow.png)

# Chunking Module

# Embedding Module

## Cite

- Extraction: Deep Search Team (2024). Docling Technical Report. arXiv:2408.09869. https://doi.org/10.48550/arXiv.2408.09869
- Embedding baseline: Arora, Liang, Ma (2017). A Simple but Tough-to-Beat Baseline for Sentence Embeddings. https://openreview.net/pdf?id=SyK00v5xx

```
@techreport{Docling,
  author = {Deep Search Team},
  month = {8},
  title = {Docling Technical Report},
  url = {https://arxiv.org/abs/2408.09869},
  eprint = {2408.09869},
  doi = {10.48550/arXiv.2408.09869},
  version = {1.0.0},
  year = {2024}
}

@inproceedings{arora2017simple,
  title = {A Simple but Tough-to-Beat Baseline for Sentence Embeddings},
  author = {Sanjeev Arora and Yingyu Liang and Tengyu Ma},
  booktitle = {Proceedings of the International Conference on Learning Representations},
  year = {2017},
  url = {https://openreview.net/pdf?id=SyK00v5xx}
}
```

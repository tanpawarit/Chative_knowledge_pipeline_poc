from typing import Any, Dict, List, Optional

import numpy as np
from langchain_text_splitters import TokenTextSplitter

from src.chunking.cache import DiskVectorCache
from src.chunking.config import Settings
from src.chunking.embed_gemini import GeminiEmbedder
from src.chunking.splitter import split_by_markdown
from src.chunking.utils import make_chunk_id, sentence_split, token_len, weighted_mean

def token_part_vectorization(settings: Settings, long_text: str,
                             embedder: GeminiEmbedder, cache: DiskVectorCache) -> List[Dict[str, Any]]:
    '''
    Not semantic chunking, but semantic pooling for vectors.

    - Chunking: done by TokenTextSplitter (token-limited parts). This decides boundaries.
    - Semantics: per-part sentence splitting solely to build vectors via
      sentence-level embeddings + token-weighted mean pooling.
    '''
    # Stage 1: enforce token-limited parts; semantic pooling happens per part below
    splitter = TokenTextSplitter(
        chunk_size=settings.max_tokens_per_subchunk,
        chunk_overlap=settings.overlap_tokens,
        encoding_name=settings.token_encoding_name,
    )
    parts = splitter.split_text(long_text)
    if not parts:
        # Fallback: nothing to split → keep original text as a single part
        parts = [long_text]

    subs: List[Dict[str, Any]] = []

    for part in parts:
        # Stage 2: sentence-level split used only for pooling, not for boundaries
        sents = sentence_split(part)
        if not sents:
            subs.append({"text": part.strip(), "vector": None})
            continue

        vecs: List[Optional[np.ndarray]] = [None] * len(sents)
        need: List[str] = []
        idx_map: List[int] = []

        # Resolve sentence vectors from cache; collect the ones we still need to embed
        for i, sent in enumerate(sents):
            cached = cache.get(sent)
            if cached is None:
                need.append(sent)
                idx_map.append(i)
            else:
                vecs[i] = cached

        if need:
            new_vecs = embedder.embed_batch(need)
            for pos, vec in zip(idx_map, new_vecs):
                vecs[pos] = vec
                cache.set(sents[pos], vec)

        # Weight by token counts to align pooling with model token budget
        weights = [token_len(s, settings.token_encoding_name) for s in sents]
        resolved = [(v, w) for v, w in zip(vecs, weights) if v is not None]
        if resolved:
            res_vecs, res_weights = zip(*resolved)
            mean_vec = weighted_mean(list(res_vecs), list(res_weights))
        else:
            mean_vec = np.array([], dtype=np.float32)
        subs.append({
            "text": part.strip(),
            "vector": mean_vec if mean_vec.size else None,
        })

    return subs


def run_pipeline(md_text: str, source: str, settings: Settings) -> List[Dict[str, Any]]:
    # 1) Split by Markdown headers to preserve document structure
    base_chunks = split_by_markdown(md_text)
    cache = DiskVectorCache(settings.cache_dir)
    embedder = GeminiEmbedder(settings)

    results: List[Dict[str, Any]] = []
    ready_texts: List[str] = []
    idx_map: List[int] = []

    for ch in base_chunks:
        n_tokens = token_len(ch["text"], settings.token_encoding_name)
        # Long chunks → token-limited parts + sentence-level semantic pooling for vectors
        if n_tokens > settings.max_tokens_per_subchunk:
            subs = token_part_vectorization(settings, ch["text"], embedder, cache) 
            for s in subs:
                results.append({
                    "id": make_chunk_id(s["text"]),
                    "text": s["text"],
                    "vector": s["vector"].tolist() if s["vector"] is not None else None,
                    "meta": ch["meta"] | {"parent_type": "token_part", "source": source},
                }) 
        else:
            # Short chunks → defer and batch-process sentence embeddings below
            ready_texts.append(ch["text"])
            idx_map.append(len(results))
            results.append({
                "id": make_chunk_id(ch["text"]),
                "text": ch["text"],
                "vector": None,
                "meta": ch["meta"] | {"parent_type": "header_chunk", "source": source},
            })

    # For the short chunks: embed sentences once, then weighted-mean per chunk
    if ready_texts:
        # Sentence-level cache+embed (batch)
        sent_lists = [sentence_split(t) for t in ready_texts]
        flat: List[str] = []
        owners: List[int] = []  # map flat index → which chunk (kept for clarity)
        for ci, sents in enumerate(sent_lists):
            for s in sents:
                flat.append(s)
                owners.append(ci)

        cache = DiskVectorCache(settings.cache_dir)
        embedder = GeminiEmbedder(settings)

        # Resolve cache first; only embed sentences not seen before
        vecs: List[np.ndarray] = [None] * len(flat)
        need: List[str] = []
        posmap: List[int] = []
        for i, s in enumerate(flat):
            v = cache.get(s)
            if v is None:
                need.append(s)
                posmap.append(i)
            else:
                vecs[i] = v
        if need:
            new_vecs = embedder.embed_batch(need)
            for k, v in enumerate(new_vecs):
                i = posmap[k]
                vecs[i] = v
                cache.set(flat[i], v)

        # Aggregate back per chunk via token-weighted mean of sentence vectors
        start = 0
        for chunk_idx, sents in enumerate(sent_lists):
            end = start + len(sents)
            s_vecs = vecs[start:end]
            weights = [token_len(s, settings.token_encoding_name) for s in sents]
            mean_vec = weighted_mean(s_vecs, weights) if s_vecs else np.array([], dtype=np.float32)
            results_idx = idx_map[chunk_idx]
            results[results_idx]["vector"] = mean_vec.tolist() if mean_vec.size else None
            start = end

    return results

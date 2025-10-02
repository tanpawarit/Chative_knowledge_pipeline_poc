from typing import Any, Dict, List, Optional

import numpy as np
from langchain_text_splitters import TokenTextSplitter

from src.chunking.cache import DiskVectorCache
from src.chunking.config import Settings
from src.chunking.embed_gemini import GeminiEmbedder
from src.chunking.splitter import split_by_markdown
from src.chunking.utils import cosine, make_chunk_id, sentence_split, token_len, weighted_mean


def semantic_chunking_by_sentences(settings: Settings, text: str,
                                   embedder: GeminiEmbedder, cache: DiskVectorCache) -> List[Dict[str, Any]]:
    '''
    True sentence-level semantic chunking.

    - Splits the text into sentences once, caches/embeds them, and then greedily
      groups sentences into token-constrained chunks.
    - A chunk boundary is emitted when adding the next sentence would either
      exceed the token budget or degrade cohesion beyond the configured drop.
    - Chunk vectors are produced via token-weighted mean pooling of the member
      sentence embeddings so we still embed each sentence only one time.
    '''

    sentences = sentence_split(text)
    if not sentences:
        return [{"text": text.strip(), "vector": None}]

    token_counts = [max(1, token_len(s, settings.token_encoding_name)) for s in sentences]

    # Resolve/calc sentence embeddings with caching (mirrors prior behaviour)
    vecs: List[Optional[np.ndarray]] = [None] * len(sentences)
    need: List[str] = []
    idx_map: List[int] = []
    for i, sent in enumerate(sentences):
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
            cache.set(sentences[pos], vec)

    max_tokens = settings.max_tokens_per_subchunk
    min_tokens = max(1, settings.semantic_min_tokens)
    cohesion_drop = max(0.0, settings.semantic_cohesion_drop)
    overlap = max(0, settings.semantic_sentence_overlap)

    class ChunkBuilder:
        __slots__ = ("sentences", "vecs", "tokens", "total_tokens", "sum_vec", "sum_weight")

        def __init__(self) -> None:
            self.sentences: List[str] = []
            self.vecs: List[Optional[np.ndarray]] = []
            self.tokens: List[int] = []
            self.total_tokens: int = 0
            self.sum_vec: Optional[np.ndarray] = None
            self.sum_weight: float = 0.0

        def append(self, sent: str, vec: Optional[np.ndarray], tok: int) -> None:
            self.sentences.append(sent)
            self.vecs.append(vec)
            self.tokens.append(tok)
            self.total_tokens += tok
            if vec is not None:
                if self.sum_vec is None:
                    self.sum_vec = vec * tok
                else:
                    self.sum_vec = self.sum_vec + (vec * tok)
                self.sum_weight += tok

        def mean_vec(self) -> Optional[np.ndarray]:
            if self.sum_vec is None or self.sum_weight == 0:
                return None
            return self.sum_vec / self.sum_weight

        def build(self) -> Optional[Dict[str, Any]]:
            if not self.sentences:
                return None
            joined = " ".join(self.sentences).strip()
            if not joined:
                return None
            resolved = [(v, w) for v, w in zip(self.vecs, self.tokens) if v is not None]
            if resolved:
                vecs_only, weights_only = zip(*resolved)
                mean = weighted_mean(list(vecs_only), list(weights_only))
                vector = mean if mean.size else None
            else:
                vector = None
            return {"text": joined, "vector": vector}

        def clear(self) -> None:
            self.sentences.clear()
            self.vecs.clear()
            self.tokens.clear()
            self.total_tokens = 0
            self.sum_vec = None
            self.sum_weight = 0.0

    def cohesion_exceeds(builder: ChunkBuilder, vec: Optional[np.ndarray], tok: int) -> bool:
        if builder.sum_vec is None or builder.sum_weight == 0 or vec is None:
            return False
        current_mean = builder.sum_vec / builder.sum_weight
        if not current_mean.size:
            return False
        new_sum_vec = builder.sum_vec + (vec * tok)
        new_sum_weight = builder.sum_weight + tok
        if new_sum_weight == 0:
            return False
        new_mean = new_sum_vec / new_sum_weight
        if not new_mean.size:
            return False
        similarity = cosine(current_mean, new_mean)
        if similarity <= 0:
            return True
        drop = 1.0 - similarity
        return drop > cohesion_drop

    chunks: List[Dict[str, Any]] = []
    builder = ChunkBuilder()

    for sent, vec, tok in zip(sentences, vecs, token_counts):
        if builder.sentences:
            token_limit_hit = max_tokens > 0 and (builder.total_tokens + tok > max_tokens)
            cohesion_hit = builder.total_tokens >= min_tokens and cohesion_exceeds(builder, vec, tok)
            if token_limit_hit or cohesion_hit:
                maybe_chunk = builder.build()
                if maybe_chunk is not None:
                    chunks.append(maybe_chunk)
                if overlap > 0:
                    tail_items = list(zip(builder.sentences, builder.vecs, builder.tokens))[-overlap:]
                else:
                    tail_items = []
                builder.clear()
                for tail_sent, tail_vec, tail_tok in tail_items:
                    builder.append(tail_sent, tail_vec, tail_tok)
        builder.append(sent, vec, tok)

    final_chunk = builder.build()
    if final_chunk is not None:
        chunks.append(final_chunk)

    return chunks

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
    mode = settings.chunking_mode.lower().strip()
    semantic_mode = mode == "semantic"

    if semantic_mode:
        for ch in base_chunks:
            subs = semantic_chunking_by_sentences(settings, ch["text"], embedder, cache)
            for s in subs:
                vector = s["vector"]
                results.append({
                    "id": make_chunk_id(s["text"]),
                    "text": s["text"],
                    "vector": vector.tolist() if isinstance(vector, np.ndarray) else None,
                    "meta": ch["meta"] | {"parent_type": "semantic_chunk", "source": source},
                })
        return results

    ready_texts: List[str] = []
    idx_map: List[int] = []

    for ch in base_chunks:
        n_tokens = token_len(ch["text"], settings.token_encoding_name)
        # Long chunks → token-limited parts + sentence-level semantic pooling for vectors
        if n_tokens > settings.max_tokens_per_subchunk:
            subs = token_part_vectorization(settings, ch["text"], embedder, cache)
            for s in subs:
                vector = s["vector"]
                results.append({
                    "id": make_chunk_id(s["text"]),
                    "text": s["text"],
                    "vector": vector.tolist() if isinstance(vector, np.ndarray) else None,
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
        vecs: List[Optional[np.ndarray]] = [None] * len(flat)
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

from typing import Any, Dict, List

import numpy as np

from src.chunking.cache import DiskVectorCache
from src.chunking.config import Settings
from src.chunking.embed_gemini import GeminiEmbedder
from src.chunking.splitter import split_by_markdown
from src.chunking.utils import make_chunk_id, char_len, cosine, sentence_split, weighted_mean

def semantic_subchunking(settings: Settings, long_text: str,
                         embedder: GeminiEmbedder, cache: DiskVectorCache) -> List[Dict[str, Any]]:
    '''Break a long passage into semantically coherent sub-chunks backed by embeddings.

    The text is sentence-tokenised, each sentence vector is resolved through the provided
    cache/embedder pair, and the function grows chunks greedily while tracking a
    character-weighted centroid. Growth stops when the next sentence would breach the
    ``max_chars_per_subchunk`` limit or reduce cosine cohesion beyond ``cohesion_drop`` once
    the current chunk has at least ``min_chars_per_subchunk`` characters. Each emitted
    sub-chunk carries the aggregated text and a weighted mean embedding; optional backward
    overlap is controlled by ``overlap_chars``.
    '''
    sents = sentence_split(long_text)
    if not sents:
        return [{"text": long_text, "vector": None}]

    # Embed sentences with cache (pay once per sentence)
    vecs: List[np.ndarray] = []
    need: List[str] = []
    idx_map: List[int] = []

    for i, s in enumerate(sents):
        v = cache.get(s)
        if v is None:
            need.append(s)
            idx_map.append(i)
            vecs.append(None)  # placeholder
        else:
            vecs.append(v)

    if need:
        new_vecs = embedder.embed_batch(need)
        for k, v in enumerate(new_vecs):
            pos = idx_map[k]
            vecs[pos] = v
            cache.set(sents[pos], v)

    sent_chars = [char_len(s) for s in sents]

    # Greedy build with cohesion drop + length ceiling, with overlap
    subs: List[Dict[str, Any]] = []
    cur_idx = 0
    while cur_idx < len(sents):
        acc_text: List[str] = []
        acc_vecs: List[np.ndarray] = []
        acc_chars = 0
        centroid = None
        i = cur_idx
        while i < len(sents):
            cand_t, cand_v, cand_c = sents[i], vecs[i], sent_chars[i]
            if not acc_vecs:
                acc_text.append(cand_t); acc_vecs.append(cand_v)
                acc_chars += cand_c; centroid = cand_v.copy(); i += 1; continue

            new_centroid = weighted_mean(
                acc_vecs + [cand_v],
                [char_len(t) for t in acc_text] + [cand_c]
            )
            sim_before = cosine(centroid, cand_v)
            sim_after  = cosine(new_centroid, cand_v)
            drop = sim_before - sim_after

            will_exceed = (acc_chars + cand_c) > settings.max_chars_per_subchunk
            enough_len  = acc_chars >= settings.min_chars_per_subchunk
            semantic_cut = (drop > settings.cohesion_drop) and enough_len

            if will_exceed or semantic_cut:
                break

            acc_text.append(cand_t); acc_vecs.append(cand_v)
            acc_chars += cand_c; centroid = new_centroid; i += 1

        sc_text = " ".join(acc_text).strip()
        sc_vec  = weighted_mean(acc_vecs, [char_len(t) for t in acc_text])
        subs.append({"text": sc_text, "vector": sc_vec})

        if settings.overlap_chars > 0 and i < len(sents):
            back = i - 1; overlap = 0
            while back >= cur_idx and overlap < settings.overlap_chars:
                overlap += sent_chars[back]; back -= 1
            cur_idx = max(back + 1, i)
        else:
            cur_idx = i

    return subs


def run_pipeline(md_text: str, source: str, settings: Settings) -> List[Dict[str, Any]]:
    base_chunks = split_by_markdown(md_text)
    cache = DiskVectorCache(settings.cache_dir)
    embedder = GeminiEmbedder(settings)

    results: List[Dict[str, Any]] = []
    ready_texts: List[str] = []
    idx_map: List[int] = []

    for ch in base_chunks:
        n = char_len(ch["text"])
        if n > settings.max_chars_per_subchunk:
            subs = semantic_subchunking(settings, ch["text"], embedder, cache) 
            for s in subs:
                results.append({
                    "id": make_chunk_id(s["text"]),
                    "text": s["text"],
                    "vector": s["vector"].tolist() if s["vector"] is not None else None,
                    "meta": ch["meta"] | {"parent_type": "semantic_subchunk", "source": source},
                })
                print(results)
        else:
            ready_texts.append(ch["text"])
            idx_map.append(len(results))
            results.append({
                "id": make_chunk_id(ch["text"]),
                "text": ch["text"],
                "vector": None,
                "meta": ch["meta"] | {"parent_type": "header_chunk", "source": source},
            })

    # For the short chunks: embed sentences once, then weighted mean per chunk
    if ready_texts:
        # sentence-level cache+embed
        sent_lists = [sentence_split(t) for t in ready_texts]
        flat: List[str] = []
        owners: List[int] = []  # map flat index → which chunk
        for ci, sents in enumerate(sent_lists):
            for s in sents:
                flat.append(s)
                owners.append(ci)

        cache = DiskVectorCache(settings.cache_dir)
        embedder = GeminiEmbedder(settings)

        # resolve cache
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

        # aggregate back per chunk
        start = 0
        for chunk_idx, sents in enumerate(sent_lists):
            end = start + len(sents)
            s_vecs = vecs[start:end]
            weights = [char_len(s) for s in sents]
            mean_vec = weighted_mean(s_vecs, weights) if s_vecs else np.array([], dtype=np.float32)
            results_idx = idx_map[chunk_idx]
            results[results_idx]["vector"] = mean_vec.tolist() if mean_vec.size else None
            start = end

    return results

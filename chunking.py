# A production‑ready scaffold that follows your 3‑step plan:

# 1. **Split by Markdown structure** → initial chunks
# 2. **Semantic sub‑chunk only if long** → sentence embeddings once; **weighted mean pooling** for sub‑chunks
# 3. **Batch the rest** → sentence embeddings once, then **weighted mean** to get chunk vectors

# config.py
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    genai_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_emb: str = os.getenv("GEMINI_EMBED_MODEL", "models/text-embedding-004")

    # sizing by characters (model-agnostic & simple); adjust as needed
    max_chars_per_subchunk: int = int(os.getenv("MAX_CHARS", 3000))
    min_chars_per_subchunk: int = int(os.getenv("MIN_CHARS", 700))
    overlap_chars: int = int(os.getenv("OVERLAP_CHARS", 300))
    cohesion_drop: float = float(os.getenv("COHESION_DROP", 0.12))


    # batch size for API calls
    batch_size: int = int(os.getenv("BATCH_SIZE", 128))


    # caching
    cache_dir: str = os.getenv("CACHE_DIR", ".chunk_cache")

# chunk_md/utils.py
import hashlib
import json
import numpy as np
import re
from typing import List
 
from pythainlp.tokenize import sent_tokenize as thai_sent_tokenize 


def make_chunk_id(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()
 
def char_len(s: str) -> int:
    return len(s)

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def weighted_mean(vectors: List[np.ndarray], weights: List[float]) -> np.ndarray:
    if not vectors:
        return np.array([], dtype=np.float32)
    w = np.array(weights, dtype=np.float32)
    v = np.vstack(vectors)
    return (v * (w[:, None] / (w.sum() + 1e-9))).sum(axis=0)


def sentence_split(text: str, lang: str = "auto") -> List[str]:
    """
    Lightweight sentence split. Always rely on PyThaiNLP when available;
    useful for Thai-heavy corpora where regex heuristics fall short.
    """
    t = text.strip()
    if not t:
        return []

    if not thai_sent_tokenize:
        raise RuntimeError("pythainlp is required for sentence splitting")

    try:
        sentences = [s.strip() for s in thai_sent_tokenize(t) if s.strip()]
    except ModuleNotFoundError as exc:
        if exc.name == 'pycrfsuite':
            raise RuntimeError('pythainlp sentence tokenizer needs python-crfsuite. Install it with `pip install python-crfsuite`.') from exc
        raise
    return sentences

def to_jsonl(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


# chunk_md/splitter.py
from langchain_text_splitters import MarkdownHeaderTextSplitter
from typing import List, Dict, Any


HEADERS = [("#", "H1"), ("##", "H2"), ("###", "H3")]

 
def split_by_markdown(md_text: str) -> List[Dict[str, Any]]:
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS)
    docs = splitter.split_text(md_text)
    out = []
    for d in docs:
        meta = d.metadata
        out.append({
            "text": d.page_content,
            "meta": {
                "h1": meta.get("H1", ""),
                "h2": meta.get("H2", ""),
                "h3": meta.get("H3", ""),
            },
        })
    return out


# chunk_md/cache.py
import os
import hashlib
import numpy as np
from typing import Optional


class DiskVectorCache:
    def __init__(self, root_dir: str):
        self.root = root_dir
        os.makedirs(self.root, exist_ok=True)

    # un1 normalize html-to-markdown text before hashing
    # blake3
    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


    def get(self, text: str) -> Optional[np.ndarray]:
        key = self._key(text)
        path = os.path.join(self.root, f"{key}.npy")
        if os.path.exists(path):
            try:
                return np.load(path)
            except Exception:
                return None
        return None

    def set(self, text: str, vec: np.ndarray) -> None:
        key = self._key(text)
        path = os.path.join(self.root, f"{key}.npy")
        np.save(path, vec.astype(np.float32))


# chunk_md/embed_gemini.py
import google.generativeai as genai
import numpy as np
from typing import List

 
class GeminiEmbedder:
    def __init__(self, settings: Settings):
        if not settings.genai_api_key:
            raise RuntimeError("GEMINI_API_KEY is required")
        genai.configure(api_key=settings.genai_api_key)
        self.model = settings.model_emb
        self.bs = settings.batch_size


    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []
        out: List[np.ndarray] = []
        B = self.bs
        for i in range(0, len(texts), B):
            batch = texts[i:i+B]
            for text in batch:
                resp = genai.embed_content(
                    model=self.model,
                    content=text,
                )
                out.append(np.array(resp["embedding"], dtype=np.float32))
        return out
    

# chunk_md/pipeline.py
def semantic_subchunking(settings: Settings, long_text: str,
                         embedder: GeminiEmbedder, cache: DiskVectorCache) -> List[Dict[str, Any]]:
    sents = sentence_split(long_text, lang="auto")
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
        sent_lists = [sentence_split(t, lang="auto") for t in ready_texts]
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


import requests

def read_input(src: str) -> str:
    p = src.strip()
    if p.startswith("http://") or p.startswith("https://"):
        if requests is None:
            raise RuntimeError("requests not available. `uv add requests` or use local file.")
        r = requests.get(p, timeout=30)
        r.raise_for_status()
        return r.text
    return Path(p).read_text(encoding="utf-8")

source = "output/2509.04343v1.md"
out = "chunks.jsonl"
settings = Settings()
md_text = read_input(source)
chunks = run_pipeline(md_text, source=source, settings=settings)

out = Path(out)
with out.open("w", encoding="utf-8") as f:
    for ch in chunks:
        f.write(json.dumps(ch, ensure_ascii=False) + "\n")

print(f"Wrote {len(chunks)} chunks → {out}")

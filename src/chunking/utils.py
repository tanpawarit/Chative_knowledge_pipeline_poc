import hashlib
import json
import numpy as np
import re
from typing import List
# import pycrfsuite
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
  

def sentence_split(text: str, *, prefer_thai: bool = True) -> List[str]: 
    # regex for classify lang (English/general)
    _SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n{2,}") 

    _THAI_RE = re.compile(r"[\u0E00-\u0E7F]")

    t = text.strip()
    if not t:
        return []

    has_thai = bool(_THAI_RE.search(t))
    if prefer_thai and has_thai: 
        return [s.strip() for s in thai_sent_tokenize(t) if s.strip()]
 
    return [s.strip() for s in _SENT_SPLIT_RE.split(t) if s.strip()]
 

def to_jsonl(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)

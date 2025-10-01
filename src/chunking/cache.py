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
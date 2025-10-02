import hashlib


def make_chunk_id(text: str) -> str:
    """Generate a stable chunk identifier from the chunk text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()

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
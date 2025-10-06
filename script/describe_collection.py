#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Set

from pymilvus import MilvusClient

from src.shared.config import MilvusSettings


@dataclass
class DocSummary:
    rows: int = 0
    totals: Set[int] = field(default_factory=set)

    def register(self, row: Dict[str, object]) -> None:
        self.rows += 1
        total = row.get("total_chunks")
        if total is not None:
            try:
                self.totals.add(int(total))
            except (TypeError, ValueError):
                pass

    def totals_display(self) -> str:
        if not self.totals:
            return "-"
        values = sorted(self.totals)
        return ",".join(str(v) for v in values)

    def status(self) -> str:
        if not self.totals:
            return "no total"
        if len(self.totals) > 1:
            return "mixed totals"
        total = next(iter(self.totals))
        if total != self.rows:
            return "rows!=total"
        return "ok"


def build_client(settings: MilvusSettings) -> MilvusClient:
    kwargs = {"uri": settings.uri}
    token = settings.token()
    if token:
        kwargs["token"] = token
    return MilvusClient(**kwargs)


def iter_rows(
    client: MilvusClient,
    collection: str,
    *,
    output_fields: Iterable[str],
    filter_expr: Optional[str] = None,
    batch_size: int = 1000,
    limit: Optional[int] = None,
) -> Iterator[Dict[str, object]]:
    remaining = None if limit is None else max(limit, 0)

    def take_count(requested: int) -> int:
        if remaining is None:
            return requested
        return min(requested, remaining)

    offset = 0
    while True:
        current_limit = take_count(batch_size)
        if current_limit <= 0:
            return
        rows = client.query(
            collection_name=collection,
            filter=filter_expr,
            output_fields=list(output_fields),
            limit=current_limit,
            offset=offset,
        )
        if not rows:
            return
        for row in rows:
            yield row
            if remaining is not None:
                remaining -= 1
                if remaining <= 0:
                    return
        fetched = len(rows)
        if fetched < current_limit:
            return
        offset += fetched


def format_doc_name(name: str, *, width: int = 60) -> str:
    if len(name) <= width:
        return name
    cutoff = width - 3
    return name[:cutoff] + "..."


WORKSPACE_ID: Optional[str] = None  # Override to target a specific partition/workspace.
SCAN_LIMIT: Optional[int] = None  # Set to an int to stop after the first N rows.
BATCH_SIZE: int = 1000  # Tune batch size to match Milvus limits/performance.


def main(
    *,
    workspace_id: Optional[str] = WORKSPACE_ID,
    limit: Optional[int] = SCAN_LIMIT,
    batch_size: int = BATCH_SIZE,
) -> int:

    settings = MilvusSettings()
    if not settings.is_configured():
        print("Milvus settings are incomplete. Set MILVUS_ADDR and MILVUS_COLLECTION.", file=sys.stderr)
        return 1

    try:
        settings.ensure_ready()
    except RuntimeError as exc:
        print(f"{exc}", file=sys.stderr)
        return 1

    workspace_id = workspace_id or settings.partition_key_value or ""
    workspace_field = "workspace_id"
    filter_expr = None
    if workspace_id:
        escaped = workspace_id.replace('"', '\\"')
        filter_expr = f'{workspace_field} == "{escaped}"'

    client = build_client(settings)
    doc_summaries: Dict[str, DocSummary] = {}
    total_rows = 0

    try:
        for row in iter_rows(
            client,
            settings.collection_name,
            output_fields=["doc_name", "total_chunks"],
            filter_expr=filter_expr,
            batch_size=max(1, batch_size),
            limit=limit,
        ):
            doc_name = str(row.get("doc_name") or "<missing>")
            summary = doc_summaries.setdefault(doc_name, DocSummary())
            summary.register(row)
            total_rows += 1
    except Exception as exc:
        print(f"Failed to query Milvus: {exc}", file=sys.stderr)
        return 1

    print(f"Collection: {settings.collection_name}")
    if workspace_id:
        print(f"Workspace filter: {workspace_id}")
    print(f"Rows scanned: {total_rows}")
    print(f"Unique documents: {len(doc_summaries)}")
    if limit is not None and total_rows == limit:
        print("Warning: limit reached; results may be incomplete.")

    if not doc_summaries:
        return 0

    header = f"{'Doc Name':60} {'Rows':>8} {'TotalChunks':>14} {'Status':>12}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for doc_name in sorted(doc_summaries):
        summary = doc_summaries[doc_name]
        print(
            f"{format_doc_name(doc_name):60} "
            f"{summary.rows:8d} "
            f"{summary.totals_display():>14} "
            f"{summary.status():>12}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

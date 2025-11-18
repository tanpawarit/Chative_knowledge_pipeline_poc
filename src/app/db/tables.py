"""Piccolo table mappings for application data."""

from __future__ import annotations

from piccolo.columns import BigInt, Text, Timestamptz, Varchar
from piccolo.table import Table


class DocumentTable(Table, tablename="documents", schema="public"):
    """Minimal mapping for the `documents` table.

    Note: Piccolo expects `tablename` and `schema` to be specified as class
    arguments on the Table subclass (not via an inner Meta class). Using the
    wrong pattern causes the default auto-generated name (e.g. "document_table")
    to be used, which doesn't match our actual table name "documents".
    """

    id = Varchar(length=64, primary_key=True)
    workspace_id = Varchar(length=128, index=True)
    checksum = Varchar(length=128)
    filename = Text()
    file_extension = Varchar(length=16, null=True)
    mime_type = Varchar(length=255)
    size_bytes = BigInt()
    storage_provider = Varchar(length=32)
    file_path = Text()
    created_at = Timestamptz()
    updated_at = Timestamptz()
    deleted_at = Timestamptz(null=True)


__all__ = ["DocumentTable"]

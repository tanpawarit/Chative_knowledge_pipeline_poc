"""Simple storage client supporting Cloudflare R2 and local files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, TYPE_CHECKING
from urllib.parse import urlparse

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from src.shared.config.env import optional_env, require_env
from src.shared.logging.logger import get_logger

if TYPE_CHECKING:  # pragma: no cover
    from src.app.repositories import DocumentRecord

logger = get_logger(__name__)


@dataclass(slots=True)
class FetchedDocument:
    """Represents an in-memory document fetched from storage."""

    data: bytes


class StorageClient:
    """Fetch documents from storage with minimal configuration."""

    def __init__(
        self,
        *,
        r2_endpoint: Optional[str] = None,
        r2_access_key: Optional[str] = None,
        r2_secret_key: Optional[str] = None,
        r2_bucket: Optional[str] = None,
    ) -> None:
        self._r2_endpoint = (r2_endpoint or "").strip()
        self._r2_access_key = (r2_access_key or "").strip()
        self._r2_secret_key = (r2_secret_key or "").strip()
        self._r2_bucket = (r2_bucket or "").strip()
        self._r2_client: Optional[BaseClient] = None

    @classmethod
    def from_env(cls) -> "StorageClient":
        account_id = require_env("R2_ACCOUNT_ID")
        endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
        bucket = optional_env("R2_CUSTOMER_UPLOAD_BUCKET")
        return cls(
            r2_endpoint=endpoint,
            r2_access_key=optional_env("R2_ACCESS_KEY_ID"),
            r2_secret_key=optional_env("R2_SECRET_ACCESS_KEY"),
            r2_bucket=bucket,
        )

    def fetch(self, document: "DocumentRecord") -> FetchedDocument:
        provider = (document.storage_provider or "").strip().lower()
        if provider == "local":
            return self._fetch_local(document.file_path)
        if provider == "r2":
            return self._fetch_r2(document)
        raise ValueError(f"Unsupported storage provider: {document.storage_provider}")

    def _fetch_local(self, path_value: str) -> FetchedDocument:
        if not path_value:
            raise ValueError("file_path is required for local storage")
        path = Path(path_value).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Local file not found: {path}")
        data = path.read_bytes()
        return FetchedDocument(data=data)

    def _fetch_r2(self, document: "DocumentRecord") -> FetchedDocument:
        client = self._ensure_r2_client()
        bucket, key = self._resolve_bucket_key(document.file_path)
        if not bucket:
            raise ValueError("R2 bucket is required to download documents")
        if not key:
            raise ValueError("R2 object key is required to download documents")

        response = client.get_object(Bucket=bucket, Key=key)
        body = response.get("Body")
        if body is None:
            raise RuntimeError("R2 download missing response body")
        try:
            data = body.read()
        finally:
            body.close()

        logger.info(
            "Fetched document from R2",
            document_id=document.id,
            bucket=bucket,
            key=key,
            bytes=len(data),
        )
        return FetchedDocument(data=data)

    def _ensure_r2_client(self) -> BaseClient:
        if self._r2_client is not None:
            return self._r2_client
        if not (self._r2_endpoint and self._r2_access_key and self._r2_secret_key):
            raise RuntimeError("R2 credentials are not configured")
        # Cloudflare R2 requires path-style addressing and SigV4.
        # Region "auto" is recommended by Cloudflare for signature calculation.
        self._r2_client = boto3.client(
            "s3",
            endpoint_url=self._r2_endpoint,
            aws_access_key_id=self._r2_access_key,
            aws_secret_access_key=self._r2_secret_key,
            region_name="auto",
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )
        return self._r2_client

    def _resolve_bucket_key(self, path_value: str) -> Tuple[Optional[str], str]:
        """Resolve (bucket, key) using configured default bucket.

        Rules:
        - When given a URI with scheme s3:// or r2://, respect its bucket/key.
        - When a default bucket is configured (env), and the provided path does
          not start with "<bucket>/", treat the entire value as the key and use
          the default bucket.
        - When the provided path starts with "<bucket>/", strip the prefix and
          keep that bucket.
        - As a final fallback (no default bucket), split on the first '/'.
        """
        path_value = (path_value or "").strip()
        if not path_value:
            return None, ""

        parsed = urlparse(path_value)
        if parsed.scheme in {"s3", "r2"}:
            bucket = parsed.netloc or None
            key = parsed.path.lstrip("/")
            return bucket, key

        cleaned = path_value.lstrip("/")
        if self._r2_bucket:
            prefix = f"{self._r2_bucket}/"
            if cleaned.startswith(prefix):
                # Path includes the bucket prefix; strip it.
                return self._r2_bucket, cleaned[len(prefix) :]
            # Path does not include bucket; use default bucket as-is.
            return self._r2_bucket, cleaned

        # No default bucket configured; try to infer from path.
        if "/" not in cleaned:
            return None, cleaned
        bucket, key = cleaned.split("/", 1)
        return (bucket or None), key


__all__ = ["FetchedDocument", "StorageClient"]

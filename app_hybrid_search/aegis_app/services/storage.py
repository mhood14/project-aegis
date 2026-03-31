import json
from datetime import datetime
from typing import Any, Iterable

from flask import current_app

from .azure_clients import get_blob_service_client


class StorageService:
    def __init__(self):
        self.blob_service = get_blob_service_client()

    def ensure_container(self, container_name: str) -> None:
        container = self.blob_service.get_container_client(container_name)
        try:
            container.create_container()
        except Exception:
            pass

    def upload_bytes(self, container_name: str, blob_name: str, data: bytes, content_type: str | None = None) -> None:
        self.ensure_container(container_name)
        blob = self.blob_service.get_blob_client(container=container_name, blob=blob_name)
        blob.upload_blob(data, overwrite=True, content_type=content_type)

    def upload_json(self, container_name: str, blob_name: str, payload: dict[str, Any]) -> None:
        self.upload_bytes(
            container_name=container_name,
            blob_name=blob_name,
            data=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
            content_type="application/json",
        )

    def download_bytes(self, container_name: str, blob_name: str) -> bytes:
        blob = self.blob_service.get_blob_client(container=container_name, blob=blob_name)
        return blob.download_blob().readall()

    def download_json(self, container_name: str, blob_name: str) -> dict[str, Any]:
        return json.loads(self.download_bytes(container_name, blob_name).decode("utf-8"))

    def list_blob_names(self, container_name: str, prefix: str | None = None) -> Iterable[str]:
        container = self.blob_service.get_container_client(container_name)
        for blob in container.list_blobs(name_starts_with=prefix):
            yield blob.name

    def list_processed_documents(self, scope: str, limit: int = 10) -> list[dict[str, Any]]:
        docs: list[dict[str, Any]] = []
        prefix = f"{scope}/"
        for blob_name in self.list_blob_names(current_app.config["PROCESSED_DOCS_CONTAINER"], prefix=prefix):
            if not blob_name.endswith(".json"):
                continue
            doc = self.download_json(current_app.config["PROCESSED_DOCS_CONTAINER"], blob_name)
            docs.append(
                {
                    "document_id": doc.get("document_id"),
                    "filename": doc.get("original_filename"),
                    "scope": doc.get("scope"),
                    "uploaded_at": doc.get("uploaded_at"),
                    "chunk_count": len(doc.get("chunks", [])),
                }
            )

        def _dt(value: str | None) -> datetime:
            if not value:
                return datetime.min
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except Exception:
                return datetime.min

        docs.sort(key=lambda item: _dt(item.get("uploaded_at")), reverse=True)
        return docs[:limit]

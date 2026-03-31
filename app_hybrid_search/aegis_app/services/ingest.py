import io
import re
import uuid
from datetime import datetime, timezone

from flask import current_app
from pypdf import PdfReader
from werkzeug.utils import secure_filename

from .audit import log_error, log_event
from .embeddings import generate_embedding
from .search_index import index_document_chunks
from .storage import StorageService


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _validate_extension(filename: str) -> None:
    ext = _file_ext(filename)
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        raise ValueError(f"Unsupported file type: .{ext}")


def extract_text_from_pdf(content_bytes: bytes) -> tuple[str, list[dict]]:
    reader = PdfReader(io.BytesIO(content_bytes))
    page_chunks = []
    combined = []

    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            page_chunks.append({"page_number": index, "text": text})
            combined.append(text)

    return "\n\n".join(combined), page_chunks


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[dict]:
    chunks = []
    start = 0
    chunk_index = 1
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_text_value = text[start:end].strip()
        if chunk_text_value:
            chunks.append(
                {
                    "chunk_id": f"chunk-{chunk_index:04d}",
                    "page_number": None,
                    "text": chunk_text_value,
                }
            )
            chunk_index += 1

        if end >= text_len:
            break

        start = max(0, end - overlap)

    return chunks


def _should_index_hybrid() -> bool:
    strategy = current_app.config["RETRIEVAL_STRATEGY"]
    return strategy in {"hybrid", "vector"}


def process_uploaded_file(
    filename: str,
    content_bytes: bytes,
    uploaded_by: str,
    scope: str,
    content_type: str,
    request_id: str | None = None,
    *,
    document_category: str = "normal",
    is_test_document: bool = False,
) -> dict:
    storage = StorageService()
    safe_name = secure_filename(filename or "")
    document_id = f"doc-{uuid.uuid4().hex[:12]}"
    raw_blob_name = f"{scope}/{document_id}/{safe_name}"

    try:
        log_event(
            "document_upload_started",
            {
                "request_id": request_id,
                "document_id": document_id,
                "scope": scope,
                "filename": safe_name,
                "uploaded_by": uploaded_by,
                "content_type": content_type,
                "byte_count": len(content_bytes or b""),
                "document_category": document_category,
                "is_test_document": is_test_document,
            },
            message="Document upload started",
        )

        _validate_extension(filename)

        storage.upload_bytes(
            container_name=current_app.config["RAW_DOCS_CONTAINER"],
            blob_name=raw_blob_name,
            data=content_bytes,
            content_type=content_type,
        )

        log_event(
            "document_upload_completed",
            {
                "request_id": request_id,
                "document_id": document_id,
                "scope": scope,
                "raw_blob_name": raw_blob_name,
            },
            message="Raw document uploaded",
        )

        log_event(
            "document_processing_started",
            {
                "request_id": request_id,
                "document_id": document_id,
                "scope": scope,
                "filename": safe_name,
            },
            message="Document processing started",
        )

        ext = _file_ext(filename)

        if ext in {"txt", "md"}:
            extracted_text = content_bytes.decode("utf-8", errors="ignore")
            page_info = []
        elif ext == "pdf":
            extracted_text, page_info = extract_text_from_pdf(content_bytes)
        else:
            raise ValueError(f"Unsupported extension: {ext}")

        normalized = normalize_text(extracted_text)
        chunks = chunk_text(
            normalized,
            chunk_size=current_app.config["CHUNK_SIZE_CHARS"],
            overlap=current_app.config["CHUNK_OVERLAP_CHARS"],
        )

        if _should_index_hybrid():
            for chunk in chunks:
                chunk["embedding"] = generate_embedding(
                    chunk["text"],
                    request_id=request_id,
                )

        processed = {
            "document_id": document_id,
            "original_filename": safe_name,
            "scope": scope,
            "uploaded_by": uploaded_by,
            "uploaded_at": _utc_now(),
            "raw_blob_name": raw_blob_name,
            "processing_status": "ready",
            "page_count": len(page_info) if page_info else None,
            "document_category": document_category,
            "is_test_document": is_test_document,
            "chunks": chunks,
        }

        processed_blob_name = f"{scope}/{document_id}.json"
        storage.upload_json(
            container_name=current_app.config["PROCESSED_DOCS_CONTAINER"],
            blob_name=processed_blob_name,
            payload=processed,
        )

        if _should_index_hybrid():
            index_document_chunks(
                processed,
                request_id=request_id,
                index_name=current_app.config["AZURE_SEARCH_HYBRID_INDEX_NAME"],
                include_vectors=True,
            )
        else:
            index_document_chunks(
                processed,
                request_id=request_id,
                index_name=current_app.config["AZURE_SEARCH_INDEX_NAME"],
                include_vectors=False,
            )

        log_event(
            "document_processing_completed",
            {
                "request_id": request_id,
                "document_id": document_id,
                "scope": scope,
                "chunk_count": len(chunks),
                "processed_blob_name": processed_blob_name,
                "retrieval_strategy": current_app.config["RETRIEVAL_STRATEGY"],
            },
            message="Document processing completed",
        )

        return {
            "request_id": request_id,
            "document_id": document_id,
            "scope": scope,
            "status": "ready",
            "chunk_count": len(chunks),
            "raw_blob_name": raw_blob_name,
            "processed_blob_name": processed_blob_name,
        }

    except Exception as ex:
        log_error(
            "document_processing_failed",
            ex,
            {
                "request_id": request_id,
                "document_id": document_id,
                "scope": scope,
                "filename": safe_name,
                "raw_blob_name": raw_blob_name,
            },
            message="Document processing failed",
        )
        raise
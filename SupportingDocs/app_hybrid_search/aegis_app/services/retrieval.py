from __future__ import annotations

from azure.search.documents.models import VectorizedQuery
from flask import current_app

from .audit import log_error, log_event
from .azure_clients import get_search_client
from .embeddings import generate_embedding


def _escape_odata(value: str) -> str:
    return value.replace("'", "''")


def _build_filter(scope: str) -> str:
    scope_escaped = _escape_odata(scope)

    if scope == "security-tests":
        return f"scope eq '{scope_escaped}'"

    return f"scope eq '{scope_escaped}' and is_test_document eq false"


def _shape_results(results, scope: str, *, fallback: bool = False) -> list[dict]:
    chunks = []
    for item in results:
        chunks.append(
            {
                "score": item.get("@search.score", 0),
                "document_id": item.get("document_id"),
                "filename": item.get("filename", "unknown"),
                "scope": item.get("scope", scope),
                "chunk_id": item.get("chunk_id"),
                "page_number": item.get("page_number"),
                "text": item.get("content", ""),
                "uploaded_at": item.get("uploaded_at"),
                "fallback": fallback,
            }
        )
    return chunks


def _keyword_search(question: str, scope: str, filter_text: str, max_chunks: int) -> list[dict]:
    client = get_search_client(index_name=current_app.config["AZURE_SEARCH_INDEX_NAME"])
    results = client.search(
        search_text=question,
        filter=filter_text,
        top=max_chunks,
        include_total_count=True,
    )
    return _shape_results(results, scope, fallback=False)


def _hybrid_search(question: str, scope: str, filter_text: str, max_chunks: int, request_id: str | None) -> list[dict]:
    client = get_search_client(index_name=current_app.config["AZURE_SEARCH_HYBRID_INDEX_NAME"])
    question_vector = generate_embedding(question, request_id=request_id)

    vector_query = VectorizedQuery(
        vector=question_vector,
        k_nearest_neighbors=max_chunks,
        fields="content_vector",
    )

    results = client.search(
        search_text=question,
        vector_queries=[vector_query],
        filter=filter_text,
        top=max_chunks,
        include_total_count=True,
    )
    return _shape_results(results, scope, fallback=False)


def _fallback_search(scope: str, filter_text: str, max_chunks: int, *, hybrid: bool) -> list[dict]:
    index_name = (
        current_app.config["AZURE_SEARCH_HYBRID_INDEX_NAME"]
        if hybrid
        else current_app.config["AZURE_SEARCH_INDEX_NAME"]
    )
    client = get_search_client(index_name=index_name)

    results = client.search(
        search_text="*",
        filter=filter_text,
        top=max_chunks,
        include_total_count=True,
    )
    return _shape_results(results, scope, fallback=True)


def retrieve_chunks(
    question: str,
    scope: str,
    request_id: str | None = None,
    max_chunks: int | None = None,
) -> list[dict]:
    max_chunks = max_chunks or current_app.config["RETRIEVAL_MAX_CHUNKS"]
    strategy = current_app.config["RETRIEVAL_STRATEGY"]
    filter_text = _build_filter(scope)

    try:
        if strategy == "hybrid":
            chunks = _hybrid_search(question, scope, filter_text, max_chunks, request_id)
            strategy_used = "hybrid"
        elif strategy == "vector":
            chunks = _hybrid_search(question, scope, filter_text, max_chunks, request_id)
            strategy_used = "vector_like_hybrid"
        else:
            chunks = _keyword_search(question, scope, filter_text, max_chunks)
            strategy_used = "keyword"

        if chunks:
            log_event(
                "retrieval_completed",
                {
                    "request_id": request_id,
                    "scope": scope,
                    "strategy": strategy_used,
                    "result_count": len(chunks),
                    "search_filter": filter_text,
                },
                message="Retrieval completed",
            )
            return chunks

        fallback_chunks = _fallback_search(
            scope,
            filter_text,
            max_chunks,
            hybrid=(strategy in {"hybrid", "vector"}),
        )

        log_event(
            "fallback_used",
            {
                "request_id": request_id,
                "scope": scope,
                "strategy": strategy_used,
                "initial_result_count": len(chunks),
                "fallback_result_count": len(fallback_chunks),
                "search_filter": filter_text,
            },
            message="Fallback retrieval used",
        )
        return fallback_chunks

    except Exception as ex:
        log_error(
            "application_error",
            ex,
            {
                "request_id": request_id,
                "scope": scope,
                "stage": "retrieve_chunks",
                "strategy": current_app.config["RETRIEVAL_STRATEGY"],
            },
            message="Retrieval failed",
        )
        raise
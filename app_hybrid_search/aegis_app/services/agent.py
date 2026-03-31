from __future__ import annotations

from .audit import log_error, log_event
from .authz import authorize_scope_or_raise
from .llm import generate_grounded_answer
from .retrieval import retrieve_chunks

def answer_question(
    *,
    user_context: dict,
    question: str,
    scope: str,
    request_id: str | None = None,
) -> dict:
    try:
        authorize_scope_or_raise(user_context, scope, request_id=request_id)

        chunks = retrieve_chunks(
            question=question,
            scope=scope,
            request_id=request_id,
        )

        fallback_used = any(chunk.get("fallback", False) for chunk in chunks)

        answer = generate_grounded_answer(
            question=question,
            chunks=chunks,
            request_id=request_id,
        )

        citations = [
            {
                "document_id": chunk.get("document_id"),
                "filename": chunk.get("filename"),
                "chunk_id": chunk.get("chunk_id"),
                "page_number": chunk.get("page_number"),
            }
            for chunk in chunks
        ]

        log_event(
            "llm_request_completed",
            {
                "request_id": request_id,
                "scope": scope,
                "chunk_count": len(chunks),
                "fallback_used": fallback_used,
            },
            message="LLM request completed",
        )

        return {
            "answer": answer,
            "citations": citations,
            "fallback_used": fallback_used,
        }

    except Exception as ex:
        log_error(
            "application_error",
            ex,
            {
                "request_id": request_id,
                "scope": scope,
                "stage": "answer_question",
            },
            message="Question answering failed",
        )
        raise
from __future__ import annotations

from .audit import log_error, log_event
from .azure_clients import get_openai_client


def generate_embedding(text: str, request_id: str | None = None) -> list[float]:
    client = get_openai_client()

    try:
        response = client.embeddings.create(
            model=_embedding_model_name(),
            input=text,
        )
        vector = response.data[0].embedding

        log_event(
            "embedding_generated",
            {
                "request_id": request_id,
                "vector_length": len(vector),
            },
            message="Embedding generated",
        )
        return vector

    except Exception as ex:
        log_error(
            "application_error",
            ex,
            {
                "request_id": request_id,
                "stage": "generate_embedding",
            },
            message="Embedding generation failed",
        )
        raise


def _embedding_model_name() -> str:
    from flask import current_app
    return current_app.config["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

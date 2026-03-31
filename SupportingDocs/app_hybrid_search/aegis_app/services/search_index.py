from __future__ import annotations

from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from .audit import log_event
from .azure_clients import get_search_client, get_search_index_client


def create_or_update_keyword_index(index_name: str, request_id: str | None = None) -> None:
    client = get_search_index_client()

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
        SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="scope", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
        SimpleField(name="filename", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="uploaded_by", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="uploaded_at", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="document_category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="is_test_document", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
    ]

    index = SearchIndex(name=index_name, fields=fields)
    client.create_or_update_index(index)

    log_event(
        "search_index_ready",
        {
            "request_id": request_id,
            "index_name": index_name,
            "index_type": "keyword",
        },
        message="Keyword index created or updated",
    )


def create_or_update_hybrid_index(index_name: str, vector_dimensions: int, request_id: str | None = None) -> None:
    client = get_search_index_client()

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
        SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="scope", type=SearchFieldDataType.String, filterable=True, facetable=True, sortable=True),
        SimpleField(name="filename", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="uploaded_by", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="uploaded_at", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="document_category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="is_test_document", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=vector_dimensions,
            vector_search_profile_name="aegis-vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="aegis-hnsw"),
        ],
        profiles=[
            VectorSearchProfile(
                name="aegis-vector-profile",
                algorithm_configuration_name="aegis-hnsw",
            )
        ],
    )

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
    )

    client.create_or_update_index(index)

    log_event(
        "search_index_ready",
        {
            "request_id": request_id,
            "index_name": index_name,
            "index_type": "hybrid",
            "vector_dimensions": vector_dimensions,
        },
        message="Hybrid index created or updated",
    )


def build_search_documents(processed_doc: dict, *, include_vectors: bool = False) -> list[dict]:
    docs = []
    document_id = processed_doc["document_id"]
    filename = processed_doc["original_filename"]

    for chunk in processed_doc.get("chunks", []):
        doc = {
            "id": f"{document_id}-{chunk['chunk_id']}",
            "document_id": document_id,
            "chunk_id": chunk["chunk_id"],
            "scope": processed_doc["scope"],
            "filename": filename,
            "uploaded_by": processed_doc.get("uploaded_by"),
            "uploaded_at": processed_doc.get("uploaded_at"),
            "document_category": processed_doc.get("document_category", "normal"),
            "is_test_document": bool(processed_doc.get("is_test_document", False)),
            "page_number": chunk.get("page_number"),
            "content": chunk.get("text", ""),
        }
        if include_vectors:
            doc["content_vector"] = chunk.get("embedding", [])
        docs.append(doc)

    return docs


def index_document_chunks(
    processed_doc: dict,
    *,
    request_id: str | None = None,
    index_name: str | None = None,
    include_vectors: bool = False,
) -> None:
    client = get_search_client(index_name=index_name)
    docs = build_search_documents(processed_doc, include_vectors=include_vectors)

    if not docs:
        return

    client.upload_documents(documents=docs)

    log_event(
        "search_chunks_indexed",
        {
            "request_id": request_id,
            "document_id": processed_doc.get("document_id"),
            "scope": processed_doc.get("scope"),
            "chunk_count": len(docs),
            "index_name": index_name,
            "include_vectors": include_vectors,
        },
        message="Processed chunks indexed into Azure AI Search",
    )
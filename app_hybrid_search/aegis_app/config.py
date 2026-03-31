import os


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    APP_TITLE = "Aegis AI Platform"

    RAW_DOCS_CONTAINER = os.getenv("RAW_DOCS_CONTAINER", "raw-documents")
    PROCESSED_DOCS_CONTAINER = os.getenv("PROCESSED_DOCS_CONTAINER", "processed-documents")

    DEFAULT_SCOPE = os.getenv("DEFAULT_SCOPE", "internal-docs")

    CHUNK_SIZE_CHARS = int(os.getenv("CHUNK_SIZE", "2000"))
    CHUNK_OVERLAP_CHARS = int(os.getenv("CHUNK_OVERLAP", "200"))

    RETRIEVAL_MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "5"))

    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
    MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
    MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))

    ALLOWED_EXTENSIONS = {"txt", "md", "pdf"}

    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    STORAGE_ACCOUNT_URL = os.getenv("STORAGE_ACCOUNT_URL")

    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "aegis-doc-chunks")
    AZURE_SEARCH_HYBRID_INDEX_NAME = os.getenv("AZURE_SEARCH_HYBRID_INDEX_NAME", "aegis-doc-chunks-hybrid")
    AZURE_SEARCH_ENABLE_SEMANTIC = _as_bool(os.getenv("AZURE_SEARCH_ENABLE_SEMANTIC"), False)

    RETRIEVAL_STRATEGY = os.getenv("RETRIEVAL_STRATEGY", "keyword").strip().lower()
    EMBEDDING_VECTOR_DIMENSIONS = int(os.getenv("EMBEDDING_VECTOR_DIMENSIONS", "1536"))

    AUTH_REQUIRE_SIGN_IN = _as_bool(os.getenv("AUTH_REQUIRE_SIGN_IN"), True)

    SECURITY_ADMIN_USERS = {
        item.strip().lower()
        for item in os.getenv("SECURITY_ADMIN_USERS", "").split(",")
        if item.strip()
    }
    INTERNAL_USERS = {
        item.strip().lower()
        for item in os.getenv("INTERNAL_USERS", "").split(",")
        if item.strip()
    }

    CLIENT_PRINCIPAL_HEADER = "X-MS-CLIENT-PRINCIPAL"
    CLIENT_PRINCIPAL_ID_HEADER = "X-MS-CLIENT-PRINCIPAL-ID"
    CLIENT_PRINCIPAL_NAME_HEADER = "X-MS-CLIENT-PRINCIPAL-NAME"
    CLIENT_PRINCIPAL_IDP_HEADER = "X-MS-CLIENT-PRINCIPAL-IDP"
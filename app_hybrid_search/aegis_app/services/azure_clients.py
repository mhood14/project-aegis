from __future__ import annotations

from functools import lru_cache

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.storage.blob import BlobServiceClient
from flask import current_app
from openai import AzureOpenAI


@lru_cache(maxsize=1)
def get_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient(
        account_url=current_app.config["STORAGE_ACCOUNT_URL"],
        credential=get_credential(),
    )


def get_search_index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=current_app.config["AZURE_SEARCH_ENDPOINT"],
        credential=get_credential(),
    )


def get_search_client(index_name: str | None = None) -> SearchClient:
    return SearchClient(
        endpoint=current_app.config["AZURE_SEARCH_ENDPOINT"],
        index_name=index_name or current_app.config["AZURE_SEARCH_INDEX_NAME"],
        credential=get_credential(),
    )


def get_azure_openai_token_provider():
    return get_bearer_token_provider(
        get_credential(),
        "https://cognitiveservices.azure.com/.default",
    )


def get_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=current_app.config["AZURE_OPENAI_ENDPOINT"],
        api_version=current_app.config["AZURE_OPENAI_API_VERSION"],
        azure_ad_token_provider=get_azure_openai_token_provider(),
    )
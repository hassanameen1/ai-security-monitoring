"""Create the Azure AI Search index and upload knowledge base docs.

Re-runnable: drops and recreates the index on every run.
"""

import hashlib
import os
import sys
from pathlib import Path

import yaml
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
KEY = os.environ["AZURE_SEARCH_ADMIN_KEY"]
INDEX_NAME = os.environ["AZURE_SEARCH_INDEX"]
KB_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_base"

credential = AzureKeyCredential(KEY)


def build_index() -> SearchIndex:
    fields = [
        SimpleField(name="doc_id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="classification", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchField(
            name="authorized_groups",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            filterable=True,
        ),
    ]
    return SearchIndex(name=INDEX_NAME, fields=fields)


def parse_doc(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path.name} missing frontmatter")
    _, frontmatter, body = raw.split("---", 2)
    meta = yaml.safe_load(frontmatter)
    return {
        "doc_id": meta["doc_id"],
        "title": meta["title"],
        "content": body.strip(),
        "classification": meta["classification"],
        "authorized_groups": meta["authorized_groups"],
    }


def main() -> int:
    index_client = SearchIndexClient(endpoint=ENDPOINT, credential=credential)

    if INDEX_NAME in [i.name for i in index_client.list_indexes()]:
        print(f"deleting existing index '{INDEX_NAME}'")
        index_client.delete_index(INDEX_NAME)

    print(f"creating index '{INDEX_NAME}'")
    index_client.create_index(build_index())

    docs = [parse_doc(p) for p in sorted(KB_DIR.glob("*.md"))]
    print(f"uploading {len(docs)} documents")

    search_client = SearchClient(endpoint=ENDPOINT, index_name=INDEX_NAME, credential=credential)
    result = search_client.upload_documents(documents=docs)
    failed = [r for r in result if not r.succeeded]
    if failed:
        print(f"FAILED: {failed}", file=sys.stderr)
        return 1

    for doc in docs:
        print(f"  ✓ {doc['doc_id']}  {doc['classification']:14s}  groups={doc['authorized_groups']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

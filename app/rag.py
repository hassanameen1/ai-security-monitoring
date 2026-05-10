import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"]),
)


def retrieve(query: str, groups: list[str] | None = None, top: int = 3) -> list[dict]:
    """Return top-k matching docs. If groups is provided, filter by authorized_groups."""
    kwargs = {"search_text": query, "top": top, "select": ["doc_id", "title", "content", "classification"]}
    if groups:
        quoted = ",".join(f"'{g}'" for g in groups)
        kwargs["filter"] = f"authorized_groups/any(g: search.in(g, {quoted}))"
    return [dict(r) for r in _client.search(**kwargs)]


def format_context(docs: list[dict]) -> str:
    if not docs:
        return "No relevant documents found."
    blocks = [f"[doc:{d['doc_id']} | {d['title']} | classification:{d['classification']}]\n{d['content']}" for d in docs]
    return "\n\n---\n\n".join(blocks)

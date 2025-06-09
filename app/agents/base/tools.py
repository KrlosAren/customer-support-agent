from typing import Callable
from langchain_core.tools import tool


def create_lookup_policy_tool(retriever) -> list[Callable]:

    @tool
    def lookup_policy(self, query: str) -> str:
        """Consult the company policies to check whether certain options are permitted.
        Use this before making any flight changes performing other 'write' events."""
        docs = retriever.query(query, k=2)
        return "\n\n".join([doc["page_content"] for doc in docs])

    return [lookup_policy]

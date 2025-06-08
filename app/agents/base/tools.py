from langchain_core.tools import tool


class LookupPolicyTool:
    """Create a tool to lookup company policies."""

    def __init__(self, retriever):
        self.retriever = retriever

    @tool
    def lookup_policy(self, query: str) -> str:
        """Consult the company policies to check whether certain options are permitted.
        Use this before making any flight changes performing other 'write' events."""
        docs = self.retriever.query(query, k=2)
        return "\n\n".join([doc["page_content"] for doc in docs])

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool


_search = DuckDuckGoSearchResults(output_format="list", num_results=5)


@tool
def search_tool(query: str) -> str:
    """Search the web for information. Returns results with titles, snippets, and URLs."""
    results = _search.run(query)
    if not results:
        return "No results found."
    
    formatted_results = []
    for item in results:
        title = item.get("title", "No title")
        snippet = item.get("snippet", "No description")
        link = item.get("link", "No link")
        formatted_results.append(f"Title: {title}\nSnippet: {snippet}\nURL: {link}\n")
    
    return "\n".join(formatted_results)

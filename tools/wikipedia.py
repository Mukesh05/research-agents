from langchain_core.tools import tool
import wikipedia


@tool
def wiki_tool(query: str) -> str:
    """Search Wikipedia for information. Returns summary with authentic Wikipedia URL."""
    try:
        page = wikipedia.page(query, auto_suggest=True)
        summary = wikipedia.summary(query, sentences=3)
        return f"{summary}\n\nSource URL: {page.url}"
    except wikipedia.DisambiguationError as e:
        # Try the first suggestion
        try:
            page = wikipedia.page(e.options[0])
            summary = wikipedia.summary(e.options[0], sentences=3)
            return f"{summary}\n\nSource URL: {page.url}"
        except Exception:
            return f"Multiple matches found: {', '.join(e.options[:5])}"
    except Exception as e:
        return f"Could not find Wikipedia article: {e}"

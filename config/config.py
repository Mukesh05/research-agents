from dotenv import load_dotenv
from pathlib import Path
from langchain_anthropic import ChatAnthropic

# Load environment variables (.env.local takes priority over .env)
# Look for env files in project root
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env.local")
load_dotenv(ROOT_DIR / ".env")

# LLM Configuration
MODELS = {
    "simple": "claude-sonnet-4-20250514",      # Base model for simple queries
    "moderate": "claude-sonnet-4-20250514",    # Same for moderate complexity
    "complex": "claude-opus-4-20250514",       # Opus for complex queries
}

# Complexity indicators
COMPLEX_KEYWORDS = [
    "analyze", "compare", "contrast", "evaluate", "synthesize",
    "research", "in-depth", "comprehensive", "detailed", "explain why",
    "relationship between", "implications", "critique", "assess"
]

SIMPLE_KEYWORDS = [
    "what is", "who is", "when", "where", "define", "list", "name"
]


def assess_complexity(query: str) -> str:
    """Assess the complexity of a user query."""
    query_lower = query.lower()
    word_count = len(query.split())

    # Check for complex indicators
    complex_score = sum(1 for kw in COMPLEX_KEYWORDS if kw in query_lower)
    simple_score = sum(1 for kw in SIMPLE_KEYWORDS if kw in query_lower)

    # Long queries with complex keywords -> complex
    if complex_score >= 2 or (word_count > 30 and complex_score >= 1):
        return "complex"
    # Short queries with simple keywords -> simple
    elif simple_score >= 1 and word_count < 15:
        return "simple"
    else:
        return "moderate"


def get_llm(query: str = None):
    """Returns the configured LLM instance based on query complexity."""
    if query:
        complexity = assess_complexity(query)
        model_name = MODELS[complexity]
        print(f"[Using {complexity} model: {model_name}]")
    else:
        model_name = MODELS["simple"]

    return ChatAnthropic(model=model_name)


def get_viz_llm():
    """Returns the configured LLM instance for visualization agent.
    Always uses Claude Sonnet 4 for consistent visualization decisions."""
    model_name = "claude-sonnet-4-20250514"
    print(f"[Visualization Agent using: {model_name}]")
    return ChatAnthropic(model=model_name)


# Corporate Presentation Configuration
CORPORATE_THEMES = {
    "navy-teal": {
        "primary": "1F4788",
        "secondary": "00A9A5",
        "accent": "93A8AC",
        "highlight": "F7C548",
        "background": "FFFFFF",
        "text": "333333"
    },
    "navy-gold": {
        "primary": "1E2761",
        "secondary": "C5A572",
        "accent": "6E7C8F",
        "highlight": "E8B449",
        "background": "FFFFFF",
        "text": "333333"
    },
    "charcoal-blue": {
        "primary": "2C3E50",
        "secondary": "3498DB",
        "accent": "95A5A6",
        "highlight": "E74C3C",
        "background": "FFFFFF",
        "text": "2C3E50"
    }
}

# Default chart options for pptxgenjs (McKinsey-style)
CHART_DEFAULTS = {
    "showLegend": False,
    "showTitle": True,
    "showValue": True,
    "dataLabelPosition": "bestFit",
    "dataLabelFontSize": 10,
    "titleFontSize": 18,
    "catAxisLabelFontSize": 11,
    "valAxisLabelFontSize": 11,
    "showCatAxisTitle": False,
    "showValAxisTitle": False,
    "valGridLine": {"style": "none"},  # Minimalist: no gridlines
    "catAxisOrientation": "minMax"
}

# Slide dimensions (16:9 widescreen for conferences)
SLIDE_DIMENSIONS = {
    "width": 10,  # inches
    "height": 5.625  # inches (16:9 ratio)
}

# Font hierarchy (corporate style)
FONT_HIERARCHY = {
    "title": {"size": 28, "bold": True, "font": "Arial"},
    "subtitle": {"size": 18, "bold": False, "font": "Arial"},
    "body": {"size": 14, "bold": False, "font": "Arial"},
    "chart_title": {"size": 20, "bold": True, "font": "Arial"},
    "data_label": {"size": 10, "bold": False, "font": "Arial"}
}

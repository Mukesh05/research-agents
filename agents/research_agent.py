from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_agent
import asyncio
from typing import Dict, Any

from config import get_llm
from models import ResearchResponse, ResearchRequest
from tools import search_tool, wiki_tool, save_tool, pptx_tool, visualization_tool


def get_parser():
    """Returns the Pydantic output parser for research responses."""
    return PydanticOutputParser(pydantic_object=ResearchResponse)


def get_system_prompt(parser: PydanticOutputParser) -> str:
    """Generate the system prompt with format instructions."""
    format_instructions = parser.get_format_instructions()
    return f"""
You are a research assistant that will help generate a research paper.
Answer the user query and use necessary tools.

CRITICAL: After completing your research, you MUST save the results using export formats:
1. PDF format using save_to_pdf - Call this tool with your research data, a descriptive title, and auto-generated filename
2. PPTX format using save_to_pptx - Call this tool with your research data, a descriptive title, and auto-generated filename

OPTIONAL: For conference-ready, data-driven presentations:
3. If your research contains NUMERICAL DATA, TRENDS, COMPARISONS, or RANKINGS that would benefit from visual representation, 
   use visualize_data tool to create a professional McKinsey-style presentation with charts.

WHEN TO USE VISUALIZE_DATA:
✅ Numerical comparisons (market share, survey results, performance metrics)
✅ Time-based trends (growth rates, historical data, projections)
✅ Proportional data (budget allocation, demographic splits, composition)
✅ Rankings or ordered data (top companies, performance tiers)
✅ Statistical findings with multiple data points

❌ Skip visualization for pure text research (historical narratives, concept explanations, qualitative analyses)

VISUALIZATION DATA FORMAT:
Structure data as McKinsey-style slides with JSON format:
- presentation_title: Descriptive title for the deck
- theme: Choose based on topic (navy-teal for tech/general, navy-gold for finance, charcoal-blue for modern/versatile)
- executive_summary: Array of 3-5 numbered key findings (start with most important insight)
- charts: Array of chart objects with:
  * chart_type: "bar" (comparisons/rankings), "line" (trends over time), "pie" (composition, max 5 parts), "doughnut" (composition), "area" (trends with magnitude)
  * title: INSIGHT-BASED (e.g., "AWS leads with 32% market share" NOT "Market Share 2024")
  * data: Array of numbers
  * labels: Array of labels matching data
  * layout: "full-chart" (default) or "chart-insight" (includes text box for key takeaway)
  * insight_text: Required if layout is "chart-insight" - explain why the data matters
- section_dividers: Optional array of section titles to organize multiple charts

EXAMPLE VISUALIZATION CALL:
{{
  "presentation_title": "Cloud Computing Market Analysis 2024-2026",
  "theme": "navy-teal",
  "executive_summary": [
    "Cloud adoption accelerated 45% post-pandemic",
    "AWS maintains 32% market share lead over competitors",
    "Hybrid cloud deployments grew 60% year-over-year"
  ],
  "section_dividers": ["Market Share Analysis", "Growth Trends"],
  "charts": [
    {{
      "chart_type": "bar",
      "title": "AWS leads with 32% market share in 2024",
      "data": [32, 25, 20, 23],
      "labels": ["AWS", "Azure", "Google Cloud", "Others"],
      "layout": "full-chart"
    }},
    {{
      "chart_type": "line",
      "title": "Cloud spending projected to reach $500B by 2026",
      "data": [250, 330, 410, 500],
      "labels": ["2023", "2024", "2025", "2026"],
      "layout": "chart-insight",
      "insight_text": "Annual growth rate of 25% driven by AI/ML workloads and digital transformation initiatives"
    }}
  ]
}}

Always invoke both save_to_pdf and save_to_pptx tools with the complete research findings.
If data warrants visualization, also call visualize_data with structured chart specifications.
The data parameter for PDF/PPTX should contain your full research with markdown formatting (headers, bullets, tables, etc.).

Wrap the output in this format and provide no other text
{format_instructions}
"""


def create_research_agent(query: str = None):
    """Creates and returns the research agent with all tools configured."""
    llm = get_llm(query)
    parser = get_parser()
    tools = [search_tool, wiki_tool, save_tool, pptx_tool, visualization_tool]
    system_prompt = get_system_prompt(parser)

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    return agent, parser


def run_agent(agent, parser, query: str):
    """Run the agent with the given query and return parsed response."""
    raw_response = agent.invoke({"messages": [("user", query)]})

    try:
        final_message = raw_response["messages"][-1].content
        structured_response = parser.parse(final_message)
        return structured_response
    except Exception as e:
        print("Error parsing response", e, "Raw Response - ", raw_response)
        return None


async def run_research_async(request: ResearchRequest) -> Dict[str, Any]:
    """
    Run research agent asynchronously with API request parameters.

    Args:
        request: ResearchRequest with query and preferences

    Returns:
        Dictionary with:
            - response: ResearchResponse object
            - pdf_path: Path to generated PDF (if requested)
            - pptx_path: Path to generated PPTX (if requested)
            - visualization_path: Path to visualization PPTX (if created)
    """
    # Run the synchronous agent in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()

    def _run_sync():
        # Create agent with model selected based on query complexity
        agent, parser = create_research_agent(request.query)
        response = run_agent(agent, parser, request.query)
        return response

    # Execute in thread pool
    response = await loop.run_in_executor(None, _run_sync)

    if not response:
        raise Exception("Research agent failed to generate response")

    # Extract file paths from the response
    # Note: The tools now save files and return paths in their responses
    # We need to track which files were created
    result = {
        "response": response,
        "pdf_path": None,
        "pptx_path": None,
        "visualization_path": None
    }

    # The agent automatically calls save_tool and pptx_tool
    # File paths are generated based on the topic
    # We'll need to infer the paths or modify tools to return them
    # For now, we'll look in the output directory for recent files
    import os
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output"
    if output_dir.exists():
        # Get the most recent files (crude but functional for MVP)
        pdf_files = sorted(output_dir.glob("*.pdf"),
                           key=os.path.getmtime, reverse=True)
        pptx_files = sorted(output_dir.glob("*.pptx"),
                            key=os.path.getmtime, reverse=True)

        if "pdf" in request.output_formats and pdf_files:
            result["pdf_path"] = str(pdf_files[0])

        if "pptx" in request.output_formats and pptx_files:
            # First pptx might be visualization, second is regular
            if len(pptx_files) >= 2 and request.include_visualization:
                result["visualization_path"] = str(pptx_files[0])
                result["pptx_path"] = str(pptx_files[1])
            elif pptx_files:
                result["pptx_path"] = str(pptx_files[0])

    return result

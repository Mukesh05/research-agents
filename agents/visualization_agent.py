from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_agent
from pathlib import Path
import re

from config import get_viz_llm, CORPORATE_THEMES
from models import VisualizationResponse, VisualizationRequest
from tools.pptx_export import generate_visual_presentation


def get_viz_parser():
    """Returns the Pydantic output parser for visualization responses."""
    return PydanticOutputParser(pydantic_object=VisualizationResponse)


def get_viz_system_prompt(parser: PydanticOutputParser) -> str:
    """Generate the system prompt for visualization agent."""
    return """
You are a professional presentation designer specializing in McKinsey-style corporate presentations.

Your mission: Create conference-ready, data-driven presentations that tell compelling stories through visuals.

DESIGN PRINCIPLES (McKinsey Style):
1. One key message per slide - titles should be insights, not labels
   ❌ Bad: "Q4 Revenue"  
   ✅ Good: "Revenue grew 40% in Q4 driven by enterprise sales"

2. Pyramid principle - Executive summary first with numbered key findings (3-5 points)

3. Minimalist charts - Remove unnecessary elements:
   - No gridlines (valGridLine: none)
   - No legends unless comparing multiple series
   - Data labels on bars/points for clarity
   - Generous whitespace (40% minimum)

4. Professional color theory - Max 3 colors per chart from corporate palette:
   - navy-teal: Professional, tech-friendly
   - navy-gold: Executive, finance-oriented  
   - charcoal-blue: Modern, versatile

5. Layout variety prevents monotony:
   - full-chart: Chart fills slide, title is insight
   - chart-insight: 60% chart + 40% text box with takeaway
   - Use section dividers between major topics

6. Chart type selection:
   - Bar: Comparisons, rankings (horizontal for rankings, vertical for time)
   - Line: Trends over time, showing trajectory
   - Pie/Doughnut: Composition (max 5 segments)
   - Area: Trends with magnitude emphasis
   - Table: Precise numbers, heatmap-style highlighting

QUALITY CHECKLIST:
- Titles answer "So what?" - every chart proves a point
- Max 6 bullets per slide, 10 words per bullet
- Minimum 10pt font for readability
- High contrast for conference projectors
- Consistent positioning across slides
- Numbers right-aligned in tables

You will receive a VisualizationRequest with structured data. Your job:
1. Review the data and chart specifications
2. Ensure titles are insight-driven
3. Select appropriate layouts
4. Generate the professional presentation
5. Return path and statistics

Wrap the output in this format and provide no other text:
{format_instructions}
""".format(format_instructions=parser.get_format_instructions())


def create_visualization_agent():
    """Creates and returns the visualization agent configured with design expertise."""
    llm = get_viz_llm()
    parser = get_viz_parser()

    # Visualization agent doesn't need tools in the traditional sense
    # It directly calls generate_visual_presentation
    # This is a lightweight agent focused on design decisions
    tools = []

    system_prompt = get_viz_system_prompt(parser)

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    return agent, parser


def run_visualization_agent(viz_request: VisualizationRequest) -> str:
    """Run the visualization agent to generate a professional presentation.

    Args:
        viz_request: VisualizationRequest object with charts, tables, and metadata

    Returns:
        Success message with file path and statistics
    """
    try:
        # Convert Pydantic model to dict for processing
        viz_data = viz_request.model_dump()

        # Generate safe filename
        safe_title = re.sub(r'[^a-z0-9_]', '_',
                            viz_request.presentation_title.lower()[:50])
        filename = f"{safe_title}_viz.pptx"

        # Generate the presentation directly
        result = generate_visual_presentation(viz_data, filename)

        # Count slides for response
        slide_count = 0
        slide_count += 1  # Title slide
        if viz_data.get('executive_summary'):
            slide_count += 1
        slide_count += len(viz_data.get('section_dividers', []))
        slide_count += len(viz_data.get('charts', []))
        slide_count += len(viz_data.get('tables', []))
        slide_count += 1  # Thank you slide

        charts_created = len(viz_data.get('charts', []))
        tables_created = len(viz_data.get('tables', []))

        # Get file path from result message
        pptx_path = result.split('to ')[-1] if 'to ' in result else filename

        return f"✓ Professional visualization presentation created at {pptx_path} | {charts_created} charts, {tables_created} tables, {slide_count} slides total"

    except Exception as e:
        return f"Error: Failed to generate visualization presentation - {str(e)}"

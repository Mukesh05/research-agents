from langchain_core.tools import tool
import json
from pathlib import Path


@tool
def visualize_data(data: str, presentation_style: str = "corporate-conference") -> str:
    """Creates a professional McKinsey-style presentation with charts and visualizations.

    Use this tool when research includes numerical data, trends, comparisons, or rankings that 
    would benefit from visual representation. This generates conference-ready presentations 
    with data-driven storytelling.

    Args:
        data: JSON string containing VisualizationRequest with:
            - presentation_title: Title for the presentation
            - theme: Color theme (navy-teal, navy-gold, charcoal-blue)
            - charts: List of chart specifications with:
                - chart_type: bar (comparisons/rankings), line (trends/time), pie (composition), 
                              doughnut (composition), area (trends with magnitude)
                - title: Insight-based title (e.g., "Revenue grew 40% in Q4" not just "Q4 Revenue")
                - data: List of numerical values
                - labels: List of labels for data points
                - layout: full-chart (default) or chart-insight (chart + text box)
                - insight_text: Optional key takeaway for chart-insight layout
            - tables: Optional list of data tables
            - executive_summary: Optional list of 3-5 numbered key findings
            - section_dividers: Optional list of section titles
        presentation_style: Style preset (default: corporate-conference)

    Returns:
        Success message with path to generated PPTX file

    Example:
        {
            "presentation_title": "Cloud Computing Market Analysis 2024-2026",
            "theme": "navy-teal",
            "executive_summary": [
                "Cloud adoption accelerated 45% post-pandemic",
                "AWS maintains 32% market share lead",
                "Hybrid cloud deployments grew 60% YoY"
            ],
            "charts": [
                {
                    "chart_type": "bar",
                    "title": "AWS leads with 32% market share in 2024",
                    "data": [32, 25, 20, 23],
                    "labels": ["AWS", "Azure", "Google Cloud", "Others"],
                    "layout": "full-chart"
                },
                {
                    "chart_type": "line",
                    "title": "Cloud spending projected to reach $500B by 2026",
                    "data": [250, 330, 410, 500],
                    "labels": ["2023", "2024", "2025", "2026"],
                    "layout": "chart-insight",
                    "insight_text": "Annual growth rate of 25% driven by AI/ML workloads and digital transformation initiatives"
                }
            ]
        }
    """
    try:
        # Import here to avoid circular dependencies
        from agents.visualization_agent import run_visualization_agent
        from models.schemas import VisualizationRequest

        # Parse JSON string to dict
        viz_data = json.loads(data)

        # Validate using Pydantic
        viz_request = VisualizationRequest(**viz_data)

        # Run visualization agent
        result = run_visualization_agent(viz_request)

        return result

    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format. {str(e)}"
    except Exception as e:
        return f"Error generating visualization: {str(e)}"


visualization_tool = visualize_data

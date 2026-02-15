from langchain_core.tools import tool
from pathlib import Path
import subprocess
import json
import tempfile
import re

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "output"


@tool
def save_to_pptx(data: str, title: str, filename: str = None) -> str:
    """Converts research data to a professional PowerPoint presentation (.pptx) with 
    visually engaging slides following design best practices."""

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Generate filename if not provided
    if not filename:
        safe_title = re.sub(r'[^a-z0-9_]', '_', title.lower()[:50])
        filename = f"{safe_title}_presentation.pptx"

    if not title or not title.strip():
        raise ValueError("Title is required for presentation")

    filepath = OUTPUT_DIR / filename

    # Parse content into structured sections
    sections = _parse_content_to_sections(data)

    # Generate JavaScript code for pptxgenjs with full output path
    js_code = _generate_pptxgenjs_code(title, sections, str(filepath))

    # Write JS file to project root (where node_modules is) instead of system temp
    project_root = OUTPUT_DIR.parent
    js_filepath = project_root / f"temp_pptx_{Path(filename).stem}.js"

    try:
        # Write the JavaScript code
        js_filepath.write_text(js_code, encoding='utf-8')

        # Run node from project root (where node_modules is)
        result = subprocess.run(
            ['node', js_filepath.name],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=60
        )

        if result.returncode != 0:
            raise Exception(f"pptxgenjs execution failed: {result.stderr}")

        # Clean up temp file
        js_filepath.unlink()

        return f"Professional presentation successfully saved to {filepath}"

    except FileNotFoundError:
        # Clean up on error
        if js_filepath.exists():
            js_filepath.unlink()
        return "Error: Node.js is not installed. Please install Node.js and pptxgenjs: npm install pptxgenjs"
    except Exception as e:
        # Clean up on error
        if js_filepath.exists():
            js_filepath.unlink()
        return f"Error generating presentation: {str(e)}"


def _parse_content_to_sections(data: str) -> list:
    """Parse markdown-style content into presentation sections."""
    sections = []
    current_section = None
    lines = data.split('\n')

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('# '):
            if current_section:
                sections.append(current_section)
            current_section = {
                'title': stripped[2:],
                'level': 1,
                'content': []
            }
        elif stripped.startswith('## '):
            if current_section:
                sections.append(current_section)
            current_section = {
                'title': stripped[3:],
                'level': 2,
                'content': []
            }
        elif stripped.startswith('### '):
            if current_section:
                sections.append(current_section)
            current_section = {
                'title': stripped[4:],
                'level': 3,
                'content': []
            }
        elif current_section and stripped:
            current_section['content'].append(stripped)

    if current_section:
        sections.append(current_section)

    return sections


def _generate_pptxgenjs_code(title: str, sections: list, output_path: str) -> str:
    """Generate JavaScript code using pptxgenjs library.

    Args:
        title: Presentation title
        sections: List of content sections
        output_path: Full absolute path where the PPTX file should be saved
    """
    # Choose a professional color palette (Midnight Executive from skill guide)
    primary_color = "1E2761"    # Navy
    secondary_color = "CADCFC"  # Ice blue
    accent_color = "FFFFFF"     # White
    text_color = "333333"       # Dark gray

    js_code = f'''
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Research Agent';
pres.title = {json.dumps(title)};

// Title slide (dark background)
let slide1 = pres.addSlide();
slide1.background = {{ color: "{primary_color}" }};
slide1.addText({json.dumps(title)}, {{
    x: 0.5, y: 2, w: 9, h: 2,
    fontSize: 44, fontFace: "Arial", bold: true,
    color: "{accent_color}", align: "center", valign: "middle"
}});
slide1.addText("Research Report", {{
    x: 0.5, y: 3.8, w: 9, h: 0.5,
    fontSize: 18, fontFace: "Arial",
    color: "{secondary_color}", align: "center"
}});

const now = new Date();
const dateStr = now.toLocaleDateString('en-US', {{ year: 'numeric', month: 'long', day: 'numeric' }});
slide1.addText(dateStr, {{
    x: 0.5, y: 4.5, w: 9, h: 0.4,
    fontSize: 14, fontFace: "Arial",
    color: "{secondary_color}", align: "center"
}});

'''

    # Add content sections to sections
    for idx, section in enumerate(sections[:10]):  # Limit to 10 content slides
        title_text = section['title']
        content_items = section['content'][:6]  # Max 6 bullets per slide

        js_code += f'''
// Slide {idx + 2}: {title_text[:30]}
let slide{idx + 2} = pres.addSlide();
slide{idx + 2}.background = {{ color: "{accent_color}" }};

// Section number indicator
slide{idx + 2}.addShape(pres.shapes.RECTANGLE, {{
    x: 0.5, y: 0.5, w: 0.8, h: 0.5,
    fill: {{ color: "{primary_color}" }},
    line: {{ type: "none" }}
}});
slide{idx + 2}.addText("{idx + 1}", {{
    x: 0.5, y: 0.5, w: 0.8, h: 0.5,
    fontSize: 24, fontFace: "Arial", bold: true,
    color: "{accent_color}", align: "center", valign: "middle"
}});

// Title
slide{idx + 2}.addText({json.dumps(title_text)}, {{
    x: 1.5, y: 0.5, w: 8, h: 0.5,
    fontSize: 28, fontFace: "Arial", bold: true,
    color: "{primary_color}", align: "left", valign: "middle",
    margin: 0
}});

// Horizontal line under title
slide{idx + 2}.addShape(pres.shapes.LINE, {{
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: {{ color: "{secondary_color}", width: 2 }}
}});

'''

        # Add bullet points
        if content_items:
            bullets_js = []
            for content in content_items:
                # Clean content (remove markdown, bullets, etc.)
                clean_content = content.lstrip('- *•').strip()
                if clean_content:
                    bullets_js.append(
                        f'{{ text: {json.dumps(clean_content)}, options: {{ bullet: true }} }}')

            if bullets_js:
                bullets_array = ',\n    '.join(bullets_js)

                js_code += f'''
slide{idx + 2}.addText([
    {bullets_array}
], {{
    x: 1, y: 1.8, w: 8.5, h: 3.2,
    fontSize: 16, fontFace: "Arial",
    color: "{text_color}", bullet: {{ color: "{primary_color}" }}
}});
'''

    # Conclusion slide
    js_code += f'''
// Conclusion slide (dark background)
let slideEnd = pres.addSlide();
slideEnd.background = {{ color: "{primary_color}" }};
slideEnd.addText("Thank You", {{
    x: 0.5, y: 2.3, w: 9, h: 1,
    fontSize: 44, fontFace: "Arial", bold: true,
    color: "{accent_color}", align: "center", valign: "middle"
}});
slideEnd.addText("Research Agent", {{
    x: 0.5, y: 3.5, w: 9, h: 0.5,
    fontSize: 18, fontFace: "Arial",
    color: "{secondary_color}", align: "center"
}});

// Save presentation using absolute path
pres.writeFile({{ fileName: {json.dumps(output_path)} }}).then(() => {{
    console.log("Presentation created successfully");
}}).catch(err => {{
    console.error("Error:", err);
    process.exit(1);
}});
'''

    return js_code


def generate_visual_presentation(viz_request: dict, filename: str = None) -> str:
    """Generate a professional McKinsey-style presentation with charts and visualizations.

    Args:
        viz_request: Dictionary containing VisualizationRequest data with charts, tables, etc.
        filename: Optional filename for the presentation

    Returns:
        Success message with file path
    """
    from config import CORPORATE_THEMES, CHART_DEFAULTS

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Generate filename if not provided
    if not filename:
        safe_title = re.sub(r'[^a-z0-9_]', '_',
                            viz_request['presentation_title'].lower()[:50])
        filename = f"{safe_title}_viz.pptx"

    filepath = OUTPUT_DIR / filename

    # Get theme colors
    theme = viz_request.get('theme', 'navy-teal')
    colors = CORPORATE_THEMES.get(theme, CORPORATE_THEMES['navy-teal'])

    # Generate JavaScript code for pptxgenjs with charts
    js_code = _generate_viz_pptxgenjs_code(viz_request, colors, str(filepath))

    # Write JS file to project root
    project_root = OUTPUT_DIR.parent
    js_filepath = project_root / f"temp_viz_{Path(filename).stem}.js"

    try:
        # Write the JavaScript code
        js_filepath.write_text(js_code, encoding='utf-8')

        # Run node from project root
        result = subprocess.run(
            ['node', js_filepath.name],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=60
        )

        if result.returncode != 0:
            raise Exception(f"pptxgenjs execution failed: {result.stderr}")

        # Clean up temp file
        js_filepath.unlink()

        charts_count = len(viz_request.get('charts', []))
        tables_count = len(viz_request.get('tables', []))

        return f"Professional visualization presentation with {charts_count} charts and {tables_count} tables saved to {filepath}"

    except FileNotFoundError:
        if js_filepath.exists():
            js_filepath.unlink()
        return "Error: Node.js is not installed. Please install Node.js and pptxgenjs: npm install pptxgenjs"
    except Exception as e:
        if js_filepath.exists():
            js_filepath.unlink()
        return f"Error generating visualization presentation: {str(e)}"


def _generate_viz_pptxgenjs_code(viz_request: dict, colors: dict, output_path: str) -> str:
    """Generate JavaScript code for visualization presentation using pptxgenjs.

    Implements McKinsey-style corporate presentation design with:
    - Data-driven storytelling (one insight per slide)
    - Professional charts with minimal styling
    - Executive summary first
    - Generous whitespace
    """
    from config import CHART_DEFAULTS

    title = viz_request['presentation_title']
    charts = viz_request.get('charts', [])
    tables = viz_request.get('tables', [])
    exec_summary = viz_request.get('executive_summary', [])
    section_dividers = viz_request.get('section_dividers', [])

    js_code = f'''
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Visualization Agent';
pres.title = {json.dumps(title)};

// Corporate theme colors
const colors = {{
    primary: "{colors['primary']}",
    secondary: "{colors['secondary']}",
    accent: "{colors['accent']}",
    highlight: "{colors['highlight']}",
    background: "{colors['background']}",
    text: "{colors['text']}"
}};

// Title slide (professional corporate style)
let slide1 = pres.addSlide();
slide1.background = {{ color: colors.primary }};
slide1.addText({json.dumps(title)}, {{
    x: 0.5, y: 1.8, w: 9, h: 1.5,
    fontSize: 36, fontFace: "Arial", bold: true,
    color: "FFFFFF", align: "center", valign: "middle"
}});

const now = new Date();
const dateStr = now.toLocaleDateString('en-US', {{ year: 'numeric', month: 'long', day: 'numeric' }});
slide1.addText(dateStr, {{
    x: 0.5, y: 3.5, w: 9, h: 0.4,
    fontSize: 14, fontFace: "Arial",
    color: colors.secondary, align: "center"
}});

// Slide numbers helper
let slideNum = 2;

'''

    # Executive Summary slide
    if exec_summary:
        js_code += '''
// Executive Summary
let slideExec = pres.addSlide();
slideExec.background = { color: colors.background };
slideExec.addText("Executive Summary", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 28, fontFace: "Arial", bold: true,
    color: colors.primary, align: "left"
});

// Horizontal line
slideExec.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.2, w: 9, h: 0,
    line: { color: colors.accent, width: 2 }
});

'''
        # Add numbered key findings
        for idx, finding in enumerate(exec_summary[:5]):
            y_pos = 1.8 + (idx * 0.6)
            js_code += f'''
slideExec.addText("{idx + 1}. {finding}", {{
    x: 1.0, y: {y_pos}, w: 8.5, h: 0.5,
    fontSize: 16, fontFace: "Arial",
    color: colors.text, align: "left"
}});
'''
        js_code += '\nslideNum++;\n\n'

    # Section dividers and charts
    divider_idx = 0
    for chart_idx, chart in enumerate(charts):
        # Add section divider if needed
        if section_dividers and divider_idx < len(section_dividers):
            section_title = section_dividers[divider_idx]
            js_code += f'''
// Section Divider
let slideDiv{divider_idx} = pres.addSlide();
slideDiv{divider_idx}.background = {{ color: colors.primary }};
slideDiv{divider_idx}.addText({json.dumps(section_title)}, {{
    x: 0.5, y: 2.3, w: 9, h: 0.8,
    fontSize: 32, fontFace: "Arial", bold: true,
    color: "FFFFFF", align: "center", valign: "middle"
}});
slideNum++;

'''
            divider_idx += 1

        # Generate chart slide
        chart_code = _generate_chart_slide(chart, chart_idx, colors)
        js_code += chart_code

    # Add table slides
    for table_idx, table in enumerate(tables):
        table_code = _generate_table_slide(table, table_idx, colors)
        js_code += table_code

    # Closing slide
    js_code += '''
// Thank You slide
let slideEnd = pres.addSlide();
slideEnd.background = { color: colors.primary };
slideEnd.addText("Thank You", {
    x: 0.5, y: 2.3, w: 9, h: 1,
    fontSize: 44, fontFace: "Arial", bold: true,
    color: "FFFFFF", align: "center", valign: "middle"
});

'''

    js_code += f'''
// Save presentation
pres.writeFile({{ fileName: {json.dumps(output_path)} }}).then(() => {{
    console.log("Visualization presentation created successfully");
}}).catch(err => {{
    console.error("Error:", err);
    process.exit(1);
}});
'''

    return js_code


def _generate_chart_slide(chart: dict, idx: int, colors: dict) -> str:
    """Generate JavaScript code for a single chart slide."""
    from config import CHART_DEFAULTS

    chart_type = chart['chart_type'].upper()
    title = chart['title']
    data = chart['data']
    labels = chart['labels']
    layout = chart.get('layout', 'full-chart')
    insight_text = chart.get('insight_text', '')
    show_legend = chart.get('show_legend', False)
    show_data_labels = chart.get('show_data_labels', True)

    # Custom colors or default corporate palette
    if chart.get('colors'):
        chart_colors = chart['colors']
    else:
        chart_colors = [colors['primary'], colors['secondary'],
                        colors['accent'], colors['highlight']]

    # Convert chart type to pptxgenjs constant
    pptx_chart_type = {
        'BAR': 'bar',
        'LINE': 'line',
        'PIE': 'pie',
        'DOUGHNUT': 'doughnut',
        'AREA': 'area'
    }.get(chart_type, 'bar')

    js_code = f'''
// Chart Slide {idx + 1}: {title[:40]}
let slideChart{idx} = pres.addSlide();
slideChart{idx}.background = {{ color: colors.background }};

// Title (insight-based)
slideChart{idx}.addText({json.dumps(title)}, {{
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Arial", bold: true,
    color: colors.primary, align: "left"
}});

'''

    # Prepare chart data for pptxgenjs
    js_code += f'''
// Chart data
const chartData{idx} = [
    {{
        name: "Data",
        labels: {json.dumps(labels)},
        values: {json.dumps(data)}
    }}
];

'''

    # Chart positioning based on layout
    if layout == 'chart-insight' and insight_text:
        # 60% chart, 40% text
        chart_x, chart_y, chart_w, chart_h = 0.5, 1.3, 5.5, 3.5
        text_x, text_y, text_w, text_h = 6.5, 1.5, 3, 3

        js_code += f'''
// Chart (60% of slide)
slideChart{idx}.addChart(pres.ChartType.{pptx_chart_type}, chartData{idx}, {{
    x: {chart_x}, y: {chart_y}, w: {chart_w}, h: {chart_h},
    chartColors: {json.dumps(chart_colors)},
    showLegend: {str(show_legend).lower()},
    showTitle: false,
    showValue: {str(show_data_labels).lower()},
    valGridLine: {{ style: "none" }},
    dataLabelFontSize: 10,
    catAxisLabelFontSize: 11,
    valAxisLabelFontSize: 11
}});

// Insight box
slideChart{idx}.addShape(pres.shapes.RECTANGLE, {{
    x: {text_x}, y: {text_y}, w: {text_w}, h: {text_h},
    fill: {{ color: colors.accent, transparency: 20 }},
    line: {{ color: colors.primary, width: 1 }}
}});

slideChart{idx}.addText({json.dumps(insight_text)}, {{
    x: {text_x + 0.2}, y: {text_y + 0.3}, w: {text_w - 0.4}, h: {text_h - 0.6},
    fontSize: 14, fontFace: "Arial",
    color: colors.text, align: "left", valign: "top"
}});
'''
    else:
        # Full chart layout
        chart_x, chart_y, chart_w, chart_h = 0.8, 1.3, 8.4, 3.8

        js_code += f'''
// Full chart
slideChart{idx}.addChart(pres.ChartType.{pptx_chart_type}, chartData{idx}, {{
    x: {chart_x}, y: {chart_y}, w: {chart_w}, h: {chart_h},
    chartColors: {json.dumps(chart_colors)},
    showLegend: {str(show_legend).lower()},
    showTitle: false,
    showValue: {str(show_data_labels).lower()},
    valGridLine: {{ style: "none" }},
    dataLabelFontSize: 11,
    catAxisLabelFontSize: 12,
    valAxisLabelFontSize: 12,
    dataLabelPosition: "bestFit"
}});
'''

    js_code += '\nslideNum++;\n\n'
    return js_code


def _generate_table_slide(table: dict, idx: int, colors: dict) -> str:
    """Generate JavaScript code for a data table slide."""
    title = table['title']
    headers = table['headers']
    rows = table['rows']
    highlight_rows = table.get('highlight_rows', [])

    # Prepare table data for pptxgenjs
    table_data = []

    # Header row
    header_cells = []
    for header in headers:
        header_cells.append({
            'text': str(header),
            'options': {
                'bold': True,
                'fontSize': 12,
                'color': 'FFFFFF',
                'fill': colors['primary'],
                'align': 'center'
            }
        })
    table_data.append(header_cells)

    # Data rows
    for row_idx, row in enumerate(rows):
        row_cells = []
        is_highlighted = row_idx in highlight_rows

        for cell in row:
            cell_options = {
                'fontSize': 11,
                'color': colors['text'],
                'align': 'center'
            }

            if is_highlighted:
                cell_options['fill'] = colors['highlight']
                cell_options['transparency'] = 30

            row_cells.append({
                'text': str(cell),
                'options': cell_options
            })

        table_data.append(row_cells)

    js_code = f'''
// Table Slide {idx + 1}: {title[:40]}
let slideTable{idx} = pres.addSlide();
slideTable{idx}.background = {{ color: colors.background }};

slideTable{idx}.addText({json.dumps(title)}, {{
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Arial", bold: true,
    color: colors.primary, align: "left"
}});

const tableData{idx} = {json.dumps(table_data)};

slideTable{idx}.addTable(tableData{idx}, {{
    x: 0.5, y: 1.3, w: 9, h: 3.5,
    border: {{ type: "solid", pt: 1, color: colors.accent }},
    fontSize: 11,
    fontFace: "Arial"
}});

slideNum++;

'''
    return js_code


pptx_tool = save_to_pptx

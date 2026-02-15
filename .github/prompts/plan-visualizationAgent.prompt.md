# Plan: Add Visualization Agent with Corporate Consulting-Style Presentations

You'll create a visualization agent that the research agent can invoke as a tool. The viz agent generates McKinsey-style corporate presentations with professional layouts, data-driven charts, and conference-ready design suitable for executive audiences. The research agent decides when visualization is appropriate and calls the viz agent with structured data.

## Steps

### 1. Define data contracts in models/schemas.py

- Add `ChartSpec` model (type: bar/line/pie/doughnut/area, data arrays, labels, styling, insight callout)
- Add `TableSpec` model (headers, rows, column widths, highlight rows)
- Add `SlideLayout` enum (title-chart, two-column, full-bleed, data-insight)
- Add `VisualizationRequest` model (charts, tables, layouts, theme, key_message per slide)
- Add `VisualizationResponse` model (pptx_path, charts_created, slide_count)

### 2. Update configuration in config/config.py

- Add `get_viz_llm()` function that returns Anthropic Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Corporate color palettes (Navy-Teal, Navy-Gold, Charcoal-Blue)
- Chart defaults: `{showLegend: false, showTitle: true, valAxisMaxVal: auto, dataLabelPosition: 'bestFit'}`
- Slide dimensions: 16:9 widescreen (conference standard)
- Font hierarchy: Title 28pt bold, subtitle 18pt, body 14pt

### 3. Create visualization agent in agents/visualization_agent.py

- Function: `create_visualization_agent()` returns configured agent
- **LLM**: Use `get_viz_llm()` → Claude Sonnet 4 (not complexity-based, always Sonnet)
- Function: `run_visualization_agent(viz_request: VisualizationRequest)` returns PPTX path
- System prompt: "Generate McKinsey-style corporate presentation for conference audience. Use data-driven storytelling: one key message per slide, charts with insight callouts, professional corporate color schemes. Apply consulting deck principles: executive summary first, data supports narrative, clear takeaways."
- Tools: enhanced `pptx_tool` (chart-capable, layout-aware)
- Pydantic parser for `VisualizationResponse` output

### 4. Enhance PPTX tool with corporate design system in tools/pptx_export.py

**McKinsey Design Principles:**
- One chart per slide max (clarity over density)
- Data title = key insight, not just description (e.g., "Revenue grew 40% in Q4" not "Q4 Revenue")
- Chart annotations: arrows, callout boxes for critical points
- Minimalist: high data-ink ratio, remove gridlines, legends only when needed
- Corporate color palette: navy/teal primary, grey secondary, accent for highlights

**Layout Templates:**
- `title-slide`: Conference format with subtitle, date, presenter area
- `executive-summary`: Bullet points with number indicators (1., 2., 3.)
- `full-chart`: Chart fills most of slide, title is insight statement
- `chart-insight`: 60% chart, 40% text box with key takeaway
- `two-column-compare`: Side-by-side charts for before/after, A/B comparisons
- `data-table`: Formatted table with heatmap-style highlighting
- `section-divider`: Bold topic slides between sections

**Chart Styling (pptxgenjs):**
- Bar charts: horizontal for rankings, vertical for time series, data labels on bars
- Line charts: area fill for trends, markers at inflection points, annotation boxes
- Pie charts: limited to 3-5 segments, pull out key segment, percentage labels
- Tables: zebra striping subtle, bold headers, align numbers right
- Colors: `chartColors` = ['#1F4788', '#00A9A5', '#93A8AC', '#F7C548']` (corporate palette)

**Professional Details:**
- Slide numbers (bottom right)
- Consistent fonts: Calibri/Arial for corporate feel
- Generous whitespace
- Logo placeholder (top right, subtle)

### 5. Create viz agent tool wrapper in tools/visualization.py

- `@tool def visualize_data(data: str, presentation_style: str = "corporate-conference") -> str:`
- Parses JSON → `VisualizationRequest`
- Calls `run_visualization_agent()`
- Returns PPTX path with chart count

### 6. Update research agent in agents/research_agent.py

- Add `visualize_data` tool to tools list
- Update system prompt: "For conference-ready insights, use visualize_data tool. Structure data as McKinsey-style slides: lead with insight, support with chart, one message per slide. Format: chartType (bar for comparisons/rankings, line for trends/time, pie for composition max 5 parts), data arrays, labels, and KEY INSIGHT as title. Choose visualization that best proves your point."
- Instruct: "Executive summary slide first with 3-5 key findings numbered"

### 7. Add QA considerations (in pptx tool comments)

- Text overflow checks: max 6 bullets per slide, 10 words per bullet
- Chart readability: minimum font size 10pt for labels
- Color contrast: ensure text readable on backgrounds
- Consistency: same layout elements position across slides

## Verification

- Run research agent: "Analyze cloud computing market trends 2024-2026"
- Confirm research agent structures data for visualization
- Verify viz agent creates McKinsey-style deck with:
  - Executive summary slide (numbered key findings)
  - Section divider ("Market Analysis")
  - Full chart slide: line chart with trend annotation
  - Chart-insight layout: bar chart + takeaway text box
  - Professional corporate colors (navy/teal palette)
  - Data titles as insights ("Cloud adoption accelerated 45% post-pandemic")
- Test with non-visual query to confirm graceful skip
- Check viz agent uses Claude Sonnet 4 model (verify in logs/config)

## Decisions

- **Visualization LLM**: Claude Sonnet 4 (`claude-sonnet-4-20250514`) - optimized for structured output and design decisions
- **Research LLM**: Keeps existing complexity-based selection (Sonnet for simple, Opus for complex)
- **McKinsey consulting deck style**: One insight per slide, data supports narrative, executive-first structure
- **Conference audience**: 16:9 format, high contrast for projectors, minimal text density
- **Corporate palette**: Navy/teal default (professional, non-industry-specific)
- **Layout variety**: 5-6 distinct layouts prevent monotony
- **Agent-to-agent protocol**: Research agent calls viz agent when data warrants visualization
- **Optional output**: Produces 0-2 PPTXs depending on data availability

## Corporate Design Principles Applied

1. ✅ Pyramid principle: conclusion first, then supporting data
2. ✅ MECE structure: slides cover topics without overlap
3. ✅ So what? test: every chart answers "why does this matter?"
4. ✅ Slide titles = headlines, not labels
5. ✅ Professional color theory: max 3 colors per chart
6. ✅ Generous whitespace (40% of slide area minimum)

## Model Configuration

- **Research Agent**: `get_llm(query)` → Sonnet/Opus based on complexity
- **Visualization Agent**: `get_viz_llm()` → Always Claude Sonnet 4 (`claude-sonnet-4-20250514`)

## Architecture Flow

```
User Query 
  → Research Agent (LLM decides)
      → search_tool, wiki_tool (gather data)
      → save_tool (PDF export)
      → pptx_tool (text summary slides)
      → visualize_data tool (if data found)
          → Visualization Agent
              → Enhanced pptx_tool (chart generation)
              → Returns viz PPTX path
      → Research Agent returns ResearchResponse
```

## Key Advantages

- ✅ True agent-to-agent: Research agent has full control, calls viz agent when appropriate
- ✅ LLM decides visualization: Research agent's LLM evaluates if data warrants charts
- ✅ Optional visualization: No errors if no charts - normal text PPTX flow continues
- ✅ McKinsey consulting quality: Professional, conference-ready presentations
- ✅ pptxgenjs native charts: No image conversion, cleaner workflow, editable outputs
- ✅ One query, flexible outputs: 0, 1, or 2 PPTX files depending on data availability

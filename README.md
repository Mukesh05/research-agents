# Research Agents

An AI-powered research assistant that automatically generates comprehensive research reports with professional outputs in PDF and PowerPoint formats. Built with LangChain and Claude (Anthropic).

## Features

- 🔍 **Intelligent Research**: Leverages DuckDuckGo search and Wikipedia for comprehensive research
- 🤖 **Adaptive AI**: Uses Claude Sonnet for standard queries, Claude Opus for complex research
- 📄 **PDF Export**: Automatically generates formatted research reports as PDFs
- 📊 **PowerPoint Generation**: Creates professional presentations from research data
- 📈 **Data Visualization**: Generates McKinsey-style presentations with charts for numerical data
- 🎨 **Multiple Themes**: Navy-teal, navy-gold, and charcoal-blue color schemes

## Architecture

![Architecture Diagram](.docs/architecture.svg)

### Agents
- **Research Agent**: Main agent that conducts research using web search and Wikipedia
- **Visualization Agent**: Specialized agent for creating data-driven presentations with charts

### Tools
- `search_tool`: DuckDuckGo web search integration
- `wiki_tool`: Wikipedia article retrieval
- `save_to_pdf`: Export research as formatted PDF documents
- `save_to_pptx`: Create PowerPoint presentations
- `visualize_data`: Generate McKinsey-style presentations with charts

### Technology Stack
- **Python 3.11+**: Core language
- **LangChain**: Agent orchestration framework
- **Anthropic Claude**: AI models (Sonnet 4 & Opus 4)
- **Node.js**: Required for PowerPoint generation via pptxgenjs
- **ReportLab**: PDF generation
- **PptxGenJS**: JavaScript library for creating PowerPoint files

## Prerequisites

### Required
- Python 3.11 or higher
- Node.js (for PowerPoint generation)
- Anthropic API key

### Environment Setup
1. Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY=your_api_key_here
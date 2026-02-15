from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
import re

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, Preformatted, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas


# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "output"


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbers and headers."""

    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop('title', 'Research Report')
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        # Footer line only (header removed)
        self.setStrokeColorRGB(0.275, 0.510, 0.706)  # Steel blue
        self.setLineWidth(1)
        self.line(0.75*inch, 0.6*inch, letter[0] - 0.75*inch, 0.6*inch)

        # Page number
        self.setFillColorRGB(0.5, 0.5, 0.5)  # Gray
        self.setFont('Helvetica-Oblique', 9)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawCentredString(letter[0]/2, 0.4*inch, page_text)


def create_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()

    # Custom title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#294172'),  # Dark blue
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=13,
        textColor=colors.HexColor('#294172'),  # Dark blue
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#4682B4'),  # Steel blue
        borderPadding=0,
    ))

    # Subsection header style
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#4682B4'),  # Steel blue
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))

    # Body text style
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),  # Dark gray
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))

    # Bullet point style
    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leftIndent=25,
        bulletIndent=10,
        fontName='Helvetica'
    ))

    # Nested bullet point style
    styles.add(ParagraphStyle(
        name='NestedBullet',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leftIndent=40,
        bulletIndent=25,
        fontName='Helvetica'
    ))

    # Link style
    styles.add(ParagraphStyle(
        name='Link',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor('#0066CC'),  # Link blue
        spaceAfter=6,
        fontName='Helvetica',
        underline=True
    ))

    # Info box style
    styles.add(ParagraphStyle(
        name='InfoBox',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor('#505050'),
        fontName='Helvetica-Oblique',
        leftIndent=10,
        rightIndent=10,
        spaceAfter=6,
        spaceBefore=6,
        backColor=colors.HexColor('#F5F5F5'),  # Light gray
    ))

    # Code block style
    styles.add(ParagraphStyle(
        name='CodeBlock',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor('#000000'),
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        spaceAfter=12,
        spaceBefore=12,
        backColor=colors.HexColor('#F5F5F5'),  # Light gray
        borderWidth=1,
        borderColor=colors.HexColor('#CCCCCC'),
        borderPadding=8,
    ))

    # Reference style (for bibliography)
    styles.add(ParagraphStyle(
        name='Reference',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica',
        leftIndent=25,
        spaceAfter=6,
        firstLineIndent=-15,
    ))

    return styles


def _convert_unicode_scripts(text: str) -> str:
    """Convert Unicode subscripts and superscripts to XML tags for reportlab.

    Per the PDF skill guide, Unicode subscript/superscript characters render
    as black boxes in reportlab's built-in fonts. We must use XML tags instead.
    """
    # Subscript mappings
    subscripts = {
        '₀': '<sub>0</sub>', '₁': '<sub>1</sub>', '₂': '<sub>2</sub>',
        '₃': '<sub>3</sub>', '₄': '<sub>4</sub>', '₅': '<sub>5</sub>',
        '₆': '<sub>6</sub>', '₇': '<sub>7</sub>', '₈': '<sub>8</sub>',
        '₉': '<sub>9</sub>', '₊': '<sub>+</sub>', '₋': '<sub>-</sub>',
        '₌': '<sub>=</sub>', '₍': '<sub>(</sub>', '₎': '<sub>)</sub>',
        'ₐ': '<sub>a</sub>', 'ₑ': '<sub>e</sub>', 'ₒ': '<sub>o</sub>',
        'ₓ': '<sub>x</sub>', 'ₔ': '<sub>ə</sub>', 'ₕ': '<sub>h</sub>',
        'ₖ': '<sub>k</sub>', 'ₗ': '<sub>l</sub>', 'ₘ': '<sub>m</sub>',
        'ₙ': '<sub>n</sub>', 'ₚ': '<sub>p</sub>', 'ₛ': '<sub>s</sub>',
        'ₜ': '<sub>t</sub>',
    }

    # Superscript mappings
    superscripts = {
        '⁰': '<super>0</super>', '¹': '<super>1</super>', '²': '<super>2</super>',
        '³': '<super>3</super>', '⁴': '<super>4</super>', '⁵': '<super>5</super>',
        '⁶': '<super>6</super>', '⁷': '<super>7</super>', '⁸': '<super>8</super>',
        '⁹': '<super>9</super>', '⁺': '<super>+</super>', '⁻': '<super>-</super>',
        '⁼': '<super>=</super>', '⁽': '<super>(</super>', '⁾': '<super>)</super>',
        'ⁿ': '<super>n</super>', 'ⁱ': '<super>i</super>',
    }

    # Apply conversions
    for unicode_char, xml_tag in {**subscripts, **superscripts}.items():
        text = text.replace(unicode_char, xml_tag)

    return text


def extract_urls(text: str) -> list[tuple[str, str]]:
    """Extract URLs from text and return list of (text_before_url, url) pairs."""
    url_pattern = r'(https?://[^\s\)\]]+)'
    return re.findall(url_pattern, text)


def _create_cover_page(title: str, styles: dict) -> list:
    """Create a professional cover page for the research report."""
    cover_elements = []

    # Add large vertical space
    cover_elements.append(Spacer(1, 2*inch))

    # Title - extra large and centered
    cover_title_style = ParagraphStyle(
        name='CoverTitle',
        parent=styles['CustomTitle'],
        fontSize=28,
        textColor=colors.HexColor('#294172'),
        spaceAfter=0.5*inch,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=34
    )
    cover_elements.append(Paragraph(title, cover_title_style))

    # "Prepared by" section
    cover_elements.append(Spacer(1, 1*inch))

    prepared_style = ParagraphStyle(
        name='PreparedBy',
        fontSize=14,
        textColor=colors.HexColor('#4682B4'),
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=8
    )
    cover_elements.append(Paragraph("Prepared by", prepared_style))

    agent_style = ParagraphStyle(
        name='AgentName',
        fontSize=16,
        textColor=colors.HexColor('#294172'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=1*inch
    )
    cover_elements.append(Paragraph("Research Agent", agent_style))

    # Date
    date_str = datetime.now().strftime("%B %d, %Y")
    date_style = ParagraphStyle(
        name='CoverDate',
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    cover_elements.append(Paragraph(date_str, date_style))

    # Page break after cover
    cover_elements.append(PageBreak())

    return cover_elements


def _parse_markdown_table(lines: list[str], start_idx: int) -> tuple[list, int]:
    """Parse a markdown table and return Table flowable and next line index.

    Expected format:
    | Header 1 | Header 2 |
    |----------|----------|
    | Data 1   | Data 2   |
    """
    table_data = []
    idx = start_idx

    # Parse table rows
    while idx < len(lines):
        line = lines[idx].strip()
        if not line.startswith('|'):
            break

        # Skip separator lines (|---|---|)
        if re.match(r'^\|[\s\-\|]+\|$', line):
            idx += 1
            continue

        # Parse cells
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        table_data.append(cells)
        idx += 1

    return table_data, idx


def _create_table_flowable(table_data: list[list[str]], styles: dict) -> Table:
    """Create a styled Table flowable from table data."""
    if not table_data:
        return None

    # Convert text cells to Paragraph objects for better formatting
    formatted_data = []
    for i, row in enumerate(table_data):
        formatted_row = []
        for cell in row:
            if i == 0:  # Header row
                # Use bold style for headers
                header_style = ParagraphStyle(
                    name='TableHeader',
                    fontSize=10,
                    textColor=colors.whitesmoke,
                    fontName='Helvetica-Bold',
                    alignment=TA_CENTER
                )
                formatted_row.append(Paragraph(cell, header_style))
            else:
                # Regular body style
                cell_style = ParagraphStyle(
                    name='TableCell',
                    fontSize=9,
                    textColor=colors.HexColor('#333333'),
                    fontName='Helvetica',
                    alignment=TA_LEFT
                )
                formatted_row.append(Paragraph(cell, cell_style))
        formatted_data.append(formatted_row)

    # Create table
    table = Table(formatted_data)

    # Apply styling
    table_style = TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),  # Steel blue
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),

        # Body styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Alternating row colors for body
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#F8F8F8')]),
    ])

    table.setStyle(table_style)
    return table


def _detect_and_create_image(line: str, styles: dict) -> Image:
    """Detect markdown image syntax and create Image flowable.

    Format: ![alt text](path/to/image.png)
    """
    img_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    match = re.match(img_pattern, line.strip())

    if not match:
        return None

    alt_text = match.group(1)
    img_path = match.group(2)

    try:
        # Try to resolve path relative to output directory or absolute
        if not Path(img_path).is_absolute():
            img_path = OUTPUT_DIR / img_path

        if not Path(img_path).exists():
            # Return error message as paragraph instead
            return Paragraph(f"[Image not found: {img_path}]", styles['InfoBox'])

        # Create image with max width constraint
        img = Image(str(img_path), width=6*inch,
                    height=4*inch, kind='proportional')
        return img
    except Exception as e:
        return Paragraph(f"[Error loading image: {str(e)}]", styles['InfoBox'])


class SectionNumberTracker:
    """Track hierarchical section numbering (1, 1.1, 1.2, 2, 2.1, etc.)."""

    def __init__(self):
        self.counters = [0, 0, 0]  # Support up to 3 levels
        self.toc_entries = []

    def get_number(self, level: int) -> str:
        """Get the section number for the given level (1=top, 2=sub, 3=subsub)."""
        if level < 1 or level > 3:
            return ""

        # Increment counter at this level
        self.counters[level - 1] += 1

        # Reset all deeper levels
        for i in range(level, 3):
            self.counters[i] = 0

        # Build number string
        if level == 1:
            return f"{self.counters[0]}"
        elif level == 2:
            return f"{self.counters[0]}.{self.counters[1]}"
        else:
            return f"{self.counters[0]}.{self.counters[1]}.{self.counters[2]}"

    def add_toc_entry(self, level: int, title: str, key: str):
        """Add an entry for the table of contents."""
        self.toc_entries.append((level, title, key))


def generate_filename(data: str) -> str:
    """Generate a filename from the data content."""
    lines = [line.strip() for line in data.split('\n') if line.strip()]
    if not lines:
        return "research_output.pdf"

    first_line = lines[0]
    for prefix in ["Topic:", "Research:", "Summary:"]:
        first_line = first_line.replace(prefix, "").strip()

    words = first_line.split()[:5]
    filename = "_".join(words).lower()
    filename = re.sub(r'[^a-z0-9_]', '', filename)
    filename = filename[:50] if len(filename) > 50 else filename

    if not filename:
        return "research_output.pdf"

    return f"{filename}_research.pdf"


@tool
def save_to_pdf(data: str, title: str, filename: str = None) -> str:
    """Saves structured research data to a professional PDF report with cover page, table of contents, 
    tables, images, code blocks, and clickable links. Title is required. Filename is auto-generated 
    from content if not provided."""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Generate filename from data if not provided
    if not filename:
        filename = generate_filename(data)

    # Title is required from user input
    if not title or not title.strip():
        raise ValueError("Title is required and must be provided by the user")

    # Build full path
    filepath = OUTPUT_DIR / filename

    # Apply Unicode conversion early in pipeline
    data = _convert_unicode_scripts(data)

    # Create PDF document with metadata
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch,
    )

    # Set PDF metadata
    doc.title = title
    doc.author = "Research Agent"
    doc.subject = f"Research Report: {title}"
    doc.creator = "Research Agent PDF Generator"

    # Container for the 'Flowable' objects
    story = []
    styles = create_styles()

    # Initialize section numbering tracker
    section_tracker = SectionNumberTracker()

    # Track references for bibliography
    references = []
    reference_counter = 1

    # 1. Add cover page
    story.extend(_create_cover_page(title, styles))

    # 2. Add Table of Contents
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            name='TOCHeading1',
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#294172'),
            leftIndent=0,
            spaceAfter=6,
            leading=16
        ),
        ParagraphStyle(
            name='TOCHeading2',
            fontSize=10,
            fontName='Helvetica',
            textColor=colors.HexColor('#4682B4'),
            leftIndent=20,
            spaceAfter=4,
            leading=14
        ),
        ParagraphStyle(
            name='TOCHeading3',
            fontSize=9,
            fontName='Helvetica',
            textColor=colors.HexColor('#666666'),
            leftIndent=40,
            spaceAfter=3,
            leading=12
        ),
    ]

    # Add TOC title
    toc_title_style = ParagraphStyle(
        name='TOCTitle',
        fontSize=18,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#294172'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Table of Contents", toc_title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(toc)
    story.append(PageBreak())

    # 3. Process main content
    lines = data.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    code_language = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle code blocks
        if stripped.startswith('```'):
            if not in_code_block:
                # Start code block
                in_code_block = True
                code_language = stripped[3:].strip() or 'text'
                code_lines = []
            else:
                # End code block - create Preformatted flowable
                in_code_block = False
                code_text = '\n'.join(code_lines)

                # Add language label if specified
                if code_language and code_language != 'text':
                    lang_style = ParagraphStyle(
                        name='CodeLanguage',
                        fontSize=8,
                        fontName='Courier-Bold',
                        textColor=colors.HexColor('#666666'),
                        leftIndent=20,
                        spaceAfter=2
                    )
                    story.append(Paragraph(f"[{code_language}]", lang_style))

                # Create preformatted text block
                pre = Preformatted(code_text, styles['CodeBlock'])
                story.append(pre)
                story.append(Spacer(1, 0.1*inch))

            i += 1
            continue

        if in_code_block:
            code_lines.append(line.rstrip())
            i += 1
            continue

        # Check for markdown tables
        if stripped.startswith('|') and i + 1 < len(lines):
            table_data, next_i = _parse_markdown_table(lines, i)
            if table_data:
                table_flowable = _create_table_flowable(table_data, styles)
                if table_flowable:
                    story.append(Spacer(1, 0.1*inch))
                    story.append(table_flowable)
                    story.append(Spacer(1, 0.2*inch))
                i = next_i
                continue

        # Check for images
        if stripped.startswith('!['):
            img_flowable = _detect_and_create_image(stripped, styles)
            if img_flowable:
                story.append(Spacer(1, 0.1*inch))
                story.append(img_flowable)
                story.append(Spacer(1, 0.2*inch))
            i += 1
            continue

        # Check for page breaks
        if stripped in ['---', '\\pagebreak', '<pagebreak>']:
            story.append(PageBreak())
            i += 1
            continue

        # Empty lines
        if not stripped:
            story.append(Spacer(1, 0.15*inch))
            i += 1
            continue

        # Detect section headers with numbering
        header_level = 0
        header_text = stripped

        if stripped.startswith('### '):
            header_level = 3
            header_text = stripped[4:]
        elif stripped.startswith('## '):
            header_level = 2
            header_text = stripped[3:]
        elif stripped.startswith('# '):
            header_level = 1
            header_text = stripped[2:]
        elif re.match(r'^[A-Z][^.!?]*:$', stripped) and len(stripped) < 60:
            header_level = 1
            header_text = stripped.rstrip(':')

        if header_level > 0:
            # Generate section number
            section_num = section_tracker.get_number(header_level)
            full_header = f"{section_num}. {header_text}"

            # Create paragraph with bookmark
            if header_level == 1:
                style = styles['SectionHeader']
            elif header_level == 2:
                style = styles['SubsectionHeader']
            else:
                style = styles['SubsectionHeader']

            # Add bookmark anchor
            bookmark_key = re.sub(
                r'[^a-z0-9_]', '', header_text.lower().replace(' ', '_'))
            bookmarked_text = f'<a name="{bookmark_key}"/>{full_header}'
            para = Paragraph(bookmarked_text, style)
            story.append(para)

            i += 1
            continue

        # Detect bullet points
        if stripped.startswith(('- ', '* ', '• ')):
            text = f"• {stripped[2:]}"
            # Convert Unicode and process URLs
            text = _convert_unicode_scripts(text)
            urls = extract_urls(text)
            if urls:
                for url in urls:
                    link_html = f'<a href="{url}" color="blue"><u>{url}</u></a>'
                    text = text.replace(url, link_html)
                    if url not in references:
                        references.append(url)
            story.append(Paragraph(text, styles['BulletPoint']))
            i += 1
            continue

        if stripped.startswith(('  - ', '  * ', '  • ')):
            text = f"◦ {stripped[4:]}"
            text = _convert_unicode_scripts(text)
            urls = extract_urls(text)
            if urls:
                for url in urls:
                    link_html = f'<a href="{url}" color="blue"><u>{url}</u></a>'
                    text = text.replace(url, link_html)
                    if url not in references:
                        references.append(url)
            story.append(Paragraph(text, styles['NestedBullet']))
            i += 1
            continue

        # Detect numbered lists
        if re.match(r'^\d+[\.\)]\s', stripped):
            text = re.sub(r'^\d+[\.\)]\s', '• ', stripped)
            text = _convert_unicode_scripts(text)
            urls = extract_urls(text)
            if urls:
                for url in urls:
                    link_html = f'<a href="{url}" color="blue"><u>{url}</u></a>'
                    text = text.replace(url, link_html)
                    if url not in references:
                        references.append(url)
            story.append(Paragraph(text, styles['BulletPoint']))
            i += 1
            continue

        # Regular paragraph with URL handling
        text = stripped
        text = _convert_unicode_scripts(text)
        urls = extract_urls(text)

        if urls:
            # Process text with embedded links
            for url in urls:
                link_html = f'<a href="{url}" color="blue"><u>{url}</u></a>'
                text = text.replace(url, link_html)
                if url not in references:
                    references.append(url)

        story.append(Paragraph(text, styles['CustomBody']))
        i += 1

    # 4. Add References section if URLs were found
    if references:
        story.append(PageBreak())

        # References header
        ref_header_style = ParagraphStyle(
            name='ReferencesHeader',
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#294172'),
            spaceAfter=20,
            spaceBefore=10
        )
        story.append(Paragraph("References", ref_header_style))
        story.append(Spacer(1, 0.2*inch))

        # Add each reference
        for idx, url in enumerate(references, 1):
            ref_text = f'[{idx}] <a href="{url}" color="blue"><u>{url}</u></a>'
            story.append(Paragraph(ref_text, styles['Reference']))

    # Build PDF with custom canvas for headers/footers
    doc.build(story, canvasmaker=lambda *args, **
              kwargs: NumberedCanvas(*args, title=title, **kwargs))

    return f"Professional research report successfully saved to {filepath}"


save_tool = save_to_pdf

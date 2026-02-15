# Plan: Professional Research Report PDF Generation

Your current PDF export has good styling fundamentals but lacks essential features for professional research reports: no cover page, no table of contents, no table/image support, and Unicode rendering issues that will break scientific content. The plan focuses on implementing the high-impact features recommended in your [PDF skill guide](.github/skills/pdf/SKILL.md) using reportlab's full capabilities.

**Key Decisions:**
- Keep reportlab (already imported, well-suited for the task)
- Maintain existing color scheme and basic styling structure
- Add cover page as first page with custom template
- Implement auto-generated TOC with section tracking
- Add markdown-style table parsing (`| col | col |`) and code block detection (` ``` `)
- Fix Unicode subscript/superscript issue per skill guide warning

**Steps**

1. **Fix Unicode subscript/superscript rendering** in [tools/pdf_export.py](tools/pdf_export.py)
   - Add `_convert_unicode_scripts()` function to detect Unicode sub/superscripts (₀₁₂, ⁰¹²)
   - Convert to XML tags `<sub>` and `<super>` before creating Paragraph objects
   - Apply to all content before processing to prevent black box rendering per [SKILL.md](c:\Users\mysti\Desktop\New folder\agents\.github\skills\pdf\SKILL.md#L175-L195)

2. **Implement cover page generation** in [tools/pdf_export.py](tools/pdf_export.py)
   - Create `_create_cover_page()` function returning list of flowables
   - Include: large centered title, "Prepared by Research Agent", date, optional abstract area
   - Add `PageBreak()` after cover content
   - Use larger fonts (24pt title) and more spacing than body

3. **Add Table of Contents support** in [tools/pdf_export.py](tools/pdf_export.py)
   - Initialize `TableOfContents()` (already imported but unused)
   - Track section headers during content parsing
   - Add bookmark entries for each section using `Paragraph.text` with `<a name="section1"/>`
   - Insert TOC flowable after cover page, before main content
   - Reference: reportlab's TOC links to named anchors

4. **Implement table parsing and generation** in [tools/pdf_export.py](tools/pdf_export.py)
   - Add `_parse_markdown_table()` to detect markdown tables (`| col1 | col2 |`)
   - Extract headers and rows into nested list structure
   - Create `Table()` flowables with `TableStyle` (grid lines, header background)
   - Use steel blue header background matching existing color scheme
   - Reference: [reference.md](c:\Users\mysti\Desktop\New folder\agents\.github\skills\pdf\reference.md) lines 387-420

5. **Add image embedding support** in [tools/pdf_export.py](tools/pdf_export.py)
   - Import `Image` from `reportlab.platypus`
   - Detect markdown image syntax `![alt](path)` during parsing
   - Create Image flowables with max width constraint (6 inches)
   - Handle file paths relative to output directory
   - Add error handling for missing/invalid images

6. **Implement code block formatting** in [tools/pdf_export.py](tools/pdf_export.py)
   - Detect fenced code blocks (` ``` `) in content
   - Create new `CodeBlock` paragraph style: Courier font, 9pt, light gray background
   - Preserve whitespace and indentation using `Preformatted()` or custom style
   - Add subtle border around code blocks

7. **Add bibliography/references section** in [tools/pdf_export.py](tools/pdf_export.py)
   - Track URLs mentioned during content parsing
   - Auto-generate "References" section at document end
   - Format as numbered list with clickable hyperlinks
   - Extract citations from search_tool and wiki_tool outputs

8. **Implement section auto-numbering** in [tools/pdf_export.py](tools/pdf_export.py)
   - Track header hierarchy (# = level 1, ## = level 2, ### = level 3)
   - Prepend section numbers to headers (1, 1.1, 1.2, 2, 2.1)
   - Reset counters appropriately for each level
   - Feed numbered headers to TOC

9. **Enhance typography with multiple fonts** in [tools/pdf_export.py](tools/pdf_export.py)
   - Add Courier font for code and technical content
   - Consider Times-Roman as alternate body font option
   - Update style definitions to reference new fonts
   - Ensure consistent font usage across document

10. **Set PDF metadata** in [tools/pdf_export.py](tools/pdf_export.py)
    - Set `doc.title`, `doc.author`, `doc.subject` properties on `SimpleDocTemplate`
    - Use title parameter for doc.title
    - Set author to "Research Agent"
    - Add creation date to metadata
    - Improve searchability and professional appearance

11. **Add page break control** in [tools/pdf_export.py](tools/pdf_export.py)
    - Detect page break markers (`---` or `\pagebreak`)
    - Insert `PageBreak()` flowable at marker locations
    - Allow agent to control section placement on pages

12. **Refactor main `save_to_pdf()` function** in [tools/pdf_export.py](tools/pdf_export.py)
    - Update content parsing loop to handle all new elements (tables, images, code)
    - Sequence: cover page → TOC → main content → references
    - Apply Unicode conversion early in pipeline
    - Maintain backward compatibility with existing title parameter

**Verification**

Run test with complex research query:
```bash
python main.py
```
Input query: "Explain quantum computing with examples of H₂O molecule, code samples, and data tables"

Expected PDF features:
- Cover page with title and date
- Table of contents with clickable links
- Properly rendered H₂O subscript (not black boxes)
- Code blocks in monospace with background
- Tables with styled headers
- References section with hyperlinks
- Page numbers throughout
- Section numbering (1, 1.1, 2, etc.)

Manual checks:
- Open generated PDF in Adobe Reader/browser
- Verify TOC links navigate correctly
- Confirm Unicode renders (₂ should display, not ▯)
- Check table alignment and borders
- Verify hyperlinks are clickable

**Decisions**

- **Chose reportlab over alternatives**: Already integrated, handles all requirements, skill guide provides extensive examples
- **Cover page before TOC**: Standard research report structure
- **Automatic reference generation**: Better than manual - agent doesn't need to format citations
- **Markdown-style parsing**: Consistent with common conventions, easy for LLM agent to generate
- **Section numbering hierarchy**: Improves navigation and professional appearance per academic standards

---

This plan transforms your PDF output from basic formatted text to publication-ready research reports. The most critical fixes (Unicode, cover page, TOC, tables) are prioritized first.

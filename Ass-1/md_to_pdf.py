"""Convert markdown to PDF using markdown2 + fpdf2 with HTML parsing."""
import re
import sys
from pathlib import Path
from markdown2 import markdown
from fpdf import FPDF

def sanitize_text(text):
    """Replace non-latin1 characters with ASCII equivalents."""
    replacements = {
        '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u2192': '->',
        '\u00d7': 'x', '\u2248': '~', '\u00b1': '+/-',
        '\u03b1': 'alpha', '\u03b2': 'beta', '\u03b3': 'gamma',
        '\u03b4': 'delta', '\u03b5': 'epsilon', '\u03b8': 'theta',
        '\u03bb': 'lambda', '\u03c3': 'sigma', '\u03c9': 'omega',
        '\u0394': 'Delta', '\u03c0': 'pi',
        '\u2080': '0', '\u2081': '1', '\u2082': '2', '\u2083': '3',
        '\u2084': '4', '\u2085': '5', '\u2086': '6', '\u2087': '7',
        '\u2088': '8', '\u2089': '9',
        '\u2070': '0', '\u00b9': '1', '\u00b2': '2', '\u00b3': '3',
        '\u2074': '4', '\u2075': '5', '\u2076': '6',
        '\u2265': '>=', '\u2264': '<=', '\u2260': '!=',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text

def strip_html_in_tables(html):
    """Remove <em>, <strong>, <code> tags inside <td>/<th> elements."""
    html = re.sub(r'(<t[dh][^>]*>)(.*?)(</t[dh]>)', 
                  lambda m: m.group(1) + re.sub(r'</?(?:em|strong|code|b|i)>', '', m.group(2)) + m.group(3),
                  html, flags=re.DOTALL)
    return html

def md_to_pdf(md_path, pdf_path):
    md_text = Path(md_path).read_text(encoding='utf-8')
    md_text = sanitize_text(md_text)
    html = markdown(md_text, extras=['tables', 'fenced-code-blocks', 'header-ids'])
    html = strip_html_in_tables(html)
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    pdf.write_html(html)
    pdf.output(pdf_path)
    print(f"PDF saved: {pdf_path}")

if __name__ == "__main__":
    md_file = sys.argv[1] if len(sys.argv) > 1 else "Part_A_Report.md"
    pdf_file = md_file.replace(".md", ".pdf")
    md_to_pdf(md_file, pdf_file)

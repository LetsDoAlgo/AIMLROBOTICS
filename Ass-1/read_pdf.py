import fitz
import sys

pdf_path = r"c:\Users\INAYGUP1\OneDrive - ABB\Ayushi_M\SEM3\Robotics\Ass-1\AIML ZG528 Assignment 1 May 2026.pdf"
try:
    doc = fitz.open(pdf_path)
    print(f"Number of pages: {len(doc)}")
    for i, page in enumerate(doc):
        text = page.get_text()
        print(f"--- Page {i+1} ---")
        print(text)
    doc.close()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

"""Convert Viva_Guide.md to a styled PDF using Chrome/Edge headless print."""
import subprocess, sys, pathlib, time, re

MD_FILE   = pathlib.Path(__file__).parent / "Viva_Guide.md"
HTML_FILE = pathlib.Path(__file__).parent / "Viva_Guide_print.html"
PDF_FILE  = pathlib.Path(__file__).parent / "Viva_Guide.pdf"

# ── Step 1: markdown → HTML ───────────────────────────────────────────────────
try:
    import markdown2
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown2", "-q"])
    import markdown2

md_text = MD_FILE.read_text(encoding="utf-8")

# Replace ```mermaid blocks with <div class="mermaid"> for mermaid.js rendering
md_text_clean = re.sub(
    r"```mermaid\n(.*?)```",
    lambda m: f'<div class="mermaid">\n{m.group(1)}\n</div>',
    md_text, flags=re.DOTALL
)

body = markdown2.markdown(
    md_text_clean,
    extras=["tables", "fenced-code-blocks", "header-ids", "strike", "footnotes"]
)

CSS = """
<style>
  @page { size: A4; margin: 18mm 16mm 18mm 16mm; }
  * { box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Calibri, Arial, sans-serif;
    font-size: 10.5pt; color: #111; line-height: 1.55;
    max-width: 100%;
  }
  h1 {
    font-size: 20pt; color: #002855;
    border-bottom: 3px solid #002855; padding-bottom: 6px;
    margin-top: 0;
  }
  h2 {
    font-size: 14pt; color: #004A8F;
    border-bottom: 2px solid #b8d4f0; padding-bottom: 4px;
    margin-top: 26px; page-break-after: avoid;
  }
  h3 {
    font-size: 12pt; color: #005f8a;
    margin-top: 18px; page-break-after: avoid;
  }
  h4 {
    font-size: 10.5pt; color: #444;
    margin-top: 12px; font-style: italic; page-break-after: avoid;
  }
  /* ── tables ── */
  table {
    border-collapse: collapse; width: 100%;
    margin: 10px 0; font-size: 9.5pt;
    page-break-inside: auto;
  }
  thead tr { background: #002855; color: #fff; }
  th { padding: 6px 9px; text-align: left; font-weight: 600; }
  td { border: 1px solid #b8cfe4; padding: 5px 9px; vertical-align: top; }
  tr:nth-child(even) td { background: #eef4fc; }
  /* ── code ── */
  code {
    background: #f3f3f3; padding: 1px 5px;
    border-radius: 3px; font-family: Consolas, monospace; font-size: 9.5pt;
  }
  pre {
    background: #f3f3f3; padding: 10px 14px; border-radius: 5px;
    border-left: 4px solid #002855; font-size: 9pt;
    white-space: pre-wrap; word-break: break-word; page-break-inside: avoid;
  }
  pre code { background: none; padding: 0; }
  /* ── blockquote ── */
  blockquote {
    border-left: 4px solid #004A8F; margin: 8px 0;
    padding: 6px 14px; background: #eaf2ff; color: #222;
    page-break-inside: avoid;
  }
  /* ── misc ── */
  hr  { border: none; border-top: 1px solid #ccc; margin: 16px 0; }
  a   { color: #004A8F; text-decoration: none; }
  ul,ol { margin: 4px 0 4px 22px; }
  li  { margin-bottom: 2px; }
  /* ── mermaid diagrams ── */
  .mermaid { margin: 14px 0; text-align: center; page-break-inside: avoid; }
  svg { max-width: 100%; height: auto; }
</style>
"""

MERMAID_JS = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({ startOnLoad: true, theme: 'default',
    themeVariables: { fontSize: '11px' } });
</script>
"""

html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AIML ZG528 — Viva Guide</title>
{CSS}
</head>
<body>
{body}
{MERMAID_JS}
</body>
</html>"""

HTML_FILE.write_text(html_full, encoding="utf-8")
print(f"[1/2] HTML written → {HTML_FILE}")

# ── Step 2: HTML → PDF via Chrome/Edge headless ───────────────────────────────
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

browser = next((p for p in chrome_paths if pathlib.Path(p).exists()), None)

if browser:
    print(f"    Using browser: {browser}")
    # Give mermaid.js time to render by using --virtual-time-budget
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",
        f"--print-to-pdf={PDF_FILE}",
        "--print-to-pdf-no-header",
        str(HTML_FILE.resolve()),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if PDF_FILE.exists() and PDF_FILE.stat().st_size > 1000:
        print(f"[2/2] PDF written → {PDF_FILE}")
    else:
        print(f"[!] PDF may be incomplete. stderr: {result.stderr[:300]}")
else:
    print("[!] No Chrome/Edge found. Open Viva_Guide_print.html in browser and print to PDF.")


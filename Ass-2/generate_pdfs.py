#!/usr/bin/env python3
"""Generate PDF files from Markdown in Ass-2.

Usage:
  python generate_pdfs.py
  python generate_pdfs.py Part_A_Report.md Group2_Assignment2_Wiki.md
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

from fpdf import FPDF


DEFAULT_FILES = [
    "Part_A_Report.md",
    "Group2_Assignment2_Wiki.md",
]


def sanitize_text(text: str) -> str:
    replacements = {
        "\u2013": "-",
        "\u2014": "--",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u2192": "->",
        "\u00d7": "x",
        "\u2248": "~",
        "\u00b1": "+/-",
        "\u03b1": "alpha",
        "\u03b2": "beta",
        "\u03b3": "gamma",
        "\u03b4": "delta",
        "\u03b5": "epsilon",
        "\u03b8": "theta",
        "\u03bb": "lambda",
        "\u03c3": "sigma",
        "\u03c9": "omega",
        "\u0394": "Delta",
        "\u03c0": "pi",
        "\u2080": "0",
        "\u2081": "1",
        "\u2082": "2",
        "\u2083": "3",
        "\u2084": "4",
        "\u2085": "5",
        "\u2086": "6",
        "\u2087": "7",
        "\u2088": "8",
        "\u2089": "9",
        "\u2070": "0",
        "\u00b9": "1",
        "\u00b2": "2",
        "\u00b3": "3",
        "\u2074": "4",
        "\u2075": "5",
        "\u2076": "6",
        "\u207b": "-",
        "\u2265": ">=",
        "\u2264": "<=",
        "\u2260": "!=",
        "\u00b0": " deg",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def remove_internal_anchor_links(md_text: str) -> str:
    return re.sub(r"\[([^\]]+)\]\(#([^\)]+)\)", r"\1", md_text)


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9\s-]", "", ascii_text)
    ascii_text = re.sub(r"\s+", "-", ascii_text).strip("-")
    return ascii_text


def strip_inline_markdown(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"[Image: \1]", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", text)
    return text.strip()


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_table_separator(line: str) -> bool:
    stripped = line.strip().replace("|", "").replace(":", "").replace("-", "")
    return stripped == ""


def parse_table_row(line: str) -> list[str]:
    return [strip_inline_markdown(cell.strip()) for cell in line.strip().strip("|").split("|")]


class MarkdownPDF(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(18, 18, 18)
        self.add_page()
        self.set_title("Markdown Report")
        self.doc_title = "Markdown Report"
        self._title_rendered = False
        self.anchor_links: dict[str, int] = {}
        self._set_body_font()

    def _get_anchor_link(self, anchor: str) -> int:
        if anchor not in self.anchor_links:
            self.anchor_links[anchor] = self.add_link()
        return self.anchor_links[anchor]

    def set_anchor(self, anchor: str) -> None:
        link = self._get_anchor_link(anchor)
        self.set_link(link, page=self.page_no(), y=self.get_y())

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", style="I", size=8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, self.doc_title, new_x="LMARGIN", new_y="NEXT", align="R")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 6, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def _epw(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def _set_body_font(self) -> None:
        self.set_font("Helvetica", size=12)

    def _write_line(self, text: str, h: float = 6.0) -> None:
        self.set_x(self.l_margin)
        self.multi_cell(0, h, text)

    def _write_paragraph(self, text: str) -> None:
        self._set_body_font()
        self.set_x(self.l_margin)
        self.multi_cell(0, 7.2, text)
        self.ln(2.2)

    def _wrap_text(self, text: str, width: float) -> list[str]:
        words = text.split()
        if not words:
            return [""]

        lines: list[str] = []
        current = ""
        for word in words:
            if self.get_string_width(word) > width:
                if current:
                    lines.append(current)
                    current = ""

                chunk = ""
                for char in word:
                    candidate = f"{chunk}{char}"
                    if chunk and self.get_string_width(candidate) > width:
                        lines.append(chunk)
                        chunk = char
                    else:
                        chunk = candidate
                if chunk:
                    lines.append(chunk)
                continue

            if not current:
                current = word
                continue

            candidate = f"{current} {word}"
            if self.get_string_width(candidate) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def add_heading(self, level: int, text: str) -> None:
        heading_plain = strip_inline_markdown(text)
        heading_anchor = slugify(heading_plain)

        sizes = {1: 18, 2: 15, 3: 13, 4: 11}
        size = sizes.get(level, 10)
        self.ln(4 if level <= 2 else 2.5)
        if level == 1:
            self.doc_title = heading_plain
            self.set_title(self.doc_title)
        if heading_anchor:
            self.set_anchor(heading_anchor)
        self.set_font("Helvetica", style="B", size=size)
        self.set_x(self.l_margin)
        if level == 1:
            self.multi_cell(0, 8, heading_plain, align="C")
            self.set_draw_color(180, 180, 180)
            self.line(self.l_margin + 20, self.get_y(), self.w - self.r_margin - 20, self.get_y())
            self.ln(3)
            self._title_rendered = True
        elif level == 2 and self._title_rendered and self.page_no() == 1 and self.get_y() < 50:
            self.set_font("Helvetica", style="B", size=12)
            self.set_text_color(70, 70, 70)
            self.multi_cell(0, 6.5, heading_plain, align="C")
            self.set_text_color(0, 0, 0)
            self.ln(2)
        else:
            if level == 2:
                self.set_draw_color(205, 205, 205)
                self.line(self.l_margin, self.get_y() - 1.5, self.w - self.r_margin, self.get_y() - 1.5)
                self.ln(1)
            heading_text = heading_plain
            self.multi_cell(0, 7 if level <= 2 else 6, heading_text)
            self.ln(1)
        self._set_body_font()

    def add_toc_link_item(self, label: str, anchor: str, indent_level: int = 0) -> None:
        self._set_body_font()
        bullet_offset = min(indent_level, 3) * 6
        text_x = self.l_margin + 3 + bullet_offset
        link = self._get_anchor_link(anchor)

        self.set_x(text_x)
        self.cell(4, 6.8, "-")
        self.set_font("Helvetica", style="U", size=12)
        self.set_text_color(35, 70, 150)
        self.cell(self._epw() - 8 - bullet_offset, 6.8, label, link=link)
        self.set_text_color(0, 0, 0)
        self.ln(7.2)
        self._set_body_font()

    def add_rule(self) -> None:
        y = self.get_y() + 1
        self.set_draw_color(170, 170, 170)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)

    def add_bullet_item(self, text: str, indent_level: int = 0) -> None:
        self._set_body_font()
        indent = min(max(indent_level, 0), 4) * 6
        bullet_x = self.l_margin + 3 + indent
        marker = "-" if indent_level == 0 else "o"
        self.set_x(bullet_x)
        self.cell(5, 6.9, marker)
        self.multi_cell(self._epw() - 8 - indent, 6.9, strip_inline_markdown(text))
        self.set_x(self.l_margin)
        self.ln(1.1)

    def add_numbered_item(self, number: str, text: str, indent_level: int = 0) -> None:
        self._set_body_font()
        indent = min(max(indent_level, 0), 4) * 6
        self.set_x(self.l_margin + 1 + indent)
        self.cell(10, 6.9, f"{number}.")
        self.multi_cell(self._epw() - 10 - indent, 6.9, strip_inline_markdown(text))
        self.set_x(self.l_margin)
        self.ln(1.1)

    def add_quote(self, text: str) -> None:
        quote_x = self.l_margin + 6
        quote_y = self.get_y()
        quote_w = self._epw() - 6
        self.set_font("Helvetica", style="I", size=9)
        self.set_text_color(70, 70, 70)
        self.set_fill_color(245, 247, 250)
        self.set_x(quote_x)
        self.multi_cell(quote_w, 5.8, strip_inline_markdown(text), border="L", fill=True)
        self.set_text_color(0, 0, 0)
        self._set_body_font()
        self.set_x(self.l_margin)
        self.ln(1.5)

    def add_labeled_paragraph(self, label: str, body: str) -> None:
        label = strip_inline_markdown(label).strip()
        body = strip_inline_markdown(body).strip()
        self.set_x(self.l_margin)
        self.set_font("Helvetica", style="B", size=12)
        self.multi_cell(0, 6.8, label)
        if body:
            self.set_font("Helvetica", size=12)
            self.set_x(self.l_margin + 3)
            self.multi_cell(self._epw() - 3, 6.8, body)
        self.ln(1.8)

    def add_code_block(self, lines: list[str]) -> None:
        self.set_font("Courier", size=9.5)
        block_x = self.l_margin
        block_w = self._epw()
        inner_pad_x = 2.5
        inner_pad_y = 2.3
        line_h = 5.4
        usable_w = block_w - (2 * inner_pad_x)

        wrapped_lines: list[str] = []
        for line in lines:
            text = line if line else " "
            if self.get_string_width(text) <= usable_w:
                wrapped_lines.append(text)
                continue

            # Split overlong code lines by characters so FPDF never receives an unrenderable token.
            chunk = ""
            for ch in text:
                candidate = f"{chunk}{ch}"
                if chunk and self.get_string_width(candidate) > usable_w:
                    wrapped_lines.append(chunk)
                    chunk = ch
                else:
                    chunk = candidate
            if chunk:
                wrapped_lines.append(chunk)

        if not wrapped_lines:
            wrapped_lines = [" "]

        block_h = (2 * inner_pad_y) + (len(wrapped_lines) * line_h)
        if self.get_y() + block_h > self.page_break_trigger:
            self.add_page()

        y0 = self.get_y()
        self.set_fill_color(246, 248, 251)
        self.set_draw_color(185, 190, 198)
        self.rect(block_x, y0, block_w, block_h, style="FD")

        self.set_xy(block_x + inner_pad_x, y0 + inner_pad_y)
        for line in wrapped_lines:
            self.set_x(block_x + inner_pad_x)
            self.multi_cell(usable_w, line_h, line, border=0)

        self.set_xy(self.l_margin, y0 + block_h)
        self.ln(1.8)
        self._set_body_font()

    def add_image(self, image_path: Path, caption: str = "") -> None:
        if not image_path.exists():
            self._write_paragraph(f"[Missing image: {image_path}]")
            return

        self.ln(1)
        max_w = self._epw()
        max_h = 120.0

        try:
            self.image(str(image_path), x=self.l_margin, w=max_w)
        except RuntimeError:
            self.image(str(image_path), x=self.l_margin, w=max_w * 0.9)

        if caption:
            self.set_font("Helvetica", style="I", size=9)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 5.5, caption, align="C")
            self.set_text_color(0, 0, 0)
            self._set_body_font()

        if self.get_y() > self.page_break_trigger - max_h:
            self.add_page()
        self.ln(2)

    def add_table(self, rows: list[list[str]]) -> None:
        if not rows:
            return

        col_count = max(len(row) for row in rows)
        normalized = [row + [""] * (col_count - len(row)) for row in rows]
        max_lengths = []
        for col_index in range(col_count):
            col_max = max(len(row[col_index]) for row in normalized)
            max_lengths.append(max(col_max, 6))

        total_length = sum(max_lengths)
        widths = [(self._epw() * value / total_length) for value in max_lengths]
        line_h = 6.4

        for row_index, row in enumerate(normalized):
            table_font_size = 10
            self.set_font("Helvetica", style="B" if row_index == 0 else "", size=table_font_size)
            wrapped_cells = [self._wrap_text(cell, width - 2) for cell, width in zip(row, widths)]
            row_h = line_h * max(len(cell_lines) for cell_lines in wrapped_cells)

            if self.get_y() + row_h > self.page_break_trigger:
                self.add_page()

            x_start = self.l_margin
            y_start = self.get_y()
            for width, cell_lines in zip(widths, wrapped_cells):
                if row_index == 0:
                    self.set_fill_color(230, 236, 245)
                    self.rect(x_start, y_start, width, row_h, style="FD")
                else:
                    fill = (248, 249, 251) if row_index % 2 == 1 else (255, 255, 255)
                    self.set_fill_color(*fill)
                    self.rect(x_start, y_start, width, row_h, style="FD")
                self.set_xy(x_start + 1, y_start + 0.8)
                self.multi_cell(width - 2, line_h, "\n".join(cell_lines), border=0)
                x_start += width

            self.set_xy(self.l_margin, y_start + row_h)

        self.ln(2)
        self._set_body_font()


def render_markdown_to_pdf(pdf: MarkdownPDF, md_text: str, base_dir: Path) -> None:
    lines = md_text.splitlines()
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            index += 1
            code_lines: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(sanitize_text(lines[index].rstrip()))
                index += 1
            pdf.add_code_block(code_lines)
            index += 1
            continue

        image_match = re.match(r"^!\[([^\]]*)\]\(([^\)]+)\)$", stripped)
        if image_match:
            caption = sanitize_text(image_match.group(1).strip())
            rel_path = image_match.group(2).strip()
            resolved = (base_dir / rel_path).resolve()
            pdf.add_image(resolved, caption)
            index += 1
            continue

        if is_table_line(stripped):
            table_lines = [stripped]
            index += 1
            while index < len(lines) and is_table_line(lines[index].strip()):
                table_lines.append(lines[index].strip())
                index += 1

            rows = [parse_table_row(tline) for tline in table_lines if not is_table_separator(tline)]
            pdf.add_table(rows)
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            pdf.add_heading(len(heading_match.group(1)), sanitize_text(heading_match.group(2)))
            index += 1
            continue

        if stripped.startswith(">"):
            pdf.add_quote(sanitize_text(stripped.lstrip("> ")))
            index += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            pdf.add_rule()
            index += 1
            continue

        toc_link_match = re.match(r"^(\s*)[-*]\s+\[([^\]]+)\]\(#([^\)]+)\)\s*$", line)
        if toc_link_match:
            indent_ws = toc_link_match.group(1)
            label = sanitize_text(toc_link_match.group(2).strip())
            anchor = sanitize_text(toc_link_match.group(3).strip())
            indent_level = len(indent_ws.replace("\t", "    ")) // 4
            pdf.add_toc_link_item(label, anchor, indent_level)
            index += 1
            continue

        bullet_match = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if bullet_match:
            indent_ws = bullet_match.group(1)
            indent_level = len(indent_ws.replace("\t", "    ")) // 4
            pdf.add_bullet_item(sanitize_text(bullet_match.group(2)), indent_level)
            index += 1
            continue

        numbered_match = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if numbered_match:
            indent_ws = numbered_match.group(1)
            indent_level = len(indent_ws.replace("\t", "    ")) // 4
            pdf.add_numbered_item(numbered_match.group(2), sanitize_text(numbered_match.group(3)), indent_level)
            index += 1
            continue

        bold_line_match = re.match(r"^\*\*([^*].*?)\*\*$", stripped)
        if bold_line_match:
            pdf.add_heading(4, sanitize_text(bold_line_match.group(1)))
            index += 1
            continue

        labeled_match = re.match(r"^\*\*([^*]+?(?:[:.]))\*\*\s*(.*)$", stripped)
        if labeled_match:
            pdf.add_labeled_paragraph(sanitize_text(labeled_match.group(1)), sanitize_text(labeled_match.group(2)))
            index += 1
            continue

        paragraph_lines = [strip_inline_markdown(sanitize_text(stripped))]
        index += 1
        while index < len(lines):
            next_line = lines[index].strip()
            if (
                not next_line
                or next_line.startswith("```")
                or is_table_line(next_line)
                or re.match(r"^(#{1,6})\s+", next_line)
                or re.fullmatch(r"-{3,}|\*{3,}", next_line)
                or re.match(r"^[-*]\s+", next_line)
                or re.match(r"^(\d+)\.\s+", next_line)
            ):
                break
            paragraph_lines.append(strip_inline_markdown(sanitize_text(next_line)))
            index += 1

        pdf._write_paragraph(" ".join(part for part in paragraph_lines if part))


def md_to_pdf(md_path: Path) -> Path:
    if not md_path.exists():
        raise FileNotFoundError(f"Missing markdown file: {md_path}")

    md_text = md_path.read_text(encoding="utf-8")
    # Keep internal anchor links so TOC entries can be rendered as clickable links.
    md_text = sanitize_text(md_text)

    pdf = MarkdownPDF()
    render_markdown_to_pdf(pdf, md_text, md_path.parent)

    out_path = md_path.with_suffix(".pdf")
    pdf.output(str(out_path))
    return out_path


def main() -> int:
    files = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_FILES
    failures = 0

    for file_name in files:
        path = Path(file_name)
        try:
            out = md_to_pdf(path)
            print(f"OK: {out}")
        except Exception as exc:
            failures += 1
            print(f"FAIL: {path} -> {exc}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

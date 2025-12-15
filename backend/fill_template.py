# backend/fill_template.py

from docx import Document
from docx.shared import Inches
from docx.oxml import OxmlElement, ns
from backend.headings import normalize_heading
import re


def add_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")

    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(ns.qn("w:val"), "single")
        element.set(ns.qn("w:sz"), "8")
        element.set(ns.qn("w:space"), "0")
        element.set(ns.qn("w:color"), "000000")
        borders.append(element)

    tblPr.append(borders)


def normalize_header_cell(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)      # normalize spaces
    text = text.replace("sl no", "slno")
    text = text.replace("slno", "slno")
    return text.strip()


def table_header_key(table):
    """
    NORMALIZED header key so visually identical tables merge.
    """
    return tuple(normalize_header_cell(c) for c in table[0])


def merge_tables(tables):
    merged = {}

    for table in tables:
        header_key = table_header_key(table)
        header = table[0]
        rows = table[1:]

        if header_key not in merged:
            merged[header_key] = {
                "header": header,
                "rows": []
            }

        merged[header_key]["rows"].extend(rows)

    return merged.values()


def insert_after(paragraph, element):
    paragraph._p.addnext(
        element._p if hasattr(element, "_p") else element._tbl
    )


def fill_template(template_path, output_path, doc1, doc2):
    doc = Document(template_path)

    for para in doc.paragraphs:
        key = normalize_heading(para.text)
        if not key:
            continue

        cursor = para

        # -------- TECHNICAL ARTICLES (SPECIAL ORDER) --------
        if key == "TECHNICAL ARTICLES:":
            for src in (doc1, doc2):
                for img in src[key]["images"]:
                    p = doc.add_paragraph()
                    p.add_run().add_picture(img, width=Inches(4))
                    insert_after(cursor, p)
                    cursor = p

                for line in src[key]["text"]:
                    p = doc.add_paragraph(line)
                    insert_after(cursor, p)
                    cursor = p
            continue

        # -------- TEXT --------
        for src in (doc1, doc2):
            for line in src[key]["text"]:
                p = doc.add_paragraph(line)
                insert_after(cursor, p)
                cursor = p

        # -------- MERGED TABLES (FINAL, FIXED) --------
        all_tables = doc1[key]["tables"] + doc2[key]["tables"]
        merged_tables = merge_tables(all_tables)

        for t in merged_tables:
            header = t["header"]
            rows = t["rows"]

            table = doc.add_table(
                rows=1 + len(rows),
                cols=len(header)
            )

            # header
            for c, cell in enumerate(header):
                table.rows[0].cells[c].text = str(cell)

            # rows (doc1 first, then doc2)
            for r, row in enumerate(rows, start=1):
                for c, cell in enumerate(row):
                    table.rows[r].cells[c].text = str(cell or "")

            add_table_borders(table)
            cursor._p.addnext(table._tbl)

    doc.save(output_path)
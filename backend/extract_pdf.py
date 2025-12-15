# backend/extract_pdf.py

import os
import pdfplumber
from backend.headings import ALL_HEADINGS, normalize_heading


def detect_table_section(table):
    header = " ".join(str(c or "") for c in table[0]).lower()

    if "journal" in header:
        return "FACULTY PUBLICATIONS IN (NATIONAL / INTERNATIONAL) JOURNALS:"
    if "conference" in header:
        return "FACULTY PUBLICATIONS IN (NATIONAL / INTERNATIONAL) CONFERENCES:"
    if "funding agency" in header:
        return "FUNDED PROJECTS:"
    if "application" in header:
        return "PATENTS:"
    if "publication" in header:
        return "STUDENT PUBLICATIONS:"
    if "award" in header:
        return "STUDENT ACHIEVEMENTS:"
    if "placed" in header or "package" in header:
        return "PLACEMENT AND HIGHER STUDIES RECORD:"

    return None


def extract_pdf_to_sections(pdf_path, image_dir="temp_uploads/images"):
    os.makedirs(image_dir, exist_ok=True)

    sections = {
        h: {"text": [], "tables": [], "images": []}
        for h in ALL_HEADINGS
    }

    current_text_section = None
    image_count = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            # ---------------- TEXT ----------------
            page_text = page.extract_text() or ""
            for line in page_text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                heading = normalize_heading(line)
                if heading:
                    current_text_section = heading
                    continue

                # ✅ ONLY keep text for NON-TABLE sections
                if (
                    current_text_section
                    and current_text_section
                    not in (
                        "FACULTY PUBLICATIONS IN (NATIONAL / INTERNATIONAL) JOURNALS:",
                        "FACULTY PUBLICATIONS IN (NATIONAL / INTERNATIONAL) CONFERENCES:",
                        "FUNDED PROJECTS:",
                        "PATENTS:",
                        "STUDENT PUBLICATIONS:",
                        "STUDENT ACHIEVEMENTS:",
                        "PLACEMENT AND HIGHER STUDIES RECORD:",
                    )
                ):
                    sections[current_text_section]["text"].append(line)

            # ---------------- TABLES ----------------
            for table in page.extract_tables():
                if not table or not any(any(cell for cell in row) for row in table):
                    continue

                target_section = detect_table_section(table)
                if target_section:
                    sections[target_section]["tables"].append(table)

            # ---------------- IMAGES ----------------
            if current_text_section and "image" in page.objects:
                for img in page.objects["image"]:
                    try:
                        image_count += 1
                        img_path = os.path.join(
                            image_dir,
                            f"{os.path.basename(pdf_path)}_img_{image_count}.png"
                        )
                        with open(img_path, "wb") as f:
                            f.write(img["stream"].get_data())
                        sections[current_text_section]["images"].append(img_path)
                    except Exception:
                        pass

    return sections
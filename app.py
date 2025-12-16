# app.py

import streamlit as st
import os

from backend.extract_pdf import extract_pdf_to_sections
from backend.fill_template import fill_template
from backend.ai_technical_article import generate_ai_technical_article

st.set_page_config(
    page_title="Magazine Generator",
    layout="centered"
)

st.title("AutoMag")
st.write(
    "Upload the magazine template and two content PDFs to generate the final magazine."
)

# ---------------- UPLOADS ----------------
template_file = st.file_uploader(
    "Upload Magazine Template (.docx)",
    type=["docx"]
)

pdf_files = st.file_uploader(
    "Upload Content PDFs (doc1 and doc2)",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- VALIDATION ----------------
if template_file and pdf_files and len(pdf_files) == 2:

    st.success("Files uploaded successfully. Ready to generate.")

    if st.button("Generate Magazine"):

        with st.spinner("Processing PDFs and generating magazine..."):

            os.makedirs("temp_uploads", exist_ok=True)
            os.makedirs("outputs", exist_ok=True)

            # Save template
            template_path = "temp_uploads/template.docx"
            with open(template_path, "wb") as f:
                f.write(template_file.read())

            # Save PDFs
            pdf_paths = []
            for pdf in pdf_files:
                path = f"temp_uploads/{pdf.name}"
                with open(path, "wb") as f:
                    f.write(pdf.read())
                pdf_paths.append(path)

            # Ensure order
            pdf_paths.sort()

            # ---------------- BACKEND EXTRACTION ----------------
            doc1 = extract_pdf_to_sections(
                pdf_paths[0],
                "temp_uploads/doc1_images"
            )
            doc2 = extract_pdf_to_sections(
                pdf_paths[1],
                "temp_uploads/doc2_images"
            )

            # ---------------- AI TECHNICAL ARTICLE (OVERRIDE) ----------------
            ai_article = generate_ai_technical_article()

            doc1["TECHNICAL ARTICLES:"] = ai_article
            doc2["TECHNICAL ARTICLES:"] = {
                "text": [],
                "tables": [],
                "images": []
            }

            # ---------------- FINAL DOC GENERATION ----------------
            output_path = "outputs/final_magazine.docx"

            fill_template(
                template_path,
                output_path,
                doc1,
                doc2
            )

        st.success("✅ Magazine generated successfully!")

        with open(output_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Final Magazine",
                data=f,
                file_name="final_magazine.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

else:
    st.info(
        "Please upload **1 DOCX template** and **exactly 2 PDF files** to continue."
    )

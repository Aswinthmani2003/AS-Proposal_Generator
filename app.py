import streamlit as st
from docx import Document
from datetime import datetime
import os
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
import uuid
import tempfile

# Define the list of available proposals
proposals = [
    "AI Automations & Landing Page Website Proposal",
    "Multivendor Musician Platform Proposal",
    "Tech Consultation Proposal",
    "Web based AI Fintech App Proposal",
    "Website Update - Consultation Proposal",
    "Business Automations Proposal",
    "Marketing Proposal"
]

def apply_formatting(run, font_name, font_size, bold=False):
    """Apply formatting to runs"""
    if font_name:
        run.font.name = font_name
        run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    if font_size:
        run.font.size = Pt(font_size)
    if bold is not None:
        run.bold = bold

def replace_and_format(doc, placeholders, font_name=None, font_size=None):
    """Replace placeholders while preserving formatting"""
    for para in doc.paragraphs:
        full_text = para.text
        for key, value in placeholders.items():
            full_text = full_text.replace(key, value)
        
        if full_text != para.text:
            runs = para.runs
            para.clear()
            para.add_run(full_text)
            
            if runs:
                for new_run in para.runs:
                    new_run.font.name = runs[0].font.name
                    new_run.bold = runs[0].bold
                    new_run.italic = runs[0].italic
                    if font_size:
                        new_run.font.size = Pt(font_size)

    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    original_text = para.text
                    new_text = original_text
                    for key, value in placeholders.items():
                        new_text = new_text.replace(key, value)
                    
                    if new_text != original_text:
                        runs = para.runs
                        para.clear()
                        new_run = para.add_run(new_text)
                        
                        if runs:
                            new_run.font.name = runs[0].font.name
                            new_run.bold = runs[0].bold
                            new_run.italic = runs[0].italic
                            if font_size:
                                new_run.font.size = Pt(font_size)
                        
                        if "<<Address>>" in original_text:
                            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        else:
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    
    return doc

def apply_image_placeholder(doc, placeholder_key, image_file):
    """Replace placeholder with image"""
    try:
        for para in doc.paragraphs:
            if placeholder_key in para.text:
                para.clear()
                run = para.add_run()
                run.add_picture(image_file, width=Inches(1.2), height=Inches(0.75))
                return doc

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if placeholder_key in para.text:
                            para.clear()
                            run = para.add_run()
                            run.add_picture(image_file, width=Inches(1.5), height=Inches(0.75))
                            return doc

        st.warning(f"Signature placeholder '{placeholder_key}' not found")
        return doc

    except Exception as e:
        st.error(f"Error inserting image: {e}")
        return doc

def generate_document():
    st.title("Proposal Generator")
    
    # Path setup for Streamlit Cloud
    base_dir = os.path.join(os.getcwd(), "templates")
    
    # Template mapping
    proposal_templates = {
        "AI Automations & Landing Page Website Proposal": "AI Automations Proposal.docx",
        "Multivendor Musician Platform Proposal": "Multivendor Musician Platform.docx",
        "Tech Consultation Proposal": "Tech Consultation Proposal.docx",
        "Web based AI Fintech App Proposal": "Web based AI Fintech App.docx",
        "Website Update - Consultation Proposal": "Website Update - Consultation Proposal.docx",
        "Business Automations Proposal": "Business Automations Proposal.docx",
        "Marketing Proposal": "Marketing Proposal.docx"
    }

    selected_proposal = st.selectbox("Select Proposal", proposals)
    template_path = os.path.join(base_dir, proposal_templates[selected_proposal])

    if not os.path.exists(template_path):
        st.error("Template file not found!")
        return

    # Client inputs
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name:")
        client_email = st.text_input("Client Email:")
    with col2:
        client_number = st.text_input("Client Number:")
        if selected_proposal not in ["Business Automations Proposal", "Marketing Proposal"]:
            country = st.text_input("Country:")
        else:
            country = ""

    if selected_proposal in ["Business Automations Proposal", "Marketing Proposal"]:
        client_designation = st.text_input("Client Designation:")
    else:
        client_designation = ""

    date_field = st.date_input("Date:", datetime.today())
    signature_file = st.file_uploader("Upload Signature (PNG/JPEG)", ["png", "jpg", "jpeg"])

    # Placeholder mapping
    placeholders = {
        "<<Client Name>>": client_name,
        "<<Client Email>>": client_email,
        "<<Client Number>>": client_number,
        "<<Date>>": date_field.strftime("%d-%m-%Y"),
        "<<Signature>>": "<<Signature>>",
    }

    # Conditional placeholders
    if selected_proposal not in ["Business Automations Proposal", "Marketing Proposal"]:
        placeholders["<<Country>>"] = country
        
    if selected_proposal in ["Business Automations Proposal", "Marketing Proposal"]:
        placeholders["<<Designation>>"] = client_designation

    # Team details
    if selected_proposal not in ["Business Automations Proposal", "Marketing Proposal"]:
        team_details = get_team_details()
        placeholders.update(team_details)

    if st.button("Generate Proposal"):
        try:
            formatted_date = date_field.strftime("%d %b %Y")
            unique_id = str(uuid.uuid4())[:8]
            doc_filename = f"Proposal_{client_name}_{formatted_date}_{unique_id}.docx"

            with tempfile.TemporaryDirectory() as temp_dir:
                doc = Document(template_path)
                doc = replace_and_format(doc, placeholders, "Times New Roman", 12)

                if signature_file:
                    signature_path = os.path.join(temp_dir, "signature.png")
                    with open(signature_path, "wb") as f:
                        f.write(signature_file.getbuffer())
                    doc = apply_image_placeholder(doc, "<<Signature>>", signature_path)

                doc_path = os.path.join(temp_dir, doc_filename)
                doc.save(doc_path)

                with open(doc_path, "rb") as f:
                    doc_bytes = f.read()

                st.session_state['doc_bytes'] = doc_bytes
                st.session_state['filename'] = doc_filename
                st.success("Proposal generated! Download below ↓")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Download button
    if 'doc_bytes' in st.session_state:
        st.download_button(
            label="Download Word Document",
            data=st.session_state['doc_bytes'],
            file_name=st.session_state['filename'],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

def get_team_details():
    """Collect team composition"""
    st.subheader("Team Composition")
    team_roles = {
        "Project Manager": "<<P1>>",
        "Business Analyst": "<<B1>>",
        "UI/UX Members": "<<U1>>",
        "Backend Developers": "<<BD1>>",
        "Frontend Developers": "<<F1>>",
        "AI/ML Developers": "<<A1>>",
        "System Architect": "<<S1>>",
        "AWS Developer": "<<AD1>>"
    }

    team_details = {}
    cols = st.columns(2)
    
    for idx, (role, placeholder) in enumerate(team_roles.items()):
        with cols[idx % 2]:
            count = st.number_input(
                f"{role} Count:", 
                min_value=0, 
                step=1, 
                key=f"team_{placeholder}"
            )
            team_details[placeholder] = str(count)

    return team_details

def main():
    generate_document()

if __name__ == "__main__":
    main()
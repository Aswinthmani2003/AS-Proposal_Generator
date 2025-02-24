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

# Updated list of available proposals (Tech Consultation Proposal removed)
proposals = [
    "AI Automations Proposal",
    "Landing Page Website Proposal",
    "Marketing Proposal",
    "Multivendor Musician Platform Proposal",
    "Web based AI Fintech App Proposal",
    "Website Update - Consultation Proposal"
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

def replace_and_format(doc, placeholders):
    """Replace placeholders while preserving formatting including color"""
    for para in doc.paragraphs:
        original_runs = para.runs.copy()
        full_text = para.text
        
        # Replace placeholders
        for key, value in placeholders.items():
            full_text = full_text.replace(key, value)
        
        if full_text != para.text:
            para.clear()
            new_run = para.add_run(full_text)
            
            if original_runs:
                original_run = next((r for r in original_runs if r.text), original_runs[0])
                
                # Ensure run properties exist
                rPr = new_run._element.get_or_add_rPr()
                
                # Copy font properties safely
                if original_run.font.name:
                    new_run.font.name = original_run.font.name
                    if hasattr(original_run.font, '_element'):
                        rFonts = rPr.rFonts
                        if rFonts is None:
                            rFonts = rPr.add_rFonts()
                        rFonts.set(qn('w:eastAsia'), original_run.font.name)
                
                # Copy color if exists
                if original_run.font.color.rgb:
                    new_run.font.color.rgb = original_run.font.color.rgb
                
                # Handle font size
                if original_run.font.size:
                    new_run.font.size = original_run.font.size

                # Copy other properties
                new_run.bold = original_run.bold
                new_run.italic = original_run.italic

    # Process tables with similar logic
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    original_runs = para.runs
                    full_text = para.text
                    
                    for key, value in placeholders.items():
                        full_text = full_text.replace(key, value)
                    
                    if full_text != para.text:
                        para.clear()
                        new_run = para.add_run(full_text)
                        
                        if original_runs:
                            original_run = next((r for r in original_runs if r.text), original_runs[0])
                            
                            new_run.font.name = original_run.font.name
                            new_run._element.rPr.rFonts.set(qn('w:eastAsia'), original_run.font.name)
                            new_run.font.bold = original_run.font.bold
                            new_run.font.italic = original_run.font.italic
                            
                            if original_run.font.color.rgb:
                                new_run.font.color.rgb = original_run.font.color.rgb
                            
                            if original_run.font.size:
                                new_run.font.size = original_run.font.size

                        # Preserve cell alignment
                        if "<<Address>>" in para.text:
                            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        else:
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER

                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    
    return doc

def generate_document():
    st.title("Proposal Generator")
    base_dir = os.path.join(os.getcwd(), "templates")

    # Updated proposal templates (Tech Consultation Proposal removed)
    proposal_templates = {
        "AI Automations Proposal": "AI Automations Proposal.docx",
        "Landing Page Website Proposal": "Landing Page Website Proposal.docx",
        "Marketing Proposal": "Marketing Proposal.docx",
        "Multivendor Musician Platform Proposal": "Multivendor Musician Platform.docx",
        "Web based AI Fintech App Proposal": "Web based AI Fintech App.docx",
        "Website Update - Consultation Proposal": "Website Update - Consultation Proposal.docx"
    }

    selected_proposal = st.selectbox("Select Proposal", proposals)
    template_path = os.path.join(base_dir, proposal_templates[selected_proposal])

    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name:")
        client_email = st.text_input("Client Email:")
    with col2:
        client_number = st.text_input("Client Number:")
        country = st.text_input("Country:")

    date_field = st.date_input("Date:", datetime.today())

    placeholders = {
        "<<Client Name>>": client_name,
        "<<Client Email>>": client_email,
        "<<Client Number>>": client_number,
        "<<Date>>": date_field.strftime("%d-%m-%Y"),
        "<<Country>>": country
    }

    # Get team details based on proposal type
    if selected_proposal == "Marketing Proposal":
        team_details = get_marketing_team_details()
    else:
        team_details = get_general_team_details()
    
    placeholders.update(team_details)

    if st.button("Generate Proposal"):
        formatted_date = date_field.strftime("%d %b %Y")
        unique_id = str(uuid.uuid4())[:8]
        doc_filename = f"Proposal_{client_name}_{formatted_date}_{unique_id}.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            doc = Document(template_path)
            doc = replace_and_format(doc, placeholders)

            doc_path = os.path.join(temp_dir, doc_filename)
            doc.save(doc_path)

            with open(doc_path, "rb") as f:
                st.download_button("Download Proposal", f, doc_filename)

            st.success("Proposal generated!")

def get_general_team_details():
    """Collect team composition for non-marketing proposals"""
    st.subheader("Team Composition")
    team_roles = {
        "Project Manager": "<<P1>>",
        "Frontend Developers": "<<F1>>",
        "Business Analyst": "<<B1>>",
        "AI/ML Developers": "<<A1>>",
        "UI/UX Members": "<<U1>>",
        "System Architect": "<<S1>>",
        "Backend Developers": "<<BD1>>",
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

def get_marketing_team_details():
    """Collect marketing-specific team composition"""
    st.subheader("Team Composition")
    team_roles = {
        "Digital Marketing Executive": "<<F1>>",
        "Project Manager": "<<P1>>",
        "Business Analyst": "<<B1>>",
        "UI/UX Members": "<<U1>>"
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

if __name__ == "__main__":
    generate_document()
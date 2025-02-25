import streamlit as st
from docx import Document
from datetime import datetime
import os
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
import uuid
import tempfile

# Proposal configurations
PROPOSAL_CONFIG = {
    "AI Automations Proposal": {
        "template": "AI Automations Proposal.docx",
        "pricing_fields": [
            ("Landing Page Website", "L-Price"),
            ("Admin Panel", "A-Price"),
            ("CRM Automations", "C-Price"),
            ("ManyChat & Make Automation", "M-Price"),
            ("Social Media Automation", "S-Price"), 
            ("AI Calling", "AI-Price"),
            ("Total Amount", "T-Price"),
            ("Annual Maintenance", "AM-Price"),
            ("Additional Features & Enhancements", "AF-Price")
        ],
        "team_type": "general",
        "special_fields": []
    },
    "Business Automations Proposal": {
        "template": "Business Automations Proposal.docx",
        "pricing_fields": [
            ("Week 1 Work Description", "Description"),
            ("Week 1 Price", "week1 price"),
            ("AI Automations (6 scenarios)", "ai auto price"),
            ("WhatsApp Automation + Setup", "whts price"),
            ("CRM Setup", "crm price"),
            ("Email Marketing Setup", "email price"),
            ("Make/Zapier Automation", "make price"),
            ("Firefly Meeting Automation", "firefly price"),
            ("AI Chatbot", "chatbot price"),
            ("PDF Generation Automations", "pdf gen pr"),
            ("Social Media Content", "ai mdl price"),
            ("Custom AI Models", "cstm ai price"),
            ("Additional Features & Enhancements", "AF-Price")
        ],
        "team_type": None,
        "special_fields": [
            ("mutually_agreed_points", "{"),
            ("Designation", "<<"),
            ("validity_date", "{")
        ]
    },
    "Marketing Proposal": {
        "template": "Marketing Proposal.docx",
        "pricing_fields": [
            ("Marketing Strategy", "Market"),
            ("Social Media & Ad Account", "Social"),
            ("Creative Posts (10/month)", "Creative"),
            ("Paid Ads (Meta+Google)", "Ads"),
            ("SEO Services", "SEO"),
            ("Organic Marketing", "Organic"),
            ("GST Percentage", "GST"),
            ("Instalment 1 Amount", "Inst1"),
            ("Instalment 2 Amount", "Inst2")
        ],
        "team_type": "marketing",
        "special_fields": [
            ("validity_date", "{")
        ]
    },
    "AI Automation Proposal without LPW": {
        "template": "Landing Page Website Proposal.docx",
        "pricing_fields": [
            ("CRM Automations", "C-Price"),
            ("ManyChat & Make Automation", "M-Price"),
            ("Social Media Automation", "S-Price"),
            ("AI Calling", "AI-Price"),
            ("Total Amount", "T-Price"),
            ("Annual Maintenance", "AM-Price"),
            ("Additional Features & Enhancements", "AF-Price")
        ],
        "team_type": "general",
        "special_fields": []
    }
}

def apply_formatting(new_run, original_run):
    """Copy formatting from original run to new run"""
    if original_run.font.name:
        new_run.font.name = original_run.font.name
        new_run._element.rPr.rFonts.set(qn('w:eastAsia'), original_run.font.name)
    if original_run.font.size:
        new_run.font.size = original_run.font.size
    if original_run.font.color.rgb:
        new_run.font.color.rgb = original_run.font.color.rgb
    new_run.bold = original_run.bold
    new_run.italic = original_run.italic

def replace_in_paragraph(para, placeholders):
    """Handle paragraph replacements preserving formatting"""
    original_runs = para.runs.copy()
    full_text = para.text
    
    for ph, value in placeholders.items():
        full_text = full_text.replace(ph, str(value))
    
    if full_text != para.text:
        para.clear()
        new_run = para.add_run(full_text)
        if original_runs:
            original_run = next((r for r in original_runs if r.text), None)
            if original_run:
                apply_formatting(new_run, original_run)

def replace_and_format(doc, placeholders):
    """Enhanced replacement with table cell handling"""
    # Process paragraphs
    for para in doc.paragraphs:
        replace_in_paragraph(para, placeholders)

    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.tables:
                    for nested_table in cell.tables:
                        for nested_row in nested_table.rows:
                            for nested_cell in nested_row.cells:
                                for para in nested_cell.paragraphs:
                                    replace_in_paragraph(para, placeholders)
                else:
                    for para in cell.paragraphs:
                        replace_in_paragraph(para, placeholders)
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    return doc

def get_general_team_details():
    """Collect team composition for non-marketing proposals"""
    st.subheader("Team Composition")
    team_roles = {
        "Project Manager": "P1",
        "Frontend Developers": "F1",
        "Business Analyst": "B1", 
        "AI/ML Developers": "A1",
        "UI/UX Members": "U1",
        "System Architect": "S1",
        "Backend Developers": "BD1",
        "AWS Developer": "AD1"
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
            team_details[f"<<{placeholder}>>"] = str(count)

    return team_details

def get_marketing_team_details():
    """Collect marketing-specific team composition"""
    st.subheader("Team Composition")
    team_roles = {
        "Digital Marketing Executive": "F1",
        "Project Manager": "P1",
        "Business Analyst": "B1",
        "UI/UX Members": "U1"
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
            team_details[f"<<{placeholder}>>"] = str(count)

    return team_details

def generate_document():
    st.title("Proposal Generator")
    base_dir = os.path.join(os.getcwd(), "templates")

    selected_proposal = st.selectbox("Select Proposal", list(PROPOSAL_CONFIG.keys()))
    config = PROPOSAL_CONFIG[selected_proposal]
    template_path = os.path.join(base_dir, config["template"])

    # Client Information
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name:")
        client_email = st.text_input("Client Email:")
    with col2:
        client_number = st.text_input("Client Number:")
        country = st.text_input("Country:")

    date_field = st.date_input("Date:", datetime.today())
    
    # Currency Handling
    currency = st.selectbox("Select Currency", ["USD", "INR"])
    currency_symbol = "$" if currency == "USD" else "₹"

    # Special Fields Handling
    special_data = {}
    if config.get("special_fields"):
        st.subheader("Additional Details")
        for field, wrapper in config["special_fields"]:
            if wrapper == "{":
                placeholder = f"{{{field}}}"
                if field == "validity_date":
                    validity_date = st.date_input("Proposal Validity Until:")
                    special_data[placeholder] = validity_date.strftime("%d-%m-%Y")
                else:
                    special_data[placeholder] = st.text_input(f"{field.replace('_', ' ').title()}:")
            else:
                placeholder = f"<<{field}>>"
                special_data[placeholder] = st.text_input(f"{field.replace('_', ' ').title()}:")

    # Pricing Section
    st.subheader("Pricing Details")
    pricing_data = {}
    numerical_values = {}  # To store raw numerical values for calculations
    cols = st.columns(2)
    for idx, (label, key) in enumerate(config["pricing_fields"]):
        with cols[idx % 2]:
            if key == "GST":
                # Handle GST as percentage input
                value = st.number_input(
                    f"{label} (%)",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    format="%.1f",
                    key=f"price_{key}"
                )
                numerical_values[key] = value
                pricing_data[f"<<{key}>>"] = f"{value}%"
            else:
                value = st.number_input(
                    f"{label} ({currency})",
                    min_value=0,
                    value=0,
                    step=100,
                    format="%d",
                    key=f"price_{key}"
                )
                numerical_values[key] = value
                pricing_data[f"<<{key}>>"] = f"{currency_symbol}{value}"

    # Calculate Total and Final Amount for Marketing Proposal
    if selected_proposal == "Marketing Proposal":
        total = sum([
            numerical_values.get("Market", 0),
            numerical_values.get("Social", 0),
            numerical_values.get("Creative", 0),
            numerical_values.get("Ads", 0),
            numerical_values.get("SEO", 0),
            numerical_values.get("Organic", 0)
        ])
        gst_percentage = numerical_values.get("GST", 0)
        gst_amount = total * (gst_percentage / 100)
        final_amt = total + gst_amount

        pricing_data["<<Total>>"] = f"{currency_symbol}{total}"
        pricing_data["<<Final Amt>>"] = f"{currency_symbol}{final_amt}"

    # Team Composition
    team_data = {}
    if config["team_type"] == "marketing":
        team_data = get_marketing_team_details()
    elif config["team_type"] == "general":
        team_data = get_general_team_details()

    # Combine all placeholders
    placeholders = {
        "<<Client Name>>": client_name,
        "<<Client Email>>": client_email,
        "<<Client Number>>": client_number,
        "<<Date>>": date_field.strftime("%d-%m-%Y"),
        "<<Country>>": country
    }
    placeholders.update(pricing_data)
    placeholders.update(team_data)
    placeholders.update(special_data)

    if st.button("Generate Proposal"):
        formatted_date = date_field.strftime("%d %b %Y")
        unique_id = str(uuid.uuid4())[:8]
        doc_filename = f"{selected_proposal}_{client_name}_{formatted_date}_{unique_id}.docx"

        with tempfile.TemporaryDirectory() as temp_dir:
            doc = Document(template_path)
            doc = replace_and_format(doc, placeholders)

            doc_path = os.path.join(temp_dir, doc_filename)
            doc.save(doc_path)

            with open(doc_path, "rb") as f:
                st.download_button("Download Proposal", f, doc_filename)

            st.success("Proposal generated successfully!")

if __name__ == "__main__":
    generate_document()

import re
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from fpdf import FPDF

def extract_text_from_pdf(pdf_file):
    pdf_file.seek(0)
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_cv_content(text):
    """
    Analyze the resume text for professionalism and certifications.
    Returns professionalism score, list of certificates, and suggestions.
    """

    professionalism_score = 0
    suggestions = []
    found_certifications = []

    # 1. Check for professional sections
    sections = ['objective', 'summary', 'experience', 'education', 'skills', 'certifications']
    for section in sections:
        if section.lower() in text.lower():
            professionalism_score += 1
        else:
            suggestions.append(f"Missing section: {section.capitalize()}")

    # 2. Check for use of action words
    action_words = ['led', 'developed', 'created', 'managed', 'analyzed', 'designed', 'improved']
    if any(word in text.lower() for word in action_words):
        professionalism_score += 1
    else:
        suggestions.append("Add action words like 'managed', 'developed', etc.")

    # 3. Detect known certifications (can be expanded)
    known_certs = [
        'AWS', 'Azure', 'Google Cloud', 'PMP', 'Scrum Master', 'Coursera', 'Udemy',
        'Microsoft Certified', 'Cisco', 'CompTIA', 'Oracle', 'HubSpot', 'IBM'
    ]
    for cert in known_certs:
        pattern = re.compile(re.escape(cert), re.IGNORECASE)
        if re.search(pattern, text):
            found_certifications.append(cert)

    if found_certifications:
        professionalism_score += 1
    else:
        suggestions.append("Add relevant certifications to strengthen your resume.")

    # Cap the score to 10
    professionalism_score = min(professionalism_score, 10)
    return {
        "professionalism_score": professionalism_score,
        "certifications": list(set(found_certifications)),
        "suggestions": suggestions
    }
import os
from fpdf import FPDF

def generate_pdf_report(filename, score, matched_keywords, preview_text, output_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(0, 10, f"ATS Report for: {filename}", ln=True, align='L')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Match Score: {score}%", ln=True)
    pdf.cell(0, 10, f"Matched Keywords: {', '.join(matched_keywords)}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Preview of Resume Text:", ln=True)
    pdf.set_font("Arial", size=10)
    for line in preview_text.split('\n'):
        pdf.multi_cell(0, 8, line)

    pdf.output(output_path)  # Save PDF to file

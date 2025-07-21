from django.shortcuts import render
from .forms import ResumeUploadForm
import fitz  # PyMuPDF
from fpdf import FPDF
from django.http import HttpResponse
import os
from django.conf import settings
from .utils import extract_text_from_pdf, analyze_cv_content  # generate_pdf_report hata diya, views.py mein define karenge

def generate_pdf_report(filename, score, matched_keywords, preview_text, professionalism_score=None, certifications=None, suggestions=None, output_path=None):
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

    if isinstance(preview_text, list):
        preview_text = "\n".join(preview_text)

    for line in preview_text.split('\n'):
        pdf.multi_cell(0, 8, line)

    if professionalism_score is not None:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Professionalism Score:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, str(professionalism_score))

    if certifications:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Certifications:", ln=True)
        pdf.set_font("Arial", size=10)
        if isinstance(certifications, list):
            certifications = ", ".join(certifications)
        pdf.multi_cell(0, 8, certifications)

    if suggestions:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Suggestions:", ln=True)
        pdf.set_font("Arial", size=10)
        if isinstance(suggestions, list):
            suggestions = "\n".join(suggestions)
        pdf.multi_cell(0, 8, suggestions)

    if output_path:
        pdf.output(output_path)
        return output_path
    else:
        return pdf.output(dest='S').encode('latin-1')


def upload_resume(request):
    results = []

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)

            files = request.FILES.getlist('resumes')
            job_keywords = ['python', 'django', 'communication', 'teamwork', 'sql', 'api', 'debugging']

            for f in files:
                text = extract_text_from_pdf(f)
                matched_keywords = [kw for kw in job_keywords if kw.lower() in text.lower()]
                score = round((len(matched_keywords) / len(job_keywords)) * 100, 2) if job_keywords else 0

                analysis = analyze_cv_content(text)

                pdf_filename = f"{f.name}_report.pdf"
                pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)

                pdf_bytes = generate_pdf_report(
                    filename=f.name,
                    score=score,
                    matched_keywords=matched_keywords,
                    preview_text=text[:300],
                    professionalism_score=analysis.get("professionalism_score"),
                    certifications=analysis.get("certifications"),
                    suggestions=analysis.get("suggestions")
                )

                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_bytes)

                results.append({
                    'filename': f.name,
                    'score': score,
                    'keywords': matched_keywords,
                    'text': text[:1000],
                    'professionalism_score': analysis.get("professionalism_score"),
                    'certifications': analysis.get("certifications"),
                    'suggestions': analysis.get("suggestions"),
                    'download_link': f"/media/{pdf_filename}"
                })
    else:
        form = ResumeUploadForm()

    return render(request, 'upload.html', {'form': form, 'results': results})


def generate_txt_report(filename, score, matched_keywords, preview_text):
    report_content = f"""
ATS Report for: {filename}
----------------------------------------
Match Score: {score}%
Matched Keywords: {', '.join(matched_keywords)}

Preview of Resume Text:
----------------------------------------
{preview_text}

"""
    return report_content


def download_report(request):
    filename = request.GET.get('filename')
    score = request.GET.get('score')
    matched = request.GET.get('matched')
    preview = request.GET.get('preview')

    if not filename:
        return HttpResponse("Missing filename", status=400)

    matched_keywords = matched.split(',') if matched else []

    report_text = generate_txt_report(filename, score, matched_keywords, preview)

    response = HttpResponse(report_text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}_ATS_report.txt"'
    return response


def download_pdf_report(request):
    filename = request.GET.get('filename')
    score = request.GET.get('score')
    matched = request.GET.get('matched')
    preview = request.GET.get('preview')

    if not filename:
        return HttpResponse("Missing filename", status=400)

    matched_keywords = matched.split(',') if matched else []

    pdf_bytes = generate_pdf_report(filename, score, matched_keywords, preview)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}_ATS_report.pdf"'
    return response

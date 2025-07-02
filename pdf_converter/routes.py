from flask import Blueprint, render_template, request, send_file, flash
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import os
import uuid

pdf_bp = Blueprint('pdf', __name__,
                   template_folder='templates',
                   static_folder='static',
                   static_url_path='/pdf/static')

@pdf_bp.route('/', methods=['GET', 'POST'])
def pdf_home():
    if request.method == 'POST':
        if 'text_content' in request.form:
            text = request.form['text_content']
            if text.strip():
                pdf_bytes = text_to_pdf(text)
                return send_file(pdf_bytes, download_name='text.pdf', as_attachment=True)
            else:
                flash("Please enter some text.", "error")
        elif 'file_upload' in request.files:
            files = request.files.getlist('file_upload')
            valid_images = [f for f in files if f and allowed_file(f.filename)]
            if valid_images:
                pdf_bytes = images_to_pdf(valid_images)
                return send_file(pdf_bytes, download_name='images.pdf', as_attachment=True)
            else:
                flash("No valid images uploaded.", "error")
    return render_template('pdf/index.html')


# Utility functions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def text_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=1)
    return BytesIO(pdf.output(dest='S').encode('latin1'))

def images_to_pdf(files):
    temp_files = []
    pdf = None

    for file in files:
        if file and allowed_file(file.filename):
            img = Image.open(file.stream).convert("RGB")
            width, height = img.size
            width_mm = width * 0.264583
            height_mm = height * 0.264583

            if pdf is None:
                pdf = FPDF(unit="mm", format=(width_mm, height_mm))

            pdf.add_page()
            pdf.w = width_mm
            pdf.h = height_mm

            temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
            img.save(temp_filename, format='JPEG')
            temp_files.append(temp_filename)

            pdf.image(temp_filename, x=0, y=0, w=width_mm, h=height_mm)

    pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin1'))

    for tf in temp_files:
        if os.path.exists(tf):
            os.remove(tf)

    return pdf_bytes

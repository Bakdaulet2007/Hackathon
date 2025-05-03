

# AIzaSyAhlYLJRhT7Cyh_ViBq5ppT89xN_9-fNgo
from flask import Flask, request, render_template, send_from_directory, url_for
import os
import google.generativeai as genai
import pdfplumber
from docx import Document

genai.configure(api_key="AIzaSyAhlYLJRhT7Cyh_ViBq5ppT89xN_9-fNgo")

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text(path, ext):
    if ext == '.pdf':
        text = ''
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text
    elif ext == '.docx':
        doc = Document(path)
        return '\n'.join(p.text for p in doc.paragraphs)
    else:
        return ''

def get_summary(text):
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    prompt = f"""
Напиши структурированный конспект по следующей лекции. 
1) Разбей на разделы с заголовками. 
2) В каждом разделе выдели ключевые идеи маркерами (bullet points).
3) Дай краткие определения важных терминов.
4) Добавь пример(ы), если нужно для понимания.
Текст лекции:
{text}
"""
    response = model.generate_content([prompt])
    return response.text


def save_summary_docx(summary, original_name):
    doc = Document()
    doc.add_heading('Конспект', level=1)
    for line in summary.split('\n'):
        doc.add_paragraph(line)
    fname = f"{os.path.splitext(original_name)[0]}_summary.docx"
    out_path = os.path.join(UPLOAD_FOLDER, fname)
    doc.save(out_path)
    return fname

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file or file.filename == '':
        return "Файл не выбран", 400

    orig_name = file.filename
    ext = os.path.splitext(orig_name)[1].lower()
    if ext not in ('.pdf', '.docx'):
        return "Только PDF или DOCX поддерживаются", 400

    file_path = os.path.join(UPLOAD_FOLDER, orig_name)
    file.save(file_path)

    text = extract_text(file_path, ext)
    summary = get_summary(text)
    summary_fname = save_summary_docx(summary, orig_name)

    download_url = url_for('download_file', filename=summary_fname)
    return f"""
      <h2>Конспект готов!</h2>
      <a href="{download_url}">Скачать конспект (.docx)</a>
    """

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

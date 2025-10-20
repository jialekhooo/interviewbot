import tempfile
from fastapi import UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from docx import Document

def parse_pdf(file_path: str) -> str:
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if not text:
            raise ValueError("No text could be extracted from the PDF.")
        return text
    except Exception as e:
        raise Exception(f"PDF parsing failed: {str(e)}")


def parse_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if not text:
            raise ValueError("No text found in the DOCX file.")
        return text
    except Exception as e:
        raise Exception(f"DOCX parsing failed: {str(e)}")

def parser(file: UploadFile = File(...)):
    # Ensure file has valid content
    if file.content_type not in ["application/pdf",
                                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a .pdf or .docx file.")

    # Save uploaded file temporarily
    try:
        suffix = ".pdf" if file.filename.endswith(".pdf") else ".docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            contents = file.file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        # Determine file type and parse accordingly
        if suffix == ".pdf":
            return parse_pdf(temp_file_path)
        elif suffix == ".docx":
            return parse_docx(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")


    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Error during file processing: {str(e)}")

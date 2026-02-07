from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF
from docx import Document
import io

async def extract_text(file: UploadFile) -> str:
    """
    Extract text from uploaded file (PDF, DOCX, or TXT)
    
    Args:
        file: Uploaded file object
        
    Returns:
        Extracted text as string
        
    Raises:
        HTTPException: If file type is unsupported or extraction fails
    """
    try:
        # Get file extension
        filename = file.filename.lower()
        content = await file.read()
        
        # PDF processing
        if filename.endswith('.pdf'):
            return _extract_from_pdf(content)
        
        # DOCX processing
        elif filename.endswith('.docx'):
            return _extract_from_docx(content)
        
        # TXT processing
        elif filename.endswith('.txt'):
            return _extract_from_txt(content)
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, DOCX, or TXT file."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

def _extract_from_pdf(content: bytes) -> str:
    """Extract text from PDF file"""
    text = ""
    pdf_document = fitz.open(stream=content, filetype="pdf")
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    
    pdf_document.close()
    return text.strip()

def _extract_from_docx(content: bytes) -> str:
    """Extract text from DOCX file"""
    doc = Document(io.BytesIO(content))
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text.strip()

def _extract_from_txt(content: bytes) -> str:
    """Extract text from TXT file"""
    try:
        # Try UTF-8 first
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback to latin-1
        text = content.decode('latin-1')
    
    return text.strip()

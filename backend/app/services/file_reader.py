import os
import logging
from pathlib import Path
from .ocr_service import ocr_pdf

logging.basicConfig(level=logging.INFO)
nhat_ky = logging.getLogger(__name__)

def extract_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        nhat_ky.error(f"Không tìm thấy file: {file_path}")
        return ""

    path = Path(file_path)
    suffix = path.suffix.lower().lstrip(".")
    noi_dung = ""

    try:
        if suffix in {"png", "jpg", "jpeg"}:
            from PIL import Image
            import pytesseract
            image = Image.open(path)
            noi_dung = pytesseract.image_to_string(image, lang='vie') or ""
            
        elif suffix == "pdf":
            import pdfplumber
            extracted_parts = []
            try:
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            extracted_parts.append(text)
                noi_dung = "\n".join(extracted_parts).strip()
            except Exception as e:
                nhat_ky.error(f"Lỗi pdfplumber: {e}")
            
            # Fallback to OCR if empty or very short
            if not noi_dung or len(noi_dung) < 50:
                nhat_ky.info(f"PDF không có text hoặc text bị lỗi font, thử gọi OCR: {file_path}")
                noi_dung = ocr_pdf(str(path))
                
        elif suffix in {"docx", "doc"}:
            from docx import Document
            doc = Document(str(path))
            parts = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
            noi_dung = "\n".join(parts).strip()
            
        elif suffix in {"xls", "xlsx"}:
            import pandas as pd
            bang_du_lieu = pd.read_excel(file_path)
            noi_dung = bang_du_lieu.to_string()
            
        else:
            nhat_ky.warning(f"Định dạng {suffix} chưa được hỗ trợ trích xuất")
            
    except Exception as loi:
        nhat_ky.error(f"Lỗi khi trích xuất file {file_path}: {loi}")

    return noi_dung.strip()

import logging
from pdf2image import convert_from_path
import pytesseract

nhat_ky = logging.getLogger(__name__)

def ocr_pdf(path: str) -> str:
    """
    Sử dụng pdf2image và pytesseract để trích xuất text 
    từ file PDF không có text dạng số (scanned PDF).
    """
    try:
        images = convert_from_path(path)
        text_parts = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='vie') # Thêm ngôn ngữ tiếng Việt (vie)
            text_parts.append(text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        nhat_ky.error(f"Lỗi OCR PDF {path}: {e}")
        return ""

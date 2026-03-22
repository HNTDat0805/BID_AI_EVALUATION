import pdfplumber
import docx
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO)
nhat_ky = logging.getLogger(__name__)

def trich_xuat_noi_dung(duong_dan_file: str) -> str:
    if not os.path.exists(duong_dan_file):
        nhat_ky.error(f"Không tìm thấy file: {duong_dan_file}")
        return "Lỗi trích xuất: File không tồn tại"

    phan_mo_rong = duong_dan_file.split(".")[-1].lower()
    noi_dung = ""
    try:
        if phan_mo_rong == "pdf":
            with pdfplumber.open(duong_dan_file) as tệp_pdf:
                for trang in tệp_pdf.pages:
                    van_ban = trang.extract_text()
                    if van_ban:
                        noi_dung += van_ban + "\n"
        elif phan_mo_rong == "docx":
            tai_lieu = docx.Document(duong_dan_file)
            for doan_van in tai_lieu.paragraphs:
                noi_dung += doan_van.text + "\n"
        elif phan_mo_rong == "doc":
             nhat_ky.warning(f"Định dạng .doc có thể không được hỗ trợ đầy đủ. Vui lòng sử dụng .docx")
             noi_dung = "Cảnh báo: Định dạng .doc cũ không được hỗ trợ trích xuất toàn bộ bản văn."
        elif phan_mo_rong in ["xls", "xlsx"]:
            bang_du_lieu = pd.read_excel(duong_dan_file)
            noi_dung = bang_du_lieu.to_string()
        else:
            noi_dung = f"Định dạng {phan_mo_rong} chưa được hỗ trợ trích xuất"
    except Exception as loi:
        nhat_ky.error(f"Lỗi khi trích xuất file {duong_dan_file}: {loi}")
        noi_dung = f"Lỗi trích xuất hệ thống: {str(loi)}"
    
    return noi_dung.strip()

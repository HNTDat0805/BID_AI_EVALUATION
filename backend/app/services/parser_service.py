import re

def parse_ho_so(text: str) -> dict:
    """
    Trích xuất cấu trúc cơ bản từ văn bản hồ sơ thầu bằng regex đơn giản.
    """
    data = {
        "id_dau_thau": None,
        "ten_goi_thau": None,
        "gia_du_thau": None,
        "bao_lanh": {
            "co": False,
            "gia_tri": None
        }
    }
    
    if not text:
        return data
        
    id_match = re.search(r'(?:ố hiệu gói thầu|Mã TBMT)\s*[:|-]?\s*([A-Za-z0-9_-]+)', text, re.IGNORECASE)
    if id_match:
        data["id_dau_thau"] = id_match.group(1)

    ten_match = re.search(r'Tên gói thầu\s*[:|-]?\s*(.+)', text, re.IGNORECASE)
    if ten_match:
        data["ten_goi_thau"] = ten_match.group(1).strip()
        
    gia_match = re.search(r'Giá dự thầu\s*[:|-]?\s*([\d\.,\s]+.*?(?:VND|VNĐ|đồng))', text, re.IGNORECASE)
    if gia_match:
        data["gia_du_thau"] = gia_match.group(1).strip()
        
    bao_lanh_match = re.search(r'Bảo đảm dự thầu\s*[:|-]?\s*(Có|Không)?.*?giá trị.*:?\s*([\d\.,\s]+.*?(?:VND|VNĐ|đồng))', text, re.IGNORECASE | re.DOTALL)
    if not bao_lanh_match:
        bao_lanh_match = re.search(r'Bảo lãnh dự thầu.*?giá trị.*?([\d\.,\s]+.*?(?:VND|VNĐ|đồng))', text, re.IGNORECASE | re.DOTALL)

    if bao_lanh_match:
        data["bao_lanh"]["co"] = True
        try:
            gt = bao_lanh_match.group(2) if len(bao_lanh_match.groups()) > 1 else bao_lanh_match.group(1)
            if gt:
                data["bao_lanh"]["gia_tri"] = gt.strip()
        except IndexError:
            pass

    return data

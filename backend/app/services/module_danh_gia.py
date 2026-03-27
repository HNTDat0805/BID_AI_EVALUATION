from typing import Dict, Any
import logging

nhat_ky = logging.getLogger(__name__)

def danh_gia_tinh_hop_le(du_lieu_ai: Dict[str, Any]) -> Dict[str, Any]:
    tu_dien_anh_xa = {
        "presence": "hien_dien",
        "guarantee": "bao_lanh",
        "price": "gia",
        "signature": "chu_ky"
    }

    chi_tiet = {}
    hop_le_hoan_toan = True

    for khoa_cu, khoa_moi in tu_dien_anh_xa.items():
        du_lieu_truong = du_lieu_ai.get(khoa_cu)
        
        if isinstance(du_lieu_truong, dict):
            ket_qua = du_lieu_truong.get("ket_qua", False)
            bang_chung = du_lieu_truong.get("evidence", "Không cung cấp")
        else:
            ket_qua = False
            bang_chung = "Thiếu dữ liệu tệp"

        chi_tiet[khoa_moi] = {
            "ket_qua": ket_qua,
            "evidence": bang_chung
        }

        if not ket_qua:
            hop_le_hoan_toan = False

    ket_luan = "Hợp lệ" if hop_le_hoan_toan else "Không hợp lệ"

    nhat_ky.info(f"Kết quả đánh giá: {ket_luan}")

    return {
        "ket_luan": ket_luan,
        "chi_tiet": chi_tiet
    }

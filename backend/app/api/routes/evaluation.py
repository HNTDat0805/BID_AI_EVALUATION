import os
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import lay_db, KetQuaDanhGia, HoSoDuThau
from app.models.schemas import KetQuaDanhGiaRa

from app.services.file_reader import extract_text
from app.services.parser_service import parse_ho_so
from app.services.module_danh_gia import danh_gia_tinh_hop_le
from app.services.ai_evaluation.evaluator import BoDanhGiaAI
from app.services.ai_evaluation.llm_client import KhachHangLLM

router = APIRouter(prefix="/api/danh-gia", tags=["Đánh giá"])
nhat_ky = logging.getLogger(__name__)

# Khởi tạo instance đánh giá toàn cục để tái sử dụng
_bo_danh_gia_ai = None

def lay_bo_danh_gia() -> BoDanhGiaAI:
    global _bo_danh_gia_ai
    if _bo_danh_gia_ai is None:
        api_key_gemini = os.environ.get("GOOGLE_API_KEY", os.environ.get("GEMINI_API_KEY"))
        if not api_key_gemini:
            nhat_ky.error("Chưa cấu hình GOOGLE_API_KEY / GEMINI_API_KEY")
            raise HTTPException(status_code=500, detail="Chưa cấu hình API Key cho AI")

        khach_hang_llm = KhachHangLLM(
            loai_llm="gemini",
            api_key_gemini=api_key_gemini,
            ten_mau_gemini="gemini-1.5-pro",
            api_key_openai=None,
            ten_mau_openai=None
        )
        _bo_danh_gia_ai = BoDanhGiaAI(khach_hang_llm)
        
    return _bo_danh_gia_ai


class YeuCauChayDanhGia(BaseModel):
    ho_so_id: int


def xu_ly_trich_xuat_text(ho_so: HoSoDuThau, db: Session) -> str:
    """Hàm trích xuất văn bản từ hồ sơ dự thầu"""
    text = ho_so.noi_dung_text
    
    if not text:
        if not ho_so.duong_dan_file or not os.path.exists(ho_so.duong_dan_file):
            raise ValueError("Không tìm thấy file tài liệu để trích xuất nội dung")
            
        nhat_ky.info(f"Đang trích xuất text từ file: {ho_so.duong_dan_file}")
        text = extract_text(ho_so.duong_dan_file)
        
        if text:
            # Lưu lại text vào DB để lần sau mượn
            try:
                ho_so.noi_dung_text = text
                db.commit()
            except Exception as e:
                db.rollback()
                nhat_ky.error(f"Lỗi khi lưu trữ văn bản vào DB: {e}")
            
    if not text:
        raise ValueError("Không thể trích xuất nội dung từ hồ sơ")
        
    return text

async def goi_ai_danh_gia(text: str) -> dict:
    """Hàm gọi AI để lấy json kết quả thô"""
    evaluator = lay_bo_danh_gia()
    try:
        du_lieu_ai = await evaluator.run(text)
        return du_lieu_ai
    except Exception as e:
        nhat_ky.error(f"Lỗi xử lý AI Evaluator: {str(e)}")
        raise RuntimeError(f"Lỗi xử lý AI Evaluator: {str(e)}")

async def xu_ly_danh_gia_mot_ho_so(ho_so_id: int, db: Session) -> KetQuaDanhGia:
    """Hàm lõi thực hiện các bước cho 1 hồ sơ"""
    nhat_ky.info(f"Bắt đầu đánh giá hồ sơ ID: {ho_so_id}")
    
    ho_so = db.query(HoSoDuThau).filter(HoSoDuThau.id == ho_so_id).first()
    if not ho_so:
        raise FileNotFoundError("Không tìm thấy hồ sơ để đánh giá")
        
    # 1. Lấy hoặc trích xuất nội dung text
    try:
        text = xu_ly_trich_xuat_text(ho_so, db)
    except ValueError as e:
        raise ValueError(str(e))
        
    # parse dữ liệu cơ bản (log cho quy trình)
    _ = parse_ho_so(text)
    
    # 2. Gọi AI Evaluator
    try:
        du_lieu_ai = await goi_ai_danh_gia(text)
    except RuntimeError as e:
        raise RuntimeError(str(e))
        
    # 3. Đánh giá tính hợp lệ bằng code logic
    ket_qua = danh_gia_tinh_hop_le(du_lieu_ai)
    
    # 4. Lưu vào DB
    try:
        ban_ghi_ket_qua = KetQuaDanhGia(
            ho_so_id=ho_so_id,
            ket_luan=ket_qua["ket_luan"],
            chi_tiet_json=ket_qua["chi_tiet"]
        )
        db.add(ban_ghi_ket_qua)
        
        ho_so.trang_thai = "Đã đánh giá"
        db.commit()
        db.refresh(ban_ghi_ket_qua)
        
        return ban_ghi_ket_qua
    except Exception as loi:
        db.rollback()
        nhat_ky.error(f"Lỗi hệ thống khi lưu kết quả đánh giá cho hồ sơ {ho_so_id}: {loi}")
        raise SystemError("Lỗi hệ thống khi lưu kết quả đánh giá")

@router.post("/", response_model=KetQuaDanhGiaRa)
async def danh_gia_ho_so(yeu_cau: YeuCauChayDanhGia, db: Session = Depends(lay_db)):
    try:
        ket_qua = await xu_ly_danh_gia_mot_ho_so(yeu_cau.ho_so_id, db)
        return ket_qua
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except SystemError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        nhat_ky.error(f"Lỗi ngoại lệ: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống")

@router.post("/batch", response_model=List[KetQuaDanhGiaRa])
async def danh_gia_nhieu_ho_so(danh_sach_ho_so_id: List[int], db: Session = Depends(lay_db)):
    danh_sach_ket_qua = []
    
    for ho_so_id in danh_sach_ho_so_id:
        try:
            ket_qua = await xu_ly_danh_gia_mot_ho_so(ho_so_id, db)
            danh_sach_ket_qua.append(ket_qua)
        except Exception as e:
            nhat_ky.error(f"Bỏ qua hồ sơ {ho_so_id} do gặp lỗi: {str(e)}")
            # Không crash hệ thống nếu 1 hồ sơ bị lỗi
            continue
            
    return danh_sach_ket_qua

@router.get("/{ho_so_id}", response_model=KetQuaDanhGiaRa)
def xem_ket_qua_chi_tiet(ho_so_id: int, db: Session = Depends(lay_db)):
    ket_qua = db.query(KetQuaDanhGia).filter(KetQuaDanhGia.ho_so_id == ho_so_id).order_by(KetQuaDanhGia.thoi_gian.desc()).first()
    
    if not ket_qua:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết quả đánh giá cho hồ sơ này")
        
    return ket_qua

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import lay_db, KetQuaDanhGia, HoSoDuThau
from services.module_danh_gia import danh_gia_tinh_hop_le
from models.schemas import YeuCauDanhGia, KetQuaDanhGiaRa
from typing import Annotated
import logging

nhat_ky = logging.getLogger(__name__)
router = APIRouter(prefix="/api/danh-gia", tags=["Đánh giá"])

@router.post("/", response_model=KetQuaDanhGiaRa)
def thuc_hien_danh_gia(yeu_cau: YeuCauDanhGia, db: Annotated[Session, Depends(lay_db)]):
    try:
        ho_so = db.query(HoSoDuThau).filter(HoSoDuThau.id == yeu_cau.ho_so_id).first()
        if not ho_so:
             raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ để đánh giá")

        ket_qua = danh_gia_tinh_hop_le(yeu_cau.du_lieu_ai)

        ban_ghi_ket_qua = KetQuaDanhGia(
            ho_so_id=yeu_cau.ho_so_id,
            ket_luan=ket_qua["ket_luan"],
            chi_tiet_json=ket_qua["chi_tiet"]
        )
        db.add(ban_ghi_ket_qua)

        ho_so.trang_thai = "Đã đánh giá"
        
        db.commit()
        db.refresh(ban_ghi_ket_qua)

        return ban_ghi_ket_qua
    except HTTPException:
        raise
    except Exception as loi:
        db.rollback()
        nhat_ky.error(f"Lỗi khi thực hiện đánh giá cho hồ sơ {yeu_cau.ho_so_id}: {loi}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi xử lý đánh giá")

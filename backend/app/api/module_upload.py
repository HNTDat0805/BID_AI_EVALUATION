from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.models.database import lay_db, HoSoDuThau
from app.models.schemas import ThongBaoRa
from app.services.file_reader import extract_text
from typing import Annotated
import shutil
import os
import logging

nhat_ky = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Tải lên"])

THU_MUC_LUU_TRU = "du_lieu_tai_len"
os.makedirs(THU_MUC_LUU_TRU, exist_ok=True)

@router.post("/upload", response_model=ThongBaoRa)
async def tai_len_ho_so(
    file: Annotated[UploadFile, File(...)],
    goi_thau_id: Annotated[int, Form(...)],
    nha_thau_id: Annotated[int, Form(...)],
    db: Annotated[Session, Depends(lay_db)]
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Không tìm thấy thông tin file tải lên")

    phan_mo_rong = file.filename.split(".")[-1].lower()
    if phan_mo_rong not in ["pdf", "docx", "doc", "xlsx", "xls"]:
        raise HTTPException(status_code=400, detail=f"Định dạng {phan_mo_rong} không được hỗ trợ")

    duong_dan_file = os.path.join(THU_MUC_LUU_TRU, file.filename)
    
    try:
        with open(duong_dan_file, "wb") as bo_nho_dem:
            shutil.copyfileobj(file.file, bo_nho_dem)
    except Exception as loi:
        nhat_ky.error(f"Lỗi khi lưu file {file.filename}: {loi}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi lưu file")

    noi_dung = extract_text(duong_dan_file)

    try:
        ho_so_moi = HoSoDuThau(
            goi_thau_id=goi_thau_id,
            nha_thau_id=nha_thau_id,
            duong_dan_file=duong_dan_file,
            noi_dung_text=noi_dung,
            trang_thai="Đã tải lên"
        )
        db.add(ho_so_moi)
        db.commit()
        db.refresh(ho_so_moi)
        return ThongBaoRa(thong_bao="Tải lên thành công", ho_so_id=ho_so_moi.id)
    except Exception as loi:
        db.rollback()
        nhat_ky.error(f"Lỗi khi lưu DB hồ sơ {file.filename}: {loi}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi lưu thông tin vào CSDL")

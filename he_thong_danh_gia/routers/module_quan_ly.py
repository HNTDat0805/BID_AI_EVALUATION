from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import lay_db, HoSoDuThau
from models.schemas import HoSoKetQua
from typing import List, Annotated, Optional

router = APIRouter(prefix="/api/ho-so", tags=["Quản lý hồ sơ"])

@router.get("/", response_model=List[HoSoKetQua])
def lay_danh_sach_ho_so(
    db: Annotated[Session, Depends(lay_db)],
    goi_thau_id: Optional[int] = None
):
    try:
        truy_van = db.query(HoSoDuThau)
        if goi_thau_id is not None:
            truy_van = truy_van.filter(HoSoDuThau.goi_thau_id == goi_thau_id)
        danh_sach = truy_van.all()
        return danh_sach
    except Exception as loi:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách hồ sơ: {str(loi)}")

@router.get("/{id}", response_model=HoSoKetQua)
def lay_ho_so_theo_id(id: int, db: Annotated[Session, Depends(lay_db)]):
    ho_so = db.query(HoSoDuThau).filter(HoSoDuThau.id == id).first()
    if not ho_so:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ với ID đã cung cấp")
    return ho_so

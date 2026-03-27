from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime

class YeuCauDanhGia(BaseModel):
    ho_so_id: int = Field(..., description="ID của hồ sơ dự thầu cần đánh giá")
    du_lieu_ai: Dict[str, Any] = Field(..., description="Dữ liệu JSON thô từ AI")

class HoSoKetQua(BaseModel):
    id: int
    goi_thau_id: int
    nha_thau_id: int
    duong_dan_file: str
    noi_dung_text: Optional[str] = None
    trang_thai: str

    model_config = ConfigDict(from_attributes=True)

class KetQuaDanhGiaRa(BaseModel):
    id: int
    ho_so_id: int
    ket_luan: str
    chi_tiet_json: Dict[str, Any]
    thoi_gian: datetime

    model_config = ConfigDict(from_attributes=True)

class ThongBaoRa(BaseModel):
    thong_bao: str
    ho_so_id: Optional[int] = None

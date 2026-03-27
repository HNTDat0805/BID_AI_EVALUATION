from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChiTietHienDien(BaseModel):
    """
    Trích xuất cho tiêu chí "Sự hiện diện".
    """

    co_hien_dien: bool
    trich_dan_chung: list[str] = Field(default_factory=list)
    ghi_chu: str | None = None

    model_config = ConfigDict(extra="forbid")


class ChiTietBaoLanh(BaseModel):
    """
    Trích xuất cho tiêu chí "Bảo lãnh dự thầu".
    """

    gia_tri_bao_lanh: str
    thoi_gian_hieu_luc: str
    ngan_hang_phat_hanh: str
    trich_dan_chung: list[str] = Field(default_factory=list)
    ghi_chu: str | None = None

    model_config = ConfigDict(extra="forbid")


class ChiTietGiaThau(BaseModel):
    """
    Trích xuất cho tiêu chí "Giá dự thầu".
    """

    gia_du_thau: str
    gia_du_thau_trong_so: str | None = None
    gia_du_thau_trong_chu: str | None = None
    hop_le_so_voi_chu: bool
    trich_dan_chung: list[str] = Field(default_factory=list)
    ghi_chu: str | None = None

    model_config = ConfigDict(extra="forbid")


class ChiTietKyTenDongDau(BaseModel):
    """
    Trích xuất cho tiêu chí "Ký tên/Đóng dấu".
    """

    chu_ky: bool
    con_dau: bool
    trich_dan_chung: list[str] = Field(default_factory=list)
    ghi_chu: str | None = None

    model_config = ConfigDict(extra="forbid")


class KetQuaDanhGia(BaseModel):
    """
    Mẫu kết quả đánh giá chung.
    """

    lap_luan: str
    hop_le: bool
    du_lieu_trich_xuat: dict[str, Any]

    model_config = ConfigDict(extra="forbid")


class KetQuaHienDien(KetQuaDanhGia):
    lap_luan: str
    hop_le: bool
    du_lieu_trich_xuat: ChiTietHienDien

    model_config = ConfigDict(extra="forbid")


class KetQuaBaoLanh(KetQuaDanhGia):
    lap_luan: str
    hop_le: bool
    du_lieu_trich_xuat: ChiTietBaoLanh

    model_config = ConfigDict(extra="forbid")


class KetQuaGiaThau(KetQuaDanhGia):
    lap_luan: str
    hop_le: bool
    du_lieu_trich_xuat: ChiTietGiaThau

    model_config = ConfigDict(extra="forbid")


class KetQuaKyTenDongDau(KetQuaDanhGia):
    lap_luan: str
    hop_le: bool
    du_lieu_trich_xuat: ChiTietKyTenDongDau

    model_config = ConfigDict(extra="forbid")


from __future__ import annotations

from .llm_client import KhachHangLLM
from .prompts import (
    mau_prompt_bao_lanh,
    mau_prompt_gia_thau,
    mau_prompt_hien_dien,
    mau_prompt_ky_ten_dong_dau,
)
from .schemas import (
    KetQuaBaoLanh,
    KetQuaDanhGia,
    KetQuaGiaThau,
    KetQuaHienDien,
    KetQuaKyTenDongDau,
)


class BoDanhGiaAI:
    """
    Engine đánh giá hồ sơ bằng LLM cho 4 tiêu chí cốt lõi.
    """

    def __init__(self, khach_hang_llm: KhachHangLLM) -> None:
        self.khach_hang_llm = khach_hang_llm

    async def danh_gia_hien_dien_ai(
        self,
        tieu_chi_yeu_cau: str,
        du_lieu_dau_vao: str,
    ) -> KetQuaHienDien:
        van_ban_prompt = mau_prompt_hien_dien.format(
            tieu_chi_yeu_cau=tieu_chi_yeu_cau,
            du_lieu_dau_vao=du_lieu_dau_vao,
        )
        return await self.khach_hang_llm.goi_llm_va_trich_xuat_json_cau_truc(
            van_ban_prompt=van_ban_prompt,
            mau_model=KetQuaHienDien,
        )

    async def danh_gia_bao_lanh_ai(
        self,
        tieu_chi_yeu_cau: str,
        du_lieu_dau_vao: str,
    ) -> KetQuaBaoLanh:
        van_ban_prompt = mau_prompt_bao_lanh.format(
            tieu_chi_yeu_cau=tieu_chi_yeu_cau,
            du_lieu_dau_vao=du_lieu_dau_vao,
        )
        return await self.khach_hang_llm.goi_llm_va_trich_xuat_json_cau_truc(
            van_ban_prompt=van_ban_prompt,
            mau_model=KetQuaBaoLanh,
        )

    async def danh_gia_gia_thau_ai(
        self,
        tieu_chi_yeu_cau: str,
        du_lieu_dau_vao: str,
    ) -> KetQuaGiaThau:
        van_ban_prompt = mau_prompt_gia_thau.format(
            tieu_chi_yeu_cau=tieu_chi_yeu_cau,
            du_lieu_dau_vao=du_lieu_dau_vao,
        )
        return await self.khach_hang_llm.goi_llm_va_trich_xuat_json_cau_truc(
            van_ban_prompt=van_ban_prompt,
            mau_model=KetQuaGiaThau,
        )

    async def danh_gia_ky_ten_dong_dau_ai(
        self,
        tieu_chi_yeu_cau: str,
        du_lieu_dau_vao: str,
    ) -> KetQuaKyTenDongDau:
        van_ban_prompt = mau_prompt_ky_ten_dong_dau.format(
            tieu_chi_yeu_cau=tieu_chi_yeu_cau,
            du_lieu_dau_vao=du_lieu_dau_vao,
        )
        return await self.khach_hang_llm.goi_llm_va_trich_xuat_json_cau_truc(
            van_ban_prompt=van_ban_prompt,
            mau_model=KetQuaKyTenDongDau,
        )

    async def danh_gia_ai_theo_tieu_chi(
        self,
        loai_tieu_chi: str,
        tieu_chi_yeu_cau: str,
        du_lieu_dau_vao: str,
    ) -> KetQuaDanhGia:
        """
        API thống nhất: truyền `loai_tieu_chi` để engine chạy đúng luồng.
        """

        loai_tieu_chi_thu_gon = loai_tieu_chi.strip().lower()

        if loai_tieu_chi_thu_gon not in {
            "hien_dien",
            "bao_lanh",
            "gia_thau",
            "ky_ten_dong_dau",
        }:
            raise ValueError(
                f"Loại tiêu chí không hỗ trợ: {loai_tieu_chi}"
            )

        if loai_tieu_chi_thu_gon == "hien_dien":
            return await self.danh_gia_hien_dien_ai(
                tieu_chi_yeu_cau=tieu_chi_yeu_cau,
                du_lieu_dau_vao=du_lieu_dau_vao,
            )

        if loai_tieu_chi_thu_gon == "bao_lanh":
            return await self.danh_gia_bao_lanh_ai(
                tieu_chi_yeu_cau=tieu_chi_yeu_cau,
                du_lieu_dau_vao=du_lieu_dau_vao,
            )

        if loai_tieu_chi_thu_gon == "gia_thau":
            return await self.danh_gia_gia_thau_ai(
                tieu_chi_yeu_cau=tieu_chi_yeu_cau,
                du_lieu_dau_vao=du_lieu_dau_vao,
            )

        # ky_ten_dong_dau
        return await self.danh_gia_ky_ten_dong_dau_ai(
            tieu_chi_yeu_cau=tieu_chi_yeu_cau,
            du_lieu_dau_vao=du_lieu_dau_vao,
        )


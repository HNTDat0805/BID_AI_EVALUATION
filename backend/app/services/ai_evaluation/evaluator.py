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

    async def run(self, text: str) -> dict:
        """
        Đánh giá toàn bộ 4 tiêu chí và trả về dictionary tương thích
        với hàm danh_gia_tinh_hop_le.
        """
        import asyncio

        # Tiêu chí cơ bản
        tc_hien_dien = "Hồ sơ có đầy đủ các tài liệu pháp lý cơ bản không?"
        tc_bao_lanh = "Hồ sơ có bảo đảm dự thầu (bảo lãnh) hợp lệ không?"
        tc_gia_thau = "Giá dự thầu có được ghi rõ ràng không?"
        tc_ky_ten = "Có chữ ký và đóng dấu hợp lệ không?"

        t_hien_dien = self.danh_gia_hien_dien_ai(tc_hien_dien, text)
        t_bao_lanh = self.danh_gia_bao_lanh_ai(tc_bao_lanh, text)
        t_gia_thau = self.danh_gia_gia_thau_ai(tc_gia_thau, text)
        t_ky_ten = self.danh_gia_ky_ten_dong_dau_ai(tc_ky_ten, text)

        kq_hien_dien, kq_bao_lanh, kq_gia_thau, kq_ky_ten = await asyncio.gather(
            t_hien_dien, t_bao_lanh, t_gia_thau, t_ky_ten
        )

        return {
            "presence": {
                "ket_qua": kq_hien_dien.hop_le,
                "evidence": kq_hien_dien.lap_luan
            },
            "guarantee": {
                "ket_qua": kq_bao_lanh.hop_le,
                "evidence": kq_bao_lanh.lap_luan
            },
            "price": {
                "ket_qua": kq_gia_thau.hop_le,
                "evidence": kq_gia_thau.lap_luan
            },
            "signature": {
                "ket_qua": kq_ky_ten.hop_le,
                "evidence": kq_ky_ten.lap_luan
            }
        }

from __future__ import annotations

import asyncio
import ast
import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T_kieu_ket_qua = TypeVar("T_kieu_ket_qua", bound=BaseModel)


class LoiLLM(Exception):
    """Lỗi chung cho tầng gọi LLM."""


class LoiRateLimitHoacMang(Exception):
    """Gọi LLM bị giới hạn hoặc lỗi mạng."""


class LoiPhanTichJson(Exception):
    """LLM trả về JSON không hợp lệ."""


class LoiXacThucDuLieu(Exception):
    """JSON hợp lệ nhưng không khớp schema."""


def xu_ly_json(van_ban_phan_hoi: str) -> dict[str, Any]:
    """
    Trích xuất JSON từ phản hồi của LLM.

    Hỗ trợ các biến thể phổ biến:
    - Có/không có code fence ```json ... ```
    - Có thêm văn bản trước/sau JSON
    - JSON/giống JSON dùng dấu nháy đơn (fallback `ast.literal_eval`)
    """

    van_ban_da_strip = van_ban_phan_hoi.strip()
    if not van_ban_da_strip:
        raise LoiPhanTichJson("Phản hồi LLM rỗng, không thể trích xuất JSON.")

    # Loại bỏ markdown code fence (nếu có).
    van_ban_khong_code_fence = re.sub(
        r"^```(?:json)?\s*",
        "",
        van_ban_da_strip,
        flags=re.IGNORECASE,
    )
    van_ban_khong_code_fence = re.sub(
        r"\s*```$",
        "",
        van_ban_khong_code_fence,
        flags=re.IGNORECASE,
    )

    vi_tri_mo = van_ban_khong_code_fence.find("{")
    vi_tri_dong = van_ban_khong_code_fence.rfind("}")
    if vi_tri_mo == -1 or vi_tri_dong == -1 or vi_tri_dong <= vi_tri_mo:
        raise LoiPhanTichJson("Không tìm thấy đối tượng JSON trong phản hồi.")

    doan_json = van_ban_khong_code_fence[vi_tri_mo : vi_tri_dong + 1].strip()

    try:
        ket_qua_json = json.loads(doan_json)
    except json.JSONDecodeError as loi_json:
        # Fallback: đôi khi LLM xuất JSON kiểu python (single quotes).
        try:
            ket_qua_json = ast.literal_eval(doan_json)
        except (ValueError, SyntaxError) as loi_literal:
            raise LoiPhanTichJson(
                "Không thể parse JSON. "
                f"Loi json: {loi_json}. "
                f"Loi literal_eval: {loi_literal}."
            ) from loi_literal

    if not isinstance(ket_qua_json, dict):
        raise LoiPhanTichJson("Kết quả parse không phải dict JSON.")

    return ket_qua_json


def xac_thuc_bang_pydantic(
    mau_model: type[T_kieu_ket_qua],
    du_lieu_json: dict[str, Any],
) -> T_kieu_ket_qua:
    try:
        return mau_model.model_validate(du_lieu_json)
    except ValidationError as loi_xac_thuc:
        raise LoiXacThucDuLieu(str(loi_xac_thuc)) from loi_xac_thuc


class KhachHangLLM:
    """
    Tầng trừu tượng gọi LLM cho Gemini và OpenAI.
    """

    def __init__(
        self,
        loai_llm: str,
        api_key_gemini: str | None,
        ten_mau_gemini: str,
        api_key_openai: str | None,
        ten_mau_openai: str | None,
    ) -> None:
        self.loai_llm = loai_llm
        self.api_key_gemini = api_key_gemini
        self.ten_mau_gemini = ten_mau_gemini
        self.api_key_openai = api_key_openai
        self.ten_mau_openai = ten_mau_openai

    def goi_api_gemini(self, van_ban_prompt: str) -> str:
        """
        Gọi Google Gemini (gemini python SDK) và trả về text.
        """

        if not self.api_key_gemini:
            raise LoiRateLimitHoacMang(
                "Thiếu GOOGLE API key cho Gemini."
            )  # dùng chung loại lỗi để retry có ích

        try:
            import google.generativeai as genai
        except ImportError as loi_import:
            raise LoiLLM(
                "Thiếu thư viện `google-generativeai`. "
                "Vui lòng cài đặt để dùng Gemini."
            ) from loi_import

        try:
            genai.configure(api_key=self.api_key_gemini)
            mau_hinh_gemini = genai.GenerativeModel(self.ten_mau_gemini)
            ket_qua = mau_hinh_gemini.generate_content(van_ban_prompt)
            van_ban_phan_hoi = getattr(ket_qua, "text", None) or str(ket_qua)
            return van_ban_phan_hoi
        except Exception as loi_goi:
            # Không phụ thuộc sâu vào kiểu exception từng SDK.
            chuoi_loi = str(loi_goi).lower()
            if "429" in chuoi_loi or "rate limit" in chuoi_loi or "resource exhausted" in chuoi_loi:
                raise LoiRateLimitHoacMang(str(loi_goi)) from loi_goi
            raise LoiRateLimitHoacMang(str(loi_goi)) from loi_goi

    def goi_api_openai(self, van_ban_prompt: str) -> str:
        """
        Gọi OpenAI (official python SDK) và trả về text.
        """

        if not self.api_key_openai:
            raise LoiRateLimitHoacMang(
                "Thiếu OPENAI API key để gọi OpenAI."
            )
        if not self.ten_mau_openai:
            raise LoiLLM("Chưa cấu hình `ten_mau_openai`.")

        try:
            from openai import OpenAI  # type: ignore
        except ImportError as loi_import:
            raise LoiLLM(
                "Thiếu thư viện `openai`. Vui lòng cài đặt để dùng OpenAI."
            ) from loi_import

        khach_hang_openai = OpenAI(api_key=self.api_key_openai)

        try:
            try:
                ket_qua = khach_hang_openai.chat.completions.create(
                    model=self.ten_mau_openai,
                    messages=[{"role": "user", "content": van_ban_prompt}],
                    temperature=0,
                    response_format={"type": "json_object"},
                )
            except Exception as loi_1:
                # Một số model/phiên bản không hỗ trợ response_format.
                chuoi_loi_1 = str(loi_1).lower()
                if "response_format" in chuoi_loi_1 or "json_object" in chuoi_loi_1:
                    ket_qua = khach_hang_openai.chat.completions.create(
                        model=self.ten_mau_openai,
                        messages=[{"role": "user", "content": van_ban_prompt}],
                        temperature=0,
                    )
                else:
                    raise

            van_ban_phan_hoi = (
                ket_qua.choices[0].message.content  # type: ignore[union-attr]
                if ket_qua.choices and ket_qua.choices[0].message
                else ""
            )
            return van_ban_phan_hoi or ""
        except Exception as loi_goi:
            chuoi_loi = str(loi_goi).lower()
            if "429" in chuoi_loi or "rate limit" in chuoi_loi or "timeout" in chuoi_loi:
                raise LoiRateLimitHoacMang(str(loi_goi)) from loi_goi
            raise LoiRateLimitHoacMang(str(loi_goi)) from loi_goi

    async def _goi_api_dua_tren_loai_llm(self, van_ban_prompt: str) -> str:
        """
        Chuyển đổi call sync sang async bằng `asyncio.to_thread`.
        """

        if self.loai_llm.lower() == "gemini":
            return await asyncio.to_thread(self.goi_api_gemini, van_ban_prompt)

        if self.loai_llm.lower() == "openai":
            return await asyncio.to_thread(self.goi_api_openai, van_ban_prompt)

        raise LoiLLM(f"Loại LLM không hợp lệ: {self.loai_llm}")

    async def goi_llm_va_trich_xuat_json_cau_truc(
        self,
        van_ban_prompt: str,
        mau_model: type[T_kieu_ket_qua],
    ) -> T_kieu_ket_qua:
        """
        Gọi LLM -> parse JSON -> validate Pydantic.

        Có retry cho các lỗi rate limit/network và lỗi parse JSON.
        """

        so_lan_thu_lai_toi_da = 3

        @retry(
            reraise=True,
            stop=stop_after_attempt(so_lan_thu_lai_toi_da),
            wait=wait_exponential(multiplier=1, min=1, max=12),
            retry=retry_if_exception_type(
                (
                    LoiRateLimitHoacMang,
                    LoiPhanTichJson,
                    LoiXacThucDuLieu,
                )
            ),
        )
        async def _goi_va_phan_tich() -> T_kieu_ket_qua:
            van_ban_phan_hoi = await self._goi_api_dua_tren_loai_llm(van_ban_prompt)
            du_lieu_json = xu_ly_json(van_ban_phan_hoi)
            return xac_thuc_bang_pydantic(mau_model=mau_model, du_lieu_json=du_lieu_json)

        return await _goi_va_phan_tich()


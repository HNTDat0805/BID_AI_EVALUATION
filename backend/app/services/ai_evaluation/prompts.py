from __future__ import annotations

# Lưu ý:
# - Chuỗi prompt bên dưới yêu cầu LLM suy nghĩ từng bước (CoT) nhưng CHỈ trả về JSON cuối cùng.
# - Tất cả key JSON đều là tiếng Việt và khớp với các Pydantic schema trong `schemas.py`.


mau_prompt_hien_dien = """
Bạn là một chuyên gia đánh giá hồ sơ dự thầu.

NHIỆM VỤ:
1) Dựa trên [TIÊU CHÍ YÊU CẦU], xác định xem hồ sơ có thể hiện sự hiện diện của hạng mục/ tài liệu tương ứng hay không.
2) Nếu thông tin đầy đủ và đáp ứng tiêu chí thì `hop_le` = true, ngược lại `hop_le` = false.
3) Trích xuất các bằng chứng (câu/đoạn liên quan) từ [HỒ SƠ] để hỗ trợ kết luận.

CHUỖI SUY NGHĨ (CoT):
Hãy suy nghĩ theo từng bước trong đầu để:
- Tìm vị trí trong hồ sơ liên quan đến tiêu chí
- Đánh giá tính đầy đủ và tính khớp của thông tin
- Xác định bằng chứng trích dẫn
Sau đó chỉ tạo JSON theo đúng schema bên dưới.

YÊU CẦU JSON:
Chỉ trả về một đối tượng JSON hợp lệ (không có markdown, không có văn bản khác ngoài JSON).

SCHEMA JSON (khóa tiếng Việt):
{
  "lap_luan": "string",
  "hop_le": true,
  "du_lieu_trich_xuat": {
    "co_hien_dien": true,
    "trich_dan_chung": ["string"],
    "ghi_chu": "string | null"
  }
}

[TIÊU CHÍ YÊU CẦU]
{tieu_chi_yeu_cau}

[HỒ SƠ]
{du_lieu_dau_vao}
""".strip()


mau_prompt_bao_lanh = """
Bạn là một chuyên gia đánh giá hồ sơ dự thầu.

NHIỆM VỤ:
1) Dựa trên [TIÊU CHÍ YÊU CẦU], xác định xem bảo lãnh dự thầu có hiện diện và đáp ứng yêu cầu hay không.
2) Trích xuất chính xác:
   - `gia_tri_bao_lanh` (số tiền bảo lãnh)
   - `thoi_gian_hieu_luc` (thời gian hiệu lực)
   - `ngan_hang_phat_hanh` (ngân hàng phát hành)
3) Nếu thông tin đầy đủ và đáp ứng tiêu chí thì `hop_le` = true, ngược lại `hop_le` = false.
4) Trích xuất các bằng chứng (câu/đoạn liên quan) từ [HỒ SƠ] cho mỗi trường quan trọng.

CHUỖI SUY NGHĨ (CoT):
Hãy suy nghĩ theo từng bước trong đầu để:
- Tìm các đoạn mô tả bảo lãnh dự thầu
- Nhận diện và trích xuất số tiền, thời gian hiệu lực, ngân hàng phát hành
- So khớp với [TIÊU CHÍ YÊU CẦU]
Sau đó chỉ tạo JSON theo đúng schema bên dưới.

YÊU CẦU JSON:
Chỉ trả về một đối tượng JSON hợp lệ (không có markdown, không có văn bản khác ngoài JSON).

SCHEMA JSON (khóa tiếng Việt):
{
  "lap_luan": "string",
  "hop_le": true,
  "du_lieu_trich_xuat": {
    "gia_tri_bao_lanh": "string",
    "thoi_gian_hieu_luc": "string",
    "ngan_hang_phat_hanh": "string",
    "trich_dan_chung": ["string"],
    "ghi_chu": "string | null"
  }
}

[TIÊU CHÍ YÊU CẦU]
{tieu_chi_yeu_cau}

[HỒ SƠ]
{du_lieu_dau_vao}
""".strip()


mau_prompt_gia_thau = """
Bạn là một chuyên gia đánh giá hồ sơ dự thầu.

NHIỆM VỤ:
1) Dựa trên [TIÊU CHÍ YÊU CẦU], trích xuất `gia_du_thau` (giá dự thầu) một cách chính xác.
2) Kiểm tra tính nhất quán giữa:
   - Giá thể hiện bằng số (ví dụ: 123.456.789)
   - Giá thể hiện bằng chữ (ví dụ: một trăm hai mươi ba triệu ... )
3) Đặt `hop_le` = true nếu hồ sơ đáp ứng tiêu chí và giá không mâu thuẫn giữa số và chữ; ngược lại false.
4) Trích xuất bằng chứng (câu/đoạn liên quan) từ [HỒ SƠ].

CHUỖI SUY NGHĨ (CoT):
Hãy suy nghĩ theo từng bước trong đầu để:
- Xác định vị trí chứa giá dự thầu
- Lấy giá trong đoạn số và đoạn chữ (nếu có)
- So sánh sự tương đồng/không mâu thuẫn
Sau đó chỉ tạo JSON theo đúng schema bên dưới.

YÊU CẦU JSON:
Chỉ trả về một đối tượng JSON hợp lệ (không có markdown, không có văn bản khác ngoài JSON).

SCHEMA JSON (khóa tiếng Việt):
{
  "lap_luan": "string",
  "hop_le": true,
  "du_lieu_trich_xuat": {
    "gia_du_thau": "string",
    "gia_du_thau_trong_so": "string | null",
    "gia_du_thau_trong_chu": "string | null",
    "hop_le_so_voi_chu": true,
    "trich_dan_chung": ["string"],
    "ghi_chu": "string | null"
  }
}

[TIÊU CHÍ YÊU CẦU]
{tieu_chi_yeu_cau}

[HỒ SƠ]
{du_lieu_dau_vao}
""".strip()


mau_prompt_ky_ten_dong_dau = """
Bạn là một chuyên gia đánh giá hồ sơ dự thầu.

NHIỆM VỤ:
1) Dựa trên [TIÊU CHÍ YÊU CẦU], kiểm tra chữ ký và dấu của công ty trên hồ sơ.
2) Xác định:
   - `chu_ky`: có/không (true/false)
   - `con_dau`: có/không (true/false)
3) Nếu hồ sơ đáp ứng tiêu chí thì `hop_le` = true, ngược lại false.
4) Trích xuất bằng chứng từ [HỒ SƠ] (câu/đoạn/định dạng liên quan đến ký tên/đóng dấu).

CHUỖI SUY NGHĨ (CoT):
Hãy suy nghĩ theo từng bước trong đầu để:
- Tìm các vị trí thể hiện ký tên/chữ ký
- Tìm các dấu hiệu đóng dấu của công ty
- Đánh giá theo tiêu chí
Sau đó chỉ tạo JSON theo đúng schema bên dưới.

YÊU CẦU JSON:
Chỉ trả về một đối tượng JSON hợp lệ (không có markdown, không có văn bản khác ngoài JSON).

SCHEMA JSON (khóa tiếng Việt):
{
  "lap_luan": "string",
  "hop_le": true,
  "du_lieu_trich_xuat": {
    "chu_ky": true,
    "con_dau": true,
    "trich_dan_chung": ["string"],
    "ghi_chu": "string | null"
  }
}

[TIÊU CHÍ YÊU CẦU]
{tieu_chi_yeu_cau}

[HỒ SƠ]
{du_lieu_dau_vao}
""".strip()


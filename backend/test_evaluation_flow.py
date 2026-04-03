import json
from typing import Dict, List, Any

# Import các Models và Engine đã viết ở những bước trước
from backend.app.models.evaluation_config import (
    EvaluationConfig,
    CriterionConfig,
    RuleType,
    RangeCondition,
    BooleanCondition,
    ExactMatchCondition
)
from backend.app.services.evaluation_engine import EvaluationEngine, EvaluationResult

def generate_final_summary(result: EvaluationResult) -> Dict[str, Any]:
    """
    Trích xuất tổng điểm và kết quả từ EvaluationResult về dạng JSON yêu cầu.
    """
    return {
        "tong_diem": result.total_score,
        "ket_qua": "Đạt" if result.is_passed_overall else "Không đạt"
    }

def rank_and_summarize_bidders(evaluations: Dict[str, EvaluationResult]) -> List[Dict[str, Any]]:
    """
    Nhận dictionary kết quả của từng nhà thầu { "Tên nhà thầu": EvaluationResult }.
    Tính điểm, xếp hạng từ cao xuống thấp và trả về JSON format.
    """
    summaries = []
    
    for bidder_name, result in evaluations.items():
        summary = generate_final_summary(result)
        summary["nha_thau"] = bidder_name
        # Lưu vào tracking ẩn để dễ sort
        summary["_is_pass"] = result.is_passed_overall
        summaries.append(summary)
        
    # Sắp xếp danh sách: Ưu tiên Pass lên trước, sau đó sắp theo Điểm giảm dần
    summaries.sort(key=lambda x: (x["_is_pass"], x["tong_diem"]), reverse=True)
    
    # Gắn hạng (chỉ xếp hạng cho ai Đạt)
    current_rank = 1
    for smry in summaries:
        if smry["ket_qua"] == "Đạt":
            smry["xep_hang"] = current_rank
            current_rank += 1
        else:
            smry["xep_hang"] = None  # Rớt thì không được xếp hạng
            
        del smry["_is_pass"] # Xóa tracking ẩn
        
    return summaries

# =========================================================
# SCRIPT ĐỂ TEST TOÀN BỘ LUỒNG (BƯỚC 1 ĐẾN 3)
# =========================================================
if __name__ == "__main__":
    
    # -----------------------------------------------
    # BƯỚC 1: Xây dựng Config Bảng điểm
    # -----------------------------------------------
    mock_config = EvaluationConfig(
        version="1.0", 
        name="Chấm Thầu Xây Lắp Cầu Đường", 
        total_max_score=100.0, 
        total_pass_threshold=70.0,
        criteria=[
            CriterionConfig(
                id="doanh_thu", 
                name="Doanh thu bình quân", 
                max_score=40, pass_threshold=10, is_mandatory=True, 
                rule_type=RuleType.RANGE,
                conditions=[
                    RangeCondition(min_value=2e9, score=40),              # >= 2 Tỉ: 40 điểm
                    RangeCondition(min_value=1e9, max_value=2e9, max_inclusive=False, score=20), # 1 Tỉ -> dưới 2 Tỉ: 20 điểm
                    RangeCondition(max_value=1e9, max_inclusive=False, score=0, fail_immediately=True) # < 1 Tỉ: trượt luôn
                ]
            ),
            CriterionConfig(
                id="so_nam_kinh_nghiem", 
                name="Số năm kinh nghiệm", 
                max_score=30, pass_threshold=15, is_mandatory=False, 
                rule_type=RuleType.RANGE,
                conditions=[
                    RangeCondition(min_value=5, score=30),     # >= 5 năm: 30 đ
                    RangeCondition(min_value=3, max_value=5, max_inclusive=False, score=15), # 3 -> <5 năm: 15đ
                    RangeCondition(max_value=3, max_inclusive=False, score=0)
                ]
            ),
            CriterionConfig(
                id="co_iso", 
                name="Có ISO 9001", 
                max_score=30, is_mandatory=False, 
                rule_type=RuleType.BOOLEAN,
                conditions=[
                    BooleanCondition(expected=True, score=30),
                    BooleanCondition(expected=False, score=0)
                ]
            )
        ]
    )

    # -----------------------------------------------
    # BƯỚC 2: Mock Dữ liệu nhiều nhà thầu
    # -----------------------------------------------
    bidders_data = {
        "Nhà Thầu A": {
            "doanh_thu": 2500000000.0,  # 2.5 Tỉ đ: Trọn vẹn 40đ
            "so_nam_kinh_nghiem": 6,    # 6 năm: Trọn vẹn 30đ
            "co_iso": True              # ISO: 30đ 
                                        # --> Kỳ vọng TỔNG ĐIỂM = 100đ, PASS, Top 1.
        },
        "Nhà Thầu B": {
            "doanh_thu": 1500000000.0,  # 1.5 Tỉ đ: Được 20đ
            "so_nam_kinh_nghiem": 4,    # 4 năm: Được 15đ
            "co_iso": round(1) == 1     # ISO: Đạt 30đ (để test)
                                        # --> Kỳ vọng TỔNG ĐIỂM = 65đ -> FAIL vì không đủ ngưỡng sàn là 70đ
        },
        "Nhà Thầu C": {
            "doanh_thu": 800000000.0,   # 8 Trăm triệu đ: Điểm 0 (Nhưng đây là tiêu chí mandatory và fail_immediately)
            "so_nam_kinh_nghiem": 10,   # 10 năm: 30đ
            "co_iso": True              # Có ISO: 30đ
                                        # Kỳ vọng: Mặc dù các điểm khác cao, nhưng vi phạm doanh_thu => FAIL tổng.
        },
        "Nhà Thầu D": {
            "doanh_thu": 3000000000.0,  # 40đ
            "so_nam_kinh_nghiem": 4,    # 15 đ
            "co_iso": True              # 30 đ
                                        # --> TỔNG ĐIỂM = 85 đ -> PASS, Top 2.
        }
    }

    # -----------------------------------------------
    # BƯỚC 3: Xử lý chạy Pipeline chấm điểm
    # -----------------------------------------------
    engine = EvaluationEngine(config=mock_config)
    eval_results: Dict[str, EvaluationResult] = {}
    
    for bidder_name, b_data in bidders_data.items():
        eval_results[bidder_name] = engine.evaluate(b_data)

    # -----------------------------------------------
    # BƯỚC 4: Tổng hợp Json cuối cùng & Xếp hạng 
    # -----------------------------------------------
    final_output = rank_and_summarize_bidders(eval_results)
    
    print("--- RAW KẾT QUẢ ĐẦU RA (JSON FORMAT) ---")
    print(json.dumps(final_output, indent=2, ensure_ascii=False))

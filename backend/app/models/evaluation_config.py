from enum import Enum
from typing import List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field


class RuleType(str, Enum):
    RANGE = "range"               # Quy tắc chấm theo khoảng (VD: >= 1 tỷ)
    EXACT_MATCH = "exact_match"   # Khớp chính xác (VD: Có bằng cấp X)
    BOOLEAN = "boolean"           # True/False (VD: Đã nộp bảo lãnh)


class BaseCondition(BaseModel):
    score: float = Field(..., description="Điểm số nhận được nếu thỏa mãn điều kiện này")
    # Thay vì pass/fail chung chung, nếu người dùng rơi vào điều kiện này mà bị loại ngay, set true.
    fail_immediately: bool = Field(default=False, description="Đánh dấu rớt thầu ngay lập tức nếu rơi vào đây")


class RangeCondition(BaseCondition):
    type: Literal["range"] = "range"
    min_value: Optional[float] = Field(None, description="Giá trị tối thiểu")
    max_value: Optional[float] = Field(None, description="Giá trị tối đa")
    min_inclusive: bool = Field(True, description="Lớn hơn bằng min_value")
    max_inclusive: bool = Field(False, description="Nhỏ hơn bằng max_value")


class ExactMatchCondition(BaseCondition):
    type: Literal["exact_match"] = "exact_match"
    expected_value: Any = Field(..., description="Giá trị cần khớp định nghĩa")


class BooleanCondition(BaseCondition):
    type: Literal["boolean"] = "boolean"
    expected: bool = Field(True, description="True hoặc False")


# Do Python hỗ trợ linh hoạt, Pydantic cho phép Union. Tùy thuộc vào 'type' mà parse hợp lý.
ConditionConfig = Union[RangeCondition, ExactMatchCondition, BooleanCondition]


class CriterionConfig(BaseModel):
    id: str = Field(..., description="Mã tiêu chí, VD: 'doanh_thu_tb_3_nam', 'so_luong_nhan_su'")
    name: str = Field(..., description="Tên hoặc nội dung tiêu chí")
    description: Optional[str] = Field(None, description="Diễn giải thêm để làm rõ ý")
    
    # Các setting tính điểm
    max_score: float = Field(..., description="Điểm tối đa của tiêu chí này")
    pass_threshold: Optional[float] = Field(None, description="Điểm tối thiểu tiêu chí này cần đạt để pass (nếu có)")
    is_mandatory: bool = Field(default=False, description="Nếu True, bắt buộc phải đạt ngưỡng (nếu không đạt -> rớt thầu)")
    
    # Cấu hình quy tắc
    rule_type: RuleType = Field(..., description="Cách thức phân loại để code chạy đúng engine")
    conditions: List[ConditionConfig] = Field(
        default_factory=list, 
        description="Mảng các điều kiện điểm, thuật toán sẽ duyệt từ trên xuống / hoặc matching để ra điểm"
    )

class EvaluationConfig(BaseModel):
    """
    Cấu trúc toàn bộ bảng tiêu chí đánh giá (Master Config)
    """
    version: str = Field("1.0.0", description="Quản lý thay đổi version sau này")
    name: str = Field(..., description="Tên bộ tiêu chí (VD: Tiêu chí gói thầu IT)")
    
    total_max_score: float = Field(..., description="Tổng điểm tối đa toàn bộ các tiêu chí cộng lại")
    total_pass_threshold: float = Field(..., description="Ngưỡng tổng điểm để pass vòng Đánh giá")
    
    criteria: List[CriterionConfig] = Field(
        default_factory=list, 
        description="Danh sách các tiêu chí quy định bên trong"
    )

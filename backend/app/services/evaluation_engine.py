import logging
from typing import Dict, Any, List

from pydantic import BaseModel

from backend.app.models.evaluation_config import (
    EvaluationConfig, 
    CriterionConfig, 
    ConditionConfig, 
    RuleType,
    RangeCondition,
    ExactMatchCondition,
    BooleanCondition
)

logger = logging.getLogger(__name__)


class CriterionResult(BaseModel):
    """Lưu kết quả phân tích theo từng tiêu chí cụ thể"""
    criterion_id: str
    criterion_name: str
    raw_value: Any = None
    score: float = 0.0
    is_pass: bool = False
    is_mandatory: bool = False
    notes: List[str] = []


class EvaluationResult(BaseModel):
    """Lưu kết quả trả về tổng quan cho hệ thống chấm chấm điểm"""
    is_passed_overall: bool = False
    total_score: float = 0.0
    total_max_score: float = 0.0
    failed_mandatory_criteria: List[str] = []
    missing_data: List[str] = []
    details: Dict[str, CriterionResult] = {}


class EvaluationEngine:
    def __init__(self, config: EvaluationConfig):
        """Khởi tạo Engine với Config Rule (Đã load từ JSON/DB)"""
        self.config = config

    def evaluate(self, extracted_data: Dict[str, Any]) -> EvaluationResult:
        """
        Xử lý dictionary chứa điểm thông tin nhà thầu.
        Ví dụ data: {"doanh_thu": 1500000000, "so_nam_kinh_nghiem": 3}
        """
        result = EvaluationResult(total_max_score=self.config.total_max_score)
        
        for criterion in self.config.criteria:
            crit_res = self._evaluate_criterion(criterion, extracted_data)
            result.details[criterion.id] = crit_res
            result.total_score += crit_res.score
            
            # Kiểm tra lỗi trên tiêu chí bắt buộc
            if not crit_res.is_pass and criterion.is_mandatory:
                result.failed_mandatory_criteria.append(criterion.name)
                
            # Đánh dấu các trường dữ liệu nhà thầu đang thiếu để cảnh báo
            if "Không tìm thấy dữ liệu" in crit_res.notes:
                result.missing_data.append(criterion.id)

        # Quyết định đạt hay không ở mức tổng thể
        # Phải thoả 2 điều kiện: >= Tổng điểm sàn VÀ không trượt bất kỳ tiêu chí MANDATORY nào
        result.is_passed_overall = (
            result.total_score >= self.config.total_pass_threshold
            and len(result.failed_mandatory_criteria) == 0
        )
        
        return result

    def _evaluate_criterion(self, criterion: CriterionConfig, data: Dict[str, Any]) -> CriterionResult:
        """Thực thi logic tính điểm trên MỘT tiêu chí"""
        
        res = CriterionResult(
            criterion_id=criterion.id, 
            criterion_name=criterion.name,
            is_mandatory=criterion.is_mandatory
        )
        
        # 1. Kiểm tra Missing Data
        if criterion.id not in data or data[criterion.id] is None:
            res.notes.append("Không tìm thấy dữ liệu / Dữ liệu rỗng")
            res.score = 0.0
            
            # Nếu tiêu chí này không có ngưỡng pass, có thể châm chước pass nhưng 0 điểm, 
            # nhưng nếu thiếu của mandatory thì fail
            res.is_pass = False if criterion.is_mandatory else True
            return res
            
        value = data[criterion.id]
        res.raw_value = value
        
        achieved_score = 0.0
        fail_immediately = False
        
        # 2. Match giá trị với Rules được define trong config
        for condition in criterion.conditions:
            if self._match_condition(criterion.rule_type, condition, value):
                achieved_score = condition.score
                if condition.fail_immediately:
                    fail_immediately = True
                
                # Sẽ lấy rule ĐẦU TIÊN match được (Nên list rule cần sort ưu tiên từ cao -> thấp)
                break 
                
        res.score = achieved_score
        
        # 3. Đánh giá Pass/Fail
        if fail_immediately:
            res.is_pass = False
            res.notes.append("Bị loại vì rớt thẳng ở điều kiện loại trừ tối thiểu.")
        elif criterion.pass_threshold is not None and achieved_score < criterion.pass_threshold:
            res.is_pass = False
            res.notes.append(f"Không đạt ngưỡng điểm sàn của nhóm tiêu chí ({achieved_score}/{criterion.pass_threshold}).")
        else:
            res.is_pass = True
            
        return res
        
    def _match_condition(self, rule_type: RuleType, condition: ConditionConfig, value: Any) -> bool:
        """Kiểm tra giá trị Data đầu vào có thoả mãn điều kiện không"""
        
        if rule_type == RuleType.RANGE and isinstance(condition, RangeCondition):
            # Xử lý input biến kiểu
            try:
                numeric_val = float(value)
            except (ValueError, TypeError):
                return False
                
            if condition.min_value is not None:
                if condition.min_inclusive and numeric_val < condition.min_value:
                    return False
                if not condition.min_inclusive and numeric_val <= condition.min_value:
                    return False
                    
            if condition.max_value is not None:
                if condition.max_inclusive and numeric_val > condition.max_value:
                    return False
                if not condition.max_inclusive and numeric_val >= condition.max_value:
                    return False
                    
            return True
            
        elif rule_type == RuleType.EXACT_MATCH and isinstance(condition, ExactMatchCondition):
            return value == condition.expected_value
            
        elif rule_type == RuleType.BOOLEAN and isinstance(condition, BooleanCondition):
            return bool(value) == condition.expected
            
        return False

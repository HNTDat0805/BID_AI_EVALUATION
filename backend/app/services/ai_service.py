import google.generativeai as genai

from app.core.config import settings


class AIService:
    def __init__(self):
        # Cấu hình Gemini bằng Key từ settings
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def evaluate_proposal(self, proposal_text: str, criteria: str):
        """
        Logic này thay thế cho các node SplitInBatches và RAG trong file n8n của bạn
        """
        prompt = f"""
        Bạn là một chuyên gia đánh giá hồ sơ thầu. 
        Hãy phân tích nội dung sau dựa trên các tiêu chí đã cho.
        
        [TIÊU CHÍ]: {criteria}
        [HỒ SƠ]: {proposal_text}
        
        Hãy trả về kết quả định dạng JSON gồm: điểm số (0-100), nhận xét ưu điểm, nhận xét nhược điểm.
        """
        response = self.model.generate_content(prompt)
        return response.text


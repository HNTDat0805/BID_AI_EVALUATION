from fastapi import FastAPI
from models.database import engine, Coso
from routers.module_upload import router as router_tai_len
from routers.module_quan_ly import router as router_quan_ly
from routers.module_danh_gia import router as router_danh_gia
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    Coso.metadata.create_all(bind=engine)
except Exception as loi:
    logging.error(f"Không thể kết nối hoặc tạo CSDL: {loi}")

app = FastAPI(
    title="Hệ thống đánh giá hồ sơ thầu", 
    version="1.0.0",
    description="API xử lý hồ sơ dự thầu, trích xuất văn bản và đánh giá tính hợp lệ"
)

app.include_router(router_tai_len)
app.include_router(router_quan_ly)
app.include_router(router_danh_gia)

@app.get("/", tags=["Trang chủ"])
def trang_chu():
    return {"thong_bao": "Hệ thống Backend Đánh Giá Hồ Sơ Thầu (Bid AI Evaluation) đang hoạt động"}

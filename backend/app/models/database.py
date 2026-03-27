from sqlalchemy import create_engine, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship, Mapped, mapped_column
from typing import Dict, Any, List
from datetime import datetime
import os

URL_CO_SO_DU_LIEU = os.getenv("URL_CO_SO_DU_LIEU", "postgresql://postgres:postgres@localhost:5432/he_thong_danh_gia")

engine = create_engine(URL_CO_SO_DU_LIEU)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Coso(DeclarativeBase):
    pass

class GoiThau(Coso):
    __tablename__ = "goi_thau"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ten_goi_thau: Mapped[str] = mapped_column(String, index=True)
    gia_goi_thau: Mapped[str] = mapped_column(String)

    ho_so_du_thau: Mapped[List["HoSoDuThau"]] = relationship(back_populates="goi_thau")

class NhaThau(Coso):
    __tablename__ = "nha_thau"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ten_nha_thau: Mapped[str] = mapped_column(String, index=True)

    ho_so_du_thau: Mapped[List["HoSoDuThau"]] = relationship(back_populates="nha_thau")

class HoSoDuThau(Coso):
    __tablename__ = "ho_so_du_thau"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    goi_thau_id: Mapped[int] = mapped_column(ForeignKey("goi_thau.id"))
    nha_thau_id: Mapped[int] = mapped_column(ForeignKey("nha_thau.id"))
    duong_dan_file: Mapped[str] = mapped_column(String)
    noi_dung_text: Mapped[str] = mapped_column(Text, nullable=True)
    trang_thai: Mapped[str] = mapped_column(String)

    goi_thau: Mapped["GoiThau"] = relationship(back_populates="ho_so_du_thau")
    nha_thau: Mapped["NhaThau"] = relationship(back_populates="ho_so_du_thau")
    ket_qua_danh_gia: Mapped[List["KetQuaDanhGia"]] = relationship(back_populates="ho_so")

class KetQuaDanhGia(Coso):
    __tablename__ = "ket_qua_danh_gia"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ho_so_id: Mapped[int] = mapped_column(ForeignKey("ho_so_du_thau.id"))
    ket_luan: Mapped[str] = mapped_column(String)
    chi_tiet_json: Mapped[Dict[str, Any]] = mapped_column(JSON)
    thoi_gian: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ho_so: Mapped["HoSoDuThau"] = relationship(back_populates="ket_qua_danh_gia")

def lay_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

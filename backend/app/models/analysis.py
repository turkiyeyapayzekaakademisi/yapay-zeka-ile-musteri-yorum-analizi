"""
ADIMLAR:
    1. Base'den miras alarak ORM modelini tanımla
    2. Tablo adını belirle
    3. Kolonları ve tiplerini tanımla

NOT:
    ORM (Object-Relational Mapping): Python sınıfları ile
    veritabanı tablolarını eşleştirir. Böylece SQL yazmak
    yerine Python nesneleriyle çalışırız.

    Bu model, PostgreSQL'de şu tabloyu oluşturur:
        CREATE TABLE analyses (
            id          SERIAL PRIMARY KEY,
            comment_text TEXT NOT NULL,
            sentiment    VARCHAR(20) NOT NULL,
            confidence   FLOAT NOT NULL,
            explanation  TEXT,
            created_at   TIMESTAMPTZ DEFAULT now()
        );
"""

# =========================================================
# 1. Base'den miras alarak ORM modelini tanımla
# =========================================================
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from app.db.database import Base


class Analysis(Base):

    # =========================================================
    # 2. Tablo adını belirle
    # =========================================================
    __tablename__ = "analyses"

    # =========================================================
    # 3. Kolonları ve tiplerini tanımla
    # =========================================================
    id           = Column(Integer, primary_key=True, index=True)
    comment_text = Column(Text, nullable=False)           # Orijinal yorum metni
    sentiment    = Column(String(20), nullable=False)     # pozitif / negatif / nötr
    confidence   = Column(Float, nullable=False)          # 0.0 – 1.0 arası güven skoru
    explanation  = Column(Text, nullable=True)            # Gemini'nin kısa açıklaması
    created_at   = Column(                                # Otomatik zaman damgası
        DateTime(timezone=True),
        server_default=func.now()
    )

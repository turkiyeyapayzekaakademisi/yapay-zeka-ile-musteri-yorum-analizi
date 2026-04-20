"""
ADIMLAR:
    1. AnalysisRequest modelini tanımla  (istemciden gelen veri)
    2. AnalysisResponse modelini tanımla (istemciye dönen veri)
    3. AnalysisListResponse modelini tanımla (geçmiş listesi için)

NOT:
    Pydantic modelleri iki işe yarar:
        - Gelen veriyi otomatik doğrular (tip, zorunlu alan vb.)
        - Giden veriyi JSON'a dönüştürür
    FastAPI bu modelleri Swagger UI'da da otomatik belgeler.
"""

# =========================================================
# 1. AnalysisRequest — istemciden gelen veri
# =========================================================
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnalysisRequest(BaseModel):
    """
    POST /analysis/ endpoint'ine gönderilecek JSON gövdesi.
    Örnek: { "comment": "Ürün çok güzeldi!" }
    """
    comment: str


# =========================================================
# 2. AnalysisResponse — istemciye dönen tek analiz sonucu
# =========================================================
class AnalysisResponse(BaseModel):
    """
    Analiz tamamlandığında döndürülen JSON yanıtı.
    from_attributes=True: SQLAlchemy ORM nesnesini
    doğrudan bu modele dönüştürebilmemizi sağlar.
    """
    id: int
    comment_text: str
    sentiment: str        # "pozitif" | "negatif" | "nötr"
    confidence: float     # 0.0 – 1.0 arası güven skoru
    explanation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# 3. AnalysisListResponse — geçmiş listesi için sayfalanmış yanıt
# =========================================================
class AnalysisListResponse(BaseModel):
    """
    GET /analysis/history endpoint'inin döndürdüğü yanıt.
    total: Veritabanındaki toplam kayıt sayısı.
    analyses: Bu sayfada dönen kayıtlar.
    """
    total: int
    analyses: list[AnalysisResponse]

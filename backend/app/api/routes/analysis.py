"""
ADIMLAR:
    1. Router'ın oluşturulması
    2. POST /  →  Yeni yorum analizi yapılması ve sonuıçların kaydedilmesi  (async)
    3. GET  /history  →  Geçmiş analizleri sayfalanmış şekilde getirilmesi  (async)

NOT:
    Router, main.py'de /api/v1/analysis prefix'i ile kaydedilir.
    Yani bu dosyadaki "/" aslında "/api/v1/analysis/" olarak erişilir.

    Neden async def?
        Service fonksiyonları await gerektiriyor.
        FastAPI'de await kullanabilmek için endpoint async def olmalı.

    Dependency Injection:
        db: AsyncSession = Depends(get_db)
        FastAPI her istek için otomatik async veritabanı session'ı açar
        ve istek bitince kapatır.
"""

# =========================================================
# 1. Router'ı oluştur
# =========================================================
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.schemas import AnalysisRequest, AnalysisResponse, AnalysisListResponse
from app.services import analysis_service

router = APIRouter()


# =========================================================
# 2. POST /  →  Yeni yorum analizi yap ve kaydet
# =========================================================
@router.post("/", response_model=AnalysisResponse, status_code=201)
async def analyze(
    payload: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Akış:
        1. İstemci JSON body ile yorum gönderir
        2. await analysis_service.create_analysis() çağrılır
        3. Service Gemini'ye async istek atar
        4. Sonuç async olarak veritabanına kaydedilir
        5. Kaydedilen satır AnalysisResponse olarak döner
    """
    return await analysis_service.create_analysis(db, payload)


# =========================================================
# 3. GET /history  →  Geçmiş analizleri sayfalanmış getir
# =========================================================
@router.get("/history", response_model=AnalysisListResponse)
async def get_history(
    skip: int = Query(default=0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(default=50, ge=1, le=100, description="Döndürülecek maksimum kayıt sayısı"),
    db: AsyncSession = Depends(get_db),
):
    """
    Sayfalama (pagination) örneği:
        İlk 50 kayıt  →  GET /history?skip=0&limit=50
        Sonraki 50    →  GET /history?skip=50&limit=50
    """
    return await analysis_service.get_analyses(db, skip, limit)

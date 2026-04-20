"""
ADIMLAR:
    1. Yeni analiz oluştur: Gemini'yi çağır → sonucu DB'ye kaydet → döndür
    2. Geçmişi getir: DB'den sayfalanmış sıralı liste döndür

NOT:
    Bu service katmanı, route ile veritabanı/Gemini arasında köprü kurar.
    Route sadece HTTP ile ilgilenir, service iş mantığını yürütür.

    Neden async?
        Her iki işlem de (Gemini API çağrısı + DB sorgusu) ağ/disk I/O'dur.
        async/await ile bu bekleme sürelerinde event loop serbest kalır
        ve sunucu diğer istekleri işleyebilir.

    Akış:
        İstemci (Streamlit)
            ↓ HTTP POST
        routes/analysis.py            →  sadece HTTP katmanı
            ↓ await
        services/analysis_service.py  →  iş mantığı (burada)
            ↓ await              ↓ await
        gemini_service.py       database.py
        (Adım 1: AI analizi)    (Adım 2: kayıt/okuma)

    Async SQLAlchemy sorgu farkı:
        Sync  →  db.query(Model).filter(...).all()
        Async →  await db.execute(select(Model).where(...))
                 result.scalars().all()
"""

# =========================================================
# 1. Yeni analiz oluştur
# =========================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.analysis import Analysis
from app.schemas.schemas import AnalysisRequest, AnalysisResponse, AnalysisListResponse
from app.services.gemini_service import analyze_sentiment


async def create_analysis(db: AsyncSession, payload: AnalysisRequest) -> AnalysisResponse:
    """
    Amaç:
        Yorumu Gemini'ye async gönder, sonucu al ve veritabanına kaydet.

    Hata yönetimi:
        Gemini'den geçersiz yanıt gelirse 502 Bad Gateway döner.
        (Sorun bizde değil, upstream serviste — bu yüzden 502)
    """
    # Gemini API çağrısı (async — ağ I/O beklenir)
    try:
        gemini_result = await analyze_sentiment(payload.comment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API hatası: {str(e)}",
        )

    # Sonucu ORM nesnesi olarak hazırla
    analysis = Analysis(
        comment_text=payload.comment,
        sentiment=gemini_result["sentiment"],
        confidence=gemini_result["confidence"],
        explanation=gemini_result.get("explanation"),
    )

    # Veritabanına ekle ve kaydet (async)
    db.add(analysis)          # Session'a ekle (henüz SQL çalışmadı)
    await db.commit()         # INSERT sorgusunu çalıştır ve işlemi bitir
    await db.refresh(analysis) # DB'nin atadığı id ve created_at'ı nesneye yükle

    return AnalysisResponse.model_validate(analysis)


# =========================================================
# 2. Geçmişi getir
# =========================================================
async def get_analyses(db: AsyncSession, skip: int = 0, limit: int = 50) -> AnalysisListResponse:
    """
    Amaç:
        Tüm analizleri en yeniden en eskiye sıralı ve
        sayfalanmış biçimde async olarak döndür.

    Async sorgu farkı:
        Sync  →  db.query(Analysis).count()
        Async →  await db.execute(select(func.count()).select_from(Analysis))
                 result.scalar()
    """
    # Toplam kayıt sayısını al
    count_result = await db.execute(
        select(func.count()).select_from(Analysis)
    )
    total = count_result.scalar()

    # Sayfalanmış kayıtları al (en yeni en üstte)
    rows = await db.execute(
        select(Analysis)
        .order_by(Analysis.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    analyses = rows.scalars().all()

    return AnalysisListResponse(
        total=total,
        analyses=[AnalysisResponse.model_validate(a) for a in analyses],
    )

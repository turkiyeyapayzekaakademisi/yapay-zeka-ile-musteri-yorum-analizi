"""
ADIMLAR:
    1. Gerekli Kütüphanelerin import edilmesi
    2. Test için doğrudan DB bağlantısı kur
    3. Tabloları oluştur
    4. Test kaydı ekle
    5. Kaydı sorgula ve ekrana yazdır
    6. Test kaydını temizle

KURULUM:
    1. Sadece PostgreSQL'i başlatın (FastAPI ve Streamlit olmadan):
           docker compose up db -d
    2. Çalıştığını doğrulayın:
           docker compose ps
    3. Bu test dosyasını çalıştırın:
           python3 -m app.db.test_db

NOT:
    Bu dosya FastAPI olmadan, doğrudan SQLAlchemy üzerinden
    veritabanı bağlantısını ve ORM modelini test eder.
    Ayrıca doğrudan app.db.database içindeki yapılandırmayı kullanır.
"""

import asyncio
from sqlalchemy import select

from app.models.analysis import Analysis
# Ayrı engine oluşturmak yerine projenin kullandıklarını import ediyoruz
from app.db.database import AsyncSessionLocal, engine, init_db


# =========================================================
# 1. Tabloları oluştur
# =========================================================
async def create_tables():
    """
    Amaç:
        database.py'deki init_db fonksiyonunu kullanarak
        kendi engine'imizle tabloları oluşturmak.
    """
    await init_db(engine_override=engine)
    print(" Tablolar oluşturuldu (veya zaten vardı)")


# =========================================================
# 2. Test kaydı ekle
# =========================================================
async def insert_test_record() -> int:
    """
    Amaç:
        analyses tablosuna sahte bir analiz kaydı ekleyip
        veritabanına yazma işlemini test etmek.

    Returns:
        Eklenen kaydın id'si
    """
    async with AsyncSessionLocal() as db:
        analysis = Analysis(
            comment_text="Bu bir test yorumudur.",
            sentiment="pozitif",
            confidence=0.99,
            explanation="Bu kayıt test_db.py tarafından oluşturuldu.",
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

    print(f" Test kaydı eklendi  →  id={analysis.id}")
    return analysis.id


# =========================================================
# 3. Kaydı sorgula ve ekrana yazdır
# =========================================================
async def query_record(record_id: int):
    """
    Amaç:
        Az önce eklediğimiz kaydı id ile sorgulayıp
        veritabanından okuma işlemini test etmek.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Analysis).where(Analysis.id == record_id)
        )
        analysis = result.scalar_one_or_none()

    if analysis:
        print("\n📋 Sorgulanan kayıt:")
        print(f"   id           : {analysis.id}")
        print(f"   comment_text : {analysis.comment_text}")
        print(f"   sentiment    : {analysis.sentiment}")
        print(f"   confidence   : {analysis.confidence}")
        print(f"   explanation  : {analysis.explanation}")
        print(f"   created_at   : {analysis.created_at}")
    else:
        print(" Kayıt bulunamadı!")


# =========================================================
# 4. Test kaydını temizle
# =========================================================
async def delete_test_record(record_id: int):
    """
    Amaç:
        Test verisini veritabanından silip temizlemek.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Analysis).where(Analysis.id == record_id)
        )
        analysis = result.scalar_one_or_none()
        if analysis:
            await db.delete(analysis)
            await db.commit()

    print(f"\n  Test kaydı silindi  →  id={record_id}")


# =========================================================
# Tüm adımları sırayla çalıştır
# =========================================================
async def main():
    print("=" * 50)
    print("  Veritabanı Bağlantı Testi (Proje Config'i ile)")
    print("=" * 50)

    await create_tables()

    record_id = await insert_test_record()
    await query_record(record_id)
    await delete_test_record(record_id)

    print("\n Tüm testler başarılı! Veritabanı bağlantısı çalışıyor.")
    
    # İşlem bitince bağlantı havuzunu kapat
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

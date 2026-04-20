"""
ADIMLAR:
    1. Gerekli kütüphaneleri import et
    2. Lifespan tanımla  (uygulama açılırken/kapanırken ne yapılacak)
    3. FastAPI uygulamasını oluştur
    4. CORS middleware ekle  (Streamlit frontend'in erişmesi için)
    5. Router'ları uygulamaya kaydet
    6. Health check endpoint'i yaz

KURULUM:
    1. Virtual environment'ı aktif edin:
           - Windows : venv\Scripts\activate
           - Mac/Linux: source venv/bin/activate
    2. requirements.txt dosyasına şunları ekleyin:
           fastapi
           uvicorn[standard]
           google-genai
           python-dotenv
    3. Bağımlılıkları yükleyin:
           pip install -r requirements.txt
    4. Uygulamayı başlatmak için:
           uvicorn main:app --reload
    5. Swagger UI için tarayıcıda açın:
           http://localhost:8000/docs

NOT:
    Bu dosya uygulamanın giriş noktasıdır (entry point).
    Tüm router'lar buraya kayıt edilir.
    --reload flag'i sayesinde kod değişikliklerinde otomatik yeniden başlar.

    Adım 1 (Gemini) ve Adım 2 (PostgreSQL) hazır olduğu için
    bu dosyada her ikisini de direkt entegre edebiliyoruz.

    Neden lifespan?
        Async uygulamalarda Base.metadata.create_all() direkt çağrılamaz.
        lifespan context manager ile uygulama başlarken async olarak
        tabloları oluşturabiliyoruz. Bu modern FastAPI yaklaşımıdır.
"""

# =========================================================
# 1. Gerekli kütüphaneleri import et
# =========================================================
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis
from app.core.config import settings
from app.db.database import engine, Base, init_db


# =========================================================
# 2. Lifespan tanımla
# =========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Amaç:
        Uygulama başlarken veritabanı tablolarını async olarak oluşturmak.

    Nasıl çalışır?
        yield öncesi  →  startup (uygulama başlarken çalışır)
        yield sonrası →  shutdown (uygulama kapanırken çalışır)

    engine.begin(): async bağlantı açar ve işlem bitince otomatik kapatır.
    conn.run_sync(): async engine üzerinde sync bir fonksiyon çalıştırmak için.
    """
    await init_db()  # Veritabanı bağlantısını başlat ve tabloları oluştur
    yield
    # Uygulama kapanırken engine bağlantılarını temizle
    await engine.dispose()


# =========================================================
# 3. FastAPI uygulamasını oluştur
# =========================================================
# title ve description Swagger UI'da (/docs) görünür
app = FastAPI(
    title="Yorum Analizi API",
    description="Gemini API kullanarak müşteri yorumlarını analiz eden REST API",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# 4. CORS middleware ekle
# =========================================================
# CORS (Cross-Origin Resource Sharing): Farklı adresten gelen
# isteklere izin vermek için gerekli. Streamlit farklı bir portta
# (8501) çalıştığı için bu ayar olmadan istekler engellenir.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# 5. Router'ları uygulamaya kaydet
# =========================================================
# prefix sayesinde tüm analiz endpoint'leri /api/v1/analysis/ altında toplanır
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])


# =========================================================
# 6. Health check endpoint'i yaz
# =========================================================
@app.get("/", tags=["Health"])
async def health_check():
    """
    Amaç:
        API'nin ayakta olduğunu doğrulamak.
        Docker Compose bu endpoint'i izleyebilir.
    """
    return {"status": "ok", "message": "Yorum Analizi API çalışıyor"}

"""
ADIMLAR:
    1. Gerekli Kütüphanelerin import edilmesi
    2. Async SQLAlchemy engine'i oluştur  (veritabanı bağlantısı)
    3. Async session factory'yi tanımla   (her istek için ayrı oturum)
    4. Base class'ı oluştur               (ORM modelleri bu sınıftan türer)
    5. get_db dependency'sini yaz         (FastAPI bunu her endpoint'e enjekte eder)

KURULUM:
    2. requirements.txt dosyasına şunları ekleyin:
           sqlalchemy[asyncio]
           asyncpg
    3. Bağımlılıkları yükleyin:
           pip install -r requirements.txt
    4. backend/.env dosyasına bağlantı string'ini yazın:
           DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/yorum_analizi

TEST:
    Bu adımı bitirince bağlantıyı test etmek için:
        docker compose up db -d    (sadece PostgreSQL'i başlat)
        python test_db.py          (bağlantı + CRUD testi)

"""
# =========================================================
# 1. Gerekli Kütüphanelerin import edilmesi
# =========================================================

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# =========================================================
# 2. Async SQLAlchemy engine'i oluştur
# =========================================================
# Async engine: bağlantı havuzunu async olarak yönetir
engine = create_async_engine(
    settings.async_database_url,
    pool_size=5,      # Havuzda sürekli açık tutulan bağlantı sayısı
    max_overflow=10,  # Havuz dolunca açılabilecek ekstra bağlantı sayısı
    echo=False,       # True yapılırsa çalışan SQL sorguları terminale yazdırılır
)


# =========================================================
# 2. Async session factory'yi tanımla
# =========================================================
# async_sessionmaker: her çağrıda yeni bir AsyncSession üretir
# expire_on_commit=False: commit sonrası nesne alanlarına erişmeye devam edebiliriz
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


# =========================================================
# 3. Base class'ı oluştur
# =========================================================
# Tüm ORM modelleri (örn: Analysis) bu sınıftan miras alır
Base = declarative_base()


# =========================================================
# 4. get_db dependency'sini yaz
# =========================================================
async def init_db(engine_override=None):
    """
    Veritabanında tabloları oluşturur. (Eğer yoksa)
    Uygulama başlarken (startup event) çağrılması önerilir.
    """
    use_engine = engine_override or engine
    async with use_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """
    Amaç:
        FastAPI endpoint'lerine async veritabanı session'ı sağlamak.

    Nasıl çalışır?
        async with: session açılır, endpoint'e verilir, blok bitince
        otomatik kapatılır — hata olsa bile. try/finally gerekmez.

    Kullanım (routes/analysis.py içinde):
        async def analyze(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session

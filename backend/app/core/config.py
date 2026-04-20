"""
Adımlar:
    1. Gerekli kütüphaneleri import edin.
    2. Settings sınıfını oluşturun ve BaseSettings'ten türetin.
    3. DATABASE_URL ve GEMINI_API_KEY gibi gerekli alanları tanımlayın.
    4. async_database_url özelliğini ekleyin ve DATABASE_URL'yi asyncpg formatına dönüştürün.
    5. settings örneğini oluşturun.

Kurulum:
    1. pydantic-settings kütüphanesini requirements.txt dosyasına ekleyin:
        pydantic-settings
    2. Bağımlılıkları yükleyin:
        pip install -r requirements.txt
    3. .env dosyasına gerekli ortam değişkenlerini ekleyin:
        DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/yorum_analizi
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:8501,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

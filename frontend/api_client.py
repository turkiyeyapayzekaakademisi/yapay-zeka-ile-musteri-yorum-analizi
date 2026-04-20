"""
ADIMLAR:
    1. API base URL'ini ortam değişkeninden oku
    2. Yorum analizi isteği at  →  POST /analysis/
    3. Analiz geçmişini getir   →  GET  /analysis/history

KURULUM:
    1. requirements.txt dosyasına şunu ekleyin:
           streamlit
           requests
           python-dotenv
    2. Bağımlılıkları yükleyin:
           pip install -r requirements.txt
    3. frontend/.env dosyasına backend adresini yazın:
           Lokal geliştirme : API_BASE_URL=http://localhost:8000/api/v1
           Docker Compose   : API_BASE_URL=http://backend:8000/api/v1

NOT:
    Bu dosya Streamlit ile FastAPI arasındaki HTTP köprüsüdür.
    Streamlit sayfaları doğrudan bu fonksiyonları çağırır,
    HTTP detaylarıyla uğraşmak zorunda kalmaz.
"""

# =========================================================
# 1. API base URL'ini ortam değişkeninden oku
# =========================================================
import requests
import os

# Docker Compose içinde çalışırken servis adı "backend" olur.
# Lokal geliştirmede localhost kullanılır.
# Varsayılan: lokal geliştirme için localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


# =========================================================
# 2. Yorum analizi isteği at  →  POST /analysis/
# =========================================================
def analyze_comment(comment: str) -> dict:
    """
    Amaç:
        Kullanıcının yazdığı yorumu FastAPI'ye gönderip
        Gemini analiz sonucunu almak.

    Dönen dict örneği:
        {
            "id": 1,
            "comment_text": "Harika ürün!",
            "sentiment": "pozitif",
            "confidence": 0.97,
            "explanation": "...",
            "created_at": "2024-01-01T12:00:00"
        }
    """
    response = requests.post(
        f"{API_BASE_URL}/analysis/",
        json={"comment": comment},
        timeout=30,  # Gemini bazen yavaş yanıt verebilir
    )
    response.raise_for_status()  # HTTP 4xx/5xx → exception fırlatır
    return response.json()


# =========================================================
# 3. Analiz geçmişini getir  →  GET /analysis/history
# =========================================================
def get_history(skip: int = 0, limit: int = 50) -> dict:
    """
    Amaç:
        Veritabanındaki geçmiş analizleri sayfalanmış olarak almak.

    Dönen dict örneği:
        {
            "total": 42,
            "analyses": [ {...}, {...}, ... ]
        }
    """
    response = requests.get(
        f"{API_BASE_URL}/analysis/history",
        params={"skip": skip, "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()

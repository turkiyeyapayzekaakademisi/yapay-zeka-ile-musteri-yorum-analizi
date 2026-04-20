"""
ADIMLAR:
    1. Gerekli kütüphaneyi import et
    2. API key ile Gemini client oluştur
    3. İlk basit mesajlaşmayı yap  (bağlantı testi)
    4. Duygu analizi için prompt hazırla
    5. Bir metin üzerinde async duygu analizi yap
    6. Sonucu JSON olarak parse et ve döndür

KURULUM:
    1. Virtual environment oluşturun:
           python -m venv venv
    2. Virtual environment'ı aktif edin:
           - Windows : venv\Scripts\activate
           - Mac/Linux: source venv/bin/activate
    3. requirements.txt dosyasına şu satırı ekleyin:
           google-genai
           python-dotenv
    4. Bağımlılıkları yükleyin:
           pip install -r requirements.txt
    5. backend/.env dosyasına API key'inizi yazın:
           GEMINI_API_KEY=sizin_api_keyiniz
    6. Ücretsiz API key almak için:
           https://aistudio.google.com/app/apikey

NOT:
    Bu dosyayı doğrudan çalıştırarak Gemini bağlantısını test edebilirsiniz:
        python gemini_service.py "Ürün harika, çok memnun kaldım!"
        python gemini_service.py          (yorum için prompt açar)

    Neden async?
        FastAPI async bir framework'tür. Gemini API çağrısı ağ üzerinden
        yapılan bir I/O işlemidir. async/await sayesinde bu bekleme
        sırasında sunucu diğer istekleri işleyebilir — performans artar.
"""

# =========================================================
# 1. Gerekli kütüphaneyi import et
# =========================================================
import asyncio
import json
import os
import sys

from google import genai
from dotenv import load_dotenv

# .env dosyasını yükle — hem standalone hem app içi çalışır
load_dotenv()


# =========================================================
# 2. API key ile Gemini client oluştur
# =========================================================
# API key'i ortam değişkeninden okuyoruz (.env dosyasından gelir)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY bulunamadı. .env dosyanı kontrol et.")

# Kullanacağımız model adı
MODEL_NAME = "gemini-2.5-flash"

# Gemini istemcisini oluşturuyoruz
# client.aio  →  async çağrılar için kullanılır
# client.models  →  sync çağrılar için kullanılır
client = genai.Client(api_key=GEMINI_API_KEY)


# =========================================================
# 3. İlk basit mesajlaşmayı yap
# =========================================================
async def first_message():
    """
    Amaç:
        Gemini API bağlantısının çalıştığını görmek için
        ilk basit mesajı göndermek.

    Bu adım karmaşık bir prompt veya JSON gerektirmiyor.
    Sadece "API key doğru mu, bağlantı kuruluyor mu?" sorusunu yanıtlar.
    """
    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents="Merhaba Gemini. Bana kısa bir selam ver."
    )

    print("=== İlk Gemini API Çağrısı ===")
    print(response.text)
    print()


# =========================================================
# 4. Duygu analizi için prompt hazırla
# =========================================================
def build_sentiment_prompt(comment: str) -> str:
    """
    Amaç:
        Modele, verilen yorumun duygu analizini yapması için
        açık ve yapılandırılmış bir prompt hazırlamak.

    Neden JSON istiyoruz?
        FastAPI endpoint'imiz bu sonucu veritabanına kaydedecek.
        JSON formatı sayesinde her alanı ayrı ayrı işleyebiliriz.
    """
    prompt = f"""
Sen bir duygu analizi uzmanısın. Sana verilen müşteri yorumunu analiz et ve
aşağıdaki JSON formatında yanıt ver. JSON dışında hiçbir şey yazma.

Yorum: "{comment}"

Yanıt formatı:
{{
  "sentiment": "pozitif" | "negatif" | "nötr",
  "confidence": 0.0 ile 1.0 arasında bir sayı,
  "explanation": "Kısa Türkçe açıklama (maksimum 2 cümle)"
}}
"""
    return prompt.strip()


# =========================================================
# 5. Bir metin üzerinde async duygu analizi yap
# =========================================================
async def analyze_sentiment(comment: str) -> dict:
    """
    Amaç:
        Verilen yorumu Gemini'ye async olarak gönderip sonucu almak.

    Args:
        comment: Analiz edilecek müşteri yorum metni.

    Returns:
        sentiment, confidence, explanation anahtarlarını içeren dict.

    Raises:
        ValueError: Gemini geçerli JSON döndürmezse.
    """
    prompt = build_sentiment_prompt(comment)

    # client.aio: async Gemini çağrısı — await ile beklenir
    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    raw_text = response.text.strip()

    # =========================================================
    # 6. Sonucu JSON olarak parse et ve döndür
    # =========================================================
    # Gemini bazen cevabı ```json ... ``` bloğu içine sarar — temizliyoruz
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini geçersiz JSON döndürdü: {raw_text}") from e

    # Beklenen alanların hepsinin geldiğini doğruluyoruz
    required_keys = {"sentiment", "confidence", "explanation"}
    if not required_keys.issubset(result.keys()):
        raise ValueError(f"Gemini yanıtında eksik alanlar var: {result}")

    return result


# =========================================================
# Standalone test: dosyayı doğrudan çalıştırınca devreye girer
# =========================================================
async def _main():
    # Adım 3: önce basit bağlantı testi
    await first_message()

    # Adım 5-6: duygu analizi testi
    if len(sys.argv) > 1:
        comment = " ".join(sys.argv[1:])
    else:
        comment = input("Analiz edilecek yorum: ").strip()
        if not comment:
            print("Hata: Yorum boş olamaz.")
            sys.exit(1)

    print(f"\nYorum: {comment}")
    print("Gemini analiz ediyor...\n")

    result = await analyze_sentiment(comment)

    print(f"Duygu     : {result['sentiment']}")
    print(f"Güven     : %{int(result['confidence'] * 100)}")
    print(f"Açıklama  : {result['explanation']}")


if __name__ == "__main__":
    # async fonksiyonu çalıştırmak için asyncio.run() kullanıyoruz
    asyncio.run(_main())

# Yapay Zeka ile Müşteri Yorum Analizi

Gemini API, FastAPI, PostgreSQL, Streamlit, Docker ve Railway kullanarak
uçtan uca bir duygu analizi uygulaması.

---

## Proje Akışı

```
Gemini API → PostgreSQL → FastAPI → Streamlit → Docker → Deploy
``` 

Her adım bir öncekinin üzerine inşa edilir. Adımları sırayla takip edin.

---
## Adım 1 — Gemini ile Yorum Analizi ve İyileştirme Önerileri Geliştirme
								

**Ne yapacağız?**
Google'ın Gemini yapay zeka modeline bağlanıp müşteri yorumlarını
duygu analizine göre sınıflandıracağız: **pozitif / negatif / nötr**

**Dosya:** `backend/app/services/gemini_service.py`

**Ne öğreneceğiz?**
- `google-genai` SDK kurulumu ve virtual environment kullanımı
- `genai.Client` ile API bağlantısı kurma
- Prompt mühendisliği (modele ne söylemek gerekir?)
- JSON formatında yapılandırılmış yanıt alma
- Async Gemini çağrısı (`client.aio.models.generate_content`)

**Test:**
```bash
cd backend
python app/services/gemini_service.py "Ürün harika, çok memnun kaldım!"
```

---

## Adım 2 — PostgreSQL ile Analiz Sonuçlarını Kaydetme

**Ne yapacağız?**
Her analiz sonucunu veritabanına kaydedeceğiz. Böylece geçmiş
analizlere erişebilecek ve istatistik gösterebileceğiz.

**Dosyalar:**
- `backend/app/core/config.py` — ortam değişkenlerini oku (.env)
- `backend/app/db/database.py` — async engine, session, get_db
- `backend/app/models/analysis.py` — analyses tablosu ORM modeli

**Ne öğreneceğiz?**
- Pydantic Settings ile `.env` dosyasından config okuma
- SQLAlchemy async engine kurulumu (`asyncpg` sürücüsü)
- ORM model tanımlama (Python sınıfı → veritabanı tablosu)
- Async session yönetimi ve `get_db` dependency pattern'i

**Bağlantı string formatı:**
```
postgresql+asyncpg://kullanici:sifre@host:5432/veritabani
```

**Test:**
```bash
# Sadece PostgreSQL container'ını başlat
docker compose up db -d

# Bağlantı + tablo oluşturma + CRUD testini çalıştır
cd backend
python test_db.py
```

---

## Adım 3 — FastAPI ile Yorum Analizi API'si Geliştirme

**Ne yapacağız?**
Gemini (Adım 1) ve PostgreSQL (Adım 2) servislerini bir REST API'ye
bağlayacağız. İki endpoint yazacağız:
- `POST /api/v1/analysis/` → yorum gönder, analiz sonucu al ve kaydet
- `GET  /api/v1/analysis/history` → geçmiş analizleri listele

**Dosyalar:**
- `backend/main.py` — uygulama giriş noktası, CORS, lifespan
- `backend/app/schemas/schemas.py` — request/response modelleri (Pydantic)
- `backend/app/api/routes/analysis.py` — endpoint tanımları
- `backend/app/services/analysis_service.py` — Gemini + DB iş mantığı

**Ne öğreneceğiz?**
- FastAPI kurulumu ve async uygulama oluşturma
- Pydantic ile otomatik veri doğrulama
- CORS middleware (Streamlit'in API'ye erişebilmesi için)
- `lifespan` ile async tablo oluşturma
- Dependency Injection ile `get_db` kullanımı
- Swagger UI ile otomatik dokümantasyon (`/docs`)

**Test:**
```bash
cd backend
uvicorn main:app --reload
# Tarayıcıda: http://localhost:8000/docs
```

---

## Adım 4 — Streamlit ile Kullanıcı Arayüzü Geliştirme

**Ne yapacağız?**
Kullanıcıların yorum yazabileceği ve analiz sonuçlarını görebileceği
bir web arayüzü oluşturacağız.

**Dosyalar:**
- `frontend/app.py` — tek sayfa: ayarlar + dashboard + form + geçmiş
- `frontend/api_client.py` — FastAPI'ye HTTP istekleri atan client

**Ne öğreneceğiz?**
- Streamlit kurulumu ve `streamlit run` komutu
- `ssion_state` ile sayfa yenilenince veriyi koruma
- `requests` kütüphanesi ile FastAPI'ye istek atma

**Test:**
```bash
cd frontend
streamlit run app.py
# Tarayıcıda: http://localhost:8501
```

---

## Adım 5 — Docker ile Paketlenme

**Ne yapacağız?**
Tüm servisleri (PostgreSQL, FastAPI, Streamlit) Docker container'larına
alacağız. Tek komutla hepsini ayağa kaldıracağız.

**Dosyalar:**
- `backend/Dockerfile` — FastAPI image'ı
- `frontend/Dockerfile` — Streamlit image'ı
- `docker-compose.yml` — 3 servisi birlikte yönetir

**Ne öğreneceğiz?**
- `Dockerfile` yazımı (base image, WORKDIR, COPY, RUN, CMD)
- Docker layer cache mantığı (neden önce requirements.txt kopyalanır?)
- `docker-compose.yml` ile çok servisli yapı kurma
- Servisler arası iletişim (servis adı = hostname)
- `healthcheck` ve `depends_on` ile başlatma sırası belirleme
- Named volume ile veri kalıcılığı

**Komutlar:**
```bash
# Tüm servisleri başlat
docker compose up --build

# Arka planda çalıştır
docker compose up -d --build

# Durdur (veriyi koru)
docker compose down

# Durdur + veriyi sil
docker compose down -v
```

**Çalışan servisler:**

| Servis | URL |
|--------|-----|
| Streamlit | http://localhost:8501 |
| FastAPI Swagger | http://localhost:8000/docs |
| PostgreSQL | localhost:5433 |

---

## Adım 6 — Deploy (Railway)

**Ne yapacağız?**
Uygulamayı Railway üzerinde deploy edeceğiz. Backend (FastAPI), 
frontend (Streamlit) ve PostgreSQL servislerini ayrı ayrı ayağa 
kaldırıp internet üzerinden erişilebilir hale getireceğiz.

**Ne öğreneceğiz?**
- Railway'de monorepo yapısıyla çoklu servis deploy etme
- Root Directory ile farklı klasörleri ayrı servislere bağlama
- Managed PostgreSQL provisioning ve servisler arası reference kullanımı
- Environment variables ve Railway reference syntax
- Dockerfile'ı platform-agnostic hale getirme ($PORT kullanımı)

**Ön koşullar:**
- GitHub hesabı ve projeyi barındıran bir repo
- Railway hesabı (railway.app üzerinden GitHub ile giriş)
- `backend/` ve `frontend/` klasörlerinin her birinde kendi `Dockerfile`'ı

**Adımlar:**

### 1. Railway'de proje oluşturun
- [railway.app](https://railway.app) → GitHub ile giriş
- **New Project → Deploy from GitHub repo** → `yorum-analizi` repo'sunu seçin

### 2. Backend servisini yapılandırın
İlk oluşan servise tıklayın → **Settings**:
- **Source → Add Root Directory:** `backend`
- **Service Name:** `backend`
- **Networking → Generate Domain** (public URL için)

**Variables** sekmesi → **Raw Editor** → `backend/.env` içeriğini 
yapıştırın. `DATABASE_URL` değişkenini aşağıdaki adımda güncelleyeceksiniz.

### 3. PostgreSQL servisi ekleyin
Canvas'ta **+ Add → Database → Add PostgreSQL**.

Provisioning tamamlandıktan sonra backend'in Variables bölümüne dönün ve 
`DATABASE_URL` değerini şöyle güncelleyin:
​```
DATABASE_URL=${{Postgres.DATABASE_URL}}
​```

**Not:** `asyncpg` driver kullanıyorsanız, kodunuzda URL'yi okurken 
`postgresql://` prefix'ini `postgresql+asyncpg://` ile değiştirmeniz 
gerekir. `main.py`'da:
​```python
import os
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
​```

### 4. Backend Dockerfile'ını Railway'e uyarlayın
`backend/Dockerfile` içindeki CMD satırı `$PORT` env variable'ını 
kullanmalıdır:
​```dockerfile
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
​```

### 5. Frontend servisini ekleyin
Canvas'ta **+ Add → GitHub Repo** → aynı repo'yu tekrar seçin.

Yeni servise tıklayın → **Settings**:
- **Add Root Directory:** `frontend`
- **Service Name:** `frontend`
- **Networking → Generate Domain**

### 6. Frontend environment variables
**Variables → Raw Editor** → `frontend/.env` içeriğini yapıştırın.

`API_BASE_URL` değişkenini backend servisine işaret edecek şekilde 
güncelleyin:
​```
API_BASE_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}/api/v1
​```

### 7. Frontend Dockerfile'ını Railway'e uyarlayın
`frontend/Dockerfile` içindeki CMD satırı Streamlit'i dinamik port ve 
tüm network interface'leri üzerinden başlatmalıdır:
​```dockerfile
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
​```

### 8. Deploy'u doğrulayın
Her iki servis de "Active" durumuna geldiğinde:
- **Frontend:** `https://<frontend-domain>.up.railway.app` → Streamlit UI
- **Backend:** `https://<backend-domain>.up.railway.app/docs` → FastAPI Swagger

**Otomatik deploy:** Main branch'e her push, bağlı servisleri otomatik 
olarak yeniden build eder.

**Dikkat edilmesi gerekenler:**
- Railway `docker-compose.yml` dosyasını kullanmaz; her servis kendi 
  Dockerfile'ı üzerinden ayrı container olarak çalışır
- `.env` dosyaları git'e pushlanmaz; secrets tamamen Railway 
  Variables üzerinden yönetilir
- Railway free tier kaldırılmıştır

---

## Proje Yapısı

```
yorum-analizi/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── analysis.py        # Adım 3: POST /analysis, GET /history
│   │   ├── core/
│   │   │   └── config.py          # Adım 2: .env okuma
│   │   ├── db/
│   │   │   └── database.py        # Adım 2: Async engine, get_db
│   │   ├── models/
│   │   │   └── analysis.py        # Adım 2: analyses tablosu
│   │   ├── schemas/
│   │   │   └── schemas.py         # Adım 3: Pydantic modeller
│   │   └── services/
│   │       ├── gemini_service.py  # Adım 1: Gemini API
│   │       └── analysis_service.py # Adım 3: Gemini + DB iş mantığı
│   ├── main.py                    # Adım 3: FastAPI giriş noktası
│   ├── requirements.txt
│   ├── Dockerfile                 # Adım 5: Backend image
│   └── .env.example
├── frontend/
│   ├── app.py                     # Adım 4: Streamlit tek sayfa
│   ├── api_client.py              # Adım 4: HTTP client
│   ├── requirements.txt
│   ├── Dockerfile                 # Adım 5: Frontend image
│   └── .env.example
└── docker-compose.yml             # Adım 5: Tüm servisler
```

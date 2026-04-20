# =============================================================
# ADIMLAR:
#   1. Base image seç        (hangi Python sürümü?)
#   2. Çalışma dizinini ayarla
#   3. Bağımlılıkları yükle  (önce bu katman — cache'den faydalanır)
#   4. Uygulama kodunu kopyala
#   5. Port'u dışa aç
#   6. Başlatma komutunu tanımla
#
# NOT:
#   Neden önce requirements.txt kopyalanıyor, sonra kodlar?
#   Docker katman (layer) cache'i sayesinde requirements.txt
#   değişmediği sürece pip install tekrar çalışmaz — build hızlanır.
#   Kod değiştiğinde sadece son COPY katmanı yeniden çalışır.
# =============================================================


# =========================================================
# 1. Base image seç
# =========================================================
# python:3.11-slim: tam Python 3.11 imajının hafif versiyonu.
# Gereksiz sistem araçları içermez, boyutu küçük tutar.
FROM python:3.11-slim


# =========================================================
# 2. Çalışma dizinini ayarla
# =========================================================
# Sonraki tüm komutlar bu dizinde çalışır.
# Container içinde /app dizini oluşturulur.
WORKDIR /app


# =========================================================
# 3. Bağımlılıkları yükle
# =========================================================
# Önce sadece requirements.txt kopyalanır.
COPY requirements.txt .

# --no-cache-dir: pip'in indirdiği paket dosyalarını saklamasın.
# İmaj boyutunu küçültür.
RUN pip install --no-cache-dir -r requirements.txt


# =========================================================
# 4. Uygulama kodunu kopyala
# =========================================================
# requirements.txt değişmediği sürece üstteki pip install
# cache'den gelir; sadece bu katman yeniden çalışır.
COPY . .


# =========================================================
# 5. Port'u dışa aç
# =========================================================
# Bu sadece belgeleme amaçlı — gerçek port mapping
# docker-compose.yml içindeki ports tanımıyla yapılır.
EXPOSE 8000


# =========================================================
# 6. Başlatma komutunu tanımla
# =========================================================
# --host 0.0.0.0: Container dışından erişilebilir olması için.
# Varsayılan 127.0.0.1 sadece container içinden erişilebilirdi.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================
# ADIMLAR:
#   1. Base image seç
#   2. Çalışma dizinini ayarla
#   3. Bağımlılıkları yükle
#   4. Uygulama kodunu kopyala
#   5. Port'u dışa aç
#   6. Başlatma komutunu tanımla
#
# NOT:
#   Backend Dockerfile ile yapı aynı — sadece başlatma komutu farklı.
#   Backend: uvicorn  →  Frontend: streamlit
# =============================================================


# =========================================================
# 1. Base image seç
# =========================================================
FROM python:3.11-slim


# =========================================================
# 2. Çalışma dizinini ayarla
# =========================================================
WORKDIR /app


# =========================================================
# 3. Bağımlılıkları yükle
# =========================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# =========================================================
# 4. Uygulama kodunu kopyala
# =========================================================
COPY . .


# =========================================================
# 5. Port'u dışa aç
# =========================================================
# Streamlit varsayılan olarak 8501 portunu kullanır.
EXPOSE 8501


# =========================================================
# 6. Başlatma komutunu tanımla
# =========================================================
# --server.address=0.0.0.0 : Container dışından erişilebilir olması için.
# --server.headless=true    : Container ortamında tarayıcı açmaya çalışmasın.
# --browser.gatherUsageStats=false : Telemetri göndermesin.
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--browser.gatherUsageStats=false", \
     "--server.headless=true"]
